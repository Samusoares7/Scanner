import socket
import concurrent.futures
import urllib.request
import urllib.error
import urllib.parse
import ssl
import hashlib
import uuid
from app.scanner.ports import PORTS, HTTP_CHECKS, HTTP_SECURITY_HEADERS

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def make_request(url: str, timeout: int = 3) -> dict | None:
    """Faz requisição HTTP/HTTPS e retorna dados da resposta."""
    try:
        ctx = get_ssl_context() if url.startswith("https") else None
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; SecurityScanner/1.0)",
                "Accept": "*/*"
            }
        )
        response = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        content = response.read(4096)
        return {
            "status": response.status,
            "content_length": len(content),
            "content_hash": hashlib.md5(content).hexdigest(),
            "content": content.decode(errors="ignore"),
            "headers": dict(response.headers),
            "protocol": "https" if url.startswith("https") else "http",
            "blocked": False
        }
    except urllib.error.HTTPError as e:
        content = b""
        try:
            content = e.read(4096)
        except:
            pass
        return {
            "status": e.code,
            "content_length": len(content),
            "content_hash": hashlib.md5(content).hexdigest(),
            "content": content.decode(errors="ignore"),
            "headers": dict(e.headers) if e.headers else {},
            "protocol": "https" if url.startswith("https") else "http",
            "blocked": False
        }
    except Exception as e:
        error_str = str(e).lower()
        blocked = any(k in error_str for k in ["ssl", "certificate", "timeout", "forbidden", "reset"])
        return {
            "status": 0,
            "content_length": 0,
            "content_hash": "",
            "content": "",
            "headers": {},
            "protocol": "https" if url.startswith("https") else "http",
            "blocked": blocked
        }

def get_baseline(target: str, port: int) -> dict | None:
    """
    Faz requisição para path aleatório inexistente.
    Usado para detectar soft 404 — servidor que retorna 200 para qualquer path.
    """
    random_path = f"/baseline-check-{uuid.uuid4().hex[:12]}"
    for proto in ["https", "http"]:
        url = f"{proto}://{target}:{port}{random_path}"
        result = make_request(url)
        if result and result["status"] != 0:
            return result
    return None

def is_false_positive(response: dict, baseline: dict | None) -> bool:
    """
    Verifica se o finding é falso positivo comparando com baseline.
    Retorna True se for falso positivo.
    """
    if baseline is None:
        return False

    # Se baseline também retornou 200, é soft 404
    if baseline["status"] == 200:
        # Compara hash do conteúdo — se igual, é falso positivo
        if response["content_hash"] == baseline["content_hash"]:
            return True
        # Compara tamanho — se muito próximo (±10%), provavelmente falso positivo
        if baseline["content_length"] > 0:
            ratio = abs(response["content_length"] - baseline["content_length"]) / baseline["content_length"]
            if ratio < 0.1:
                return True

    return False

def detect_waf(target: str, port: int) -> dict:
    """
    Detecta presença de WAF/CDN tentando HTTPS primeiro.
    Retorna informações sobre o ambiente detectado.
    """
    waf_info = {
        "detected": False,
        "type": None,
        "https_blocked": False,
        "active_protocol": "http"
    }

    # Testa HTTPS
    https_url = f"https://{target}:{port}/"
    https_result = make_request(https_url, timeout=3)

    if https_result and not https_result["blocked"] and https_result["status"] != 0:
        waf_info["active_protocol"] = "https"
        # Verifica headers de WAF conhecidos
        headers = {k.lower(): v for k, v in https_result["headers"].items()}
        if "cf-ray" in headers or "cf-cache-status" in headers:
            waf_info["detected"] = True
            waf_info["type"] = "Cloudflare"
        elif "x-sucuri-id" in headers:
            waf_info["detected"] = True
            waf_info["type"] = "Sucuri"
        elif "x-waf" in headers or "x-firewall" in headers:
            waf_info["detected"] = True
            waf_info["type"] = "WAF Genérico"
        elif "server" in headers and "akamai" in headers.get("server", "").lower():
            waf_info["detected"] = True
            waf_info["type"] = "Akamai"
    else:
        waf_info["https_blocked"] = True
        waf_info["active_protocol"] = "http"
        if https_result and https_result["blocked"]:
            waf_info["detected"] = True
            waf_info["type"] = "WAF/CDN (HTTPS bloqueado)"

    return waf_info

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

