import socket
import concurrent.futures
import urllib.request
import urllib.error
import ssl
from app.scanner.ports import PORTS, HTTP_CHECKS, HTTP_SECURITY_HEADERS

def scan_port(target: str, port: int, info: dict) -> dict | None:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((target, port))
        if result == 0:
            banner = ""
            try:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                banner = sock.recv(256).decode(errors="ignore").split("\n")[0].strip()
            except:
                pass
            sock.close()
            return {
                "port": port,
                "service": info["service"],
                "risk": info["risk"],
                "context": info["context"],
                "banner": banner if banner else None,
                "type": "port"
            }
        sock.close()
    except:
        pass
    return None

def check_http(target: str, port: int, check: dict) -> dict | None:
    protocols = ["https", "http"]
    for proto in protocols:
        url = f"{proto}://{target}:{port}{check['path']}"
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={"User-Agent": "Scanner-Pro/1.0"})
            response = urllib.request.urlopen(req, timeout=2, context=ctx if proto == "https" else None)
            if response.status < 400:
                return {
                    "port": port,
                    "service": check["label"],
                    "risk": check["risk"],
                    "context": f"Endpoint {check['path']} acessível sem autenticação em {proto.upper()}.",
                    "banner": f"HTTP {response.status}",
                    "type": "http"
                }
        except urllib.error.HTTPError as e:
            if e.code not in [401, 403, 404]:
                return {
                    "port": port,
                    "service": check["label"],
                    "risk": "ATTENTION",
                    "context": f"Endpoint {check['path']} retornou HTTP {e.code}.",
                    "banner": f"HTTP {e.code}",
                    "type": "http"
                }
        except:
            pass
    return None

def check_security_headers(target: str, port: int) -> list:
    missing = []
    protocols = ["https", "http"]
    for proto in protocols:
        url = f"{proto}://{target}:{port}/"
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={"User-Agent": "Scanner-Pro/1.0"})
            response = urllib.request.urlopen(req, timeout=2, context=ctx if proto == "https" else None)
            headers = {k.lower(): v for k, v in response.headers.items()}
            for h in HTTP_SECURITY_HEADERS:
                if h.lower() not in headers:
                    missing.append({
                        "port": port,
                        "service": f"Header ausente: {h}",
                        "risk": "ATTENTION",
                        "context": f"O header de segurança '{h}' não está configurado.",
                        "banner": None,
                        "type": "header"
                    })
            break
        except:
            continue
    return missing

def run_scan(target: str) -> dict:
    results = []
    web_ports = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {
            executor.submit(scan_port, target, port, info): port
            for port, info in PORTS.items()
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                if result["service"] in ["HTTP", "HTTPS", "HTTP-Alt", "HTTPS-Alt", "HTTP-Dev",
                                          "Node/React", "Flask/Dev", "Vite/Dev", "Angular/Dev"]:
                    web_ports.append(result["port"])

    # HTTP checks nos web ports encontrados
    if web_ports:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            http_futures = []
            for port in web_ports:
                for check in HTTP_CHECKS:
                    http_futures.append(executor.submit(check_http, target, port, check))
                http_futures.append(executor.submit(check_security_headers, target, port))

            for future in concurrent.futures.as_completed(http_futures):
                result = future.result()
                if result:
                    if isinstance(result, list):
                        results.extend(result)
                    else:
                        results.append(result)

    # Ordena por risco
    risk_order = {"CRITICAL": 0, "ATTENTION": 1, "COMMON": 2}
    results.sort(key=lambda x: risk_order.get(x["risk"], 3))

    return {
        "target": target,
        "total_open_ports": len([r for r in results if r["type"] == "port"]),
        "total_findings": len(results),
        "results": results
    }