def check_http(target: str, port: int, check: dict, baseline: dict | None, waf_info: dict) -> dict | None:
    """Verifica endpoint HTTP com validação de falsos positivos."""
    proto = waf_info.get("active_protocol", "http")
    url = f"{proto}://{target}:{port}{check['path']}"
    response = make_request(url)

    if not response or response["status"] == 0:
        return None

    # Ignora 401, 403, 404 — endpoint protegido ou inexistente
    if response["status"] in [401, 403, 404]:
        return None

    # Verifica falso positivo
    if is_false_positive(response, baseline):
        return None

    if response["status"] < 400:
        context = f"Endpoint {check['path']} acessível em {proto.upper()}."
        if waf_info["detected"]:
            context += f" (Detectado {waf_info['type']} — resultado pode variar)"
        return {
            "port": port,
            "service": check["label"],
            "risk": check["risk"],
            "context": context,
            "banner": f"HTTP {response['status']}",
            "type": "http"
        }
    return None

def check_security_headers(target: str, port: int, waf_info: dict) -> list:
    """Verifica headers de segurança ausentes."""
    missing = []
    proto = waf_info.get("active_protocol", "http")
    url = f"{proto}://{target}:{port}/"
    response = make_request(url)

    if not response or response["status"] == 0:
        return missing

    headers = {k.lower(): v for k, v in response["headers"].items()}
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
    return missing

def run_scan(target: str) -> dict:
    results = []
    web_ports = []
    waf_findings = []

    # Scan de portas TCP em paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {
            executor.submit(scan_port, target, port, info): port
            for port, info in PORTS.items()
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                if result["service"] in [
                    "HTTP", "HTTPS", "HTTP-Alt", "HTTPS-Alt", "HTTP-Dev",
                    "Node/React", "Flask/Dev", "Vite/Dev", "Angular/Dev"
                ]:
                    web_ports.append(result["port"])

    # HTTP checks nos web ports encontrados
    if web_ports:
        for port in web_ports:
            # Detecta WAF/CDN
            waf_info = detect_waf(target, port)

            # Adiciona finding de WAF se detectado
            if waf_info["detected"]:
                waf_findings.append({
                    "port": port,
                    "service": f"WAF/CDN Detectado: {waf_info['type']}",
                    "risk": "ATTENTION",
                    "context": "Presença de WAF ou CDN detectada. Resultados de HTTP checks podem ser incompletos ou mascarados.",
                    "banner": None,
                    "type": "waf"
                })

            if waf_info["https_blocked"]:
                waf_findings.append({
                    "port": port,
                    "service": "HTTPS Bloqueado",
                    "risk": "ATTENTION",
                    "context": "HTTPS bloqueado pelo servidor ou WAF. Scanner utilizou HTTP como fallback — resultados podem ser imprecisos.",
                    "banner": None,
                    "type": "waf"
                })

            # Obtém baseline para detectar soft 404
            baseline = get_baseline(target, port)

            # HTTP checks com validação de falsos positivos
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                http_futures = []
                for check in HTTP_CHECKS:
                    http_futures.append(
                        executor.submit(check_http, target, port, check, baseline, waf_info)
                    )
                http_futures.append(
                    executor.submit(check_security_headers, target, port, waf_info)
                )

                for future in concurrent.futures.as_completed(http_futures):
                    result = future.result()
                    if result:
                        if isinstance(result, list):
                            results.extend(result)
                        else:
                            results.append(result)

    # Adiciona findings de WAF no início
    results = waf_findings + results

    # Ordena por risco
    risk_order = {"CRITICAL": 0, "ATTENTION": 1, "COMMON": 2}
    results.sort(key=lambda x: risk_order.get(x["risk"], 3))

    return {
        "target": target,
        "total_open_ports": len([r for r in results if r["type"] == "port"]),
        "total_findings": len(results),
        "results": results
    }
