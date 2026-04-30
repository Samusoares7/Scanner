import socket
import concurrent.futures
import urllib.request
import urllib.error
import ssl
import uuid
import hashlib
from app.scanner.ports import PORTS, HTTP_CHECKS, HTTP_SECURITY_HEADERS

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def make_request(url: str, timeout: int = 3) -> dict | None:
    """Faz requisição SEM seguir redirects — importante para detectar falsos positivos."""
    try:
        is_https = url.startswith("https")
        ctx = get_ssl_context() if is_https else None

        class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        opener = urllib.request.build_opener(NoRedirectHandler())
        if ctx:
            opener = urllib.request.build_opener(
                NoRedirectHandler(),
                urllib.request.HTTPSHandler(context=ctx)
            )

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; SecurityAudit/1.0)"}
        )

        try:
            response = opener.open(req, timeout=timeout)
            content = response.read(4096)
            return {
                "status": response.status,
                "size": len(content),
                "hash": hashlib.md5(content).hexdigest(),
                "headers": dict(response.headers),
                "ok": True
            }
        except urllib.error.HTTPError as e:
            content = b""
            try:
                content = e.read(1024)
            except:
                pass
            return {
                "status": e.code,
                "size": len(content),
                "hash": hashlib.md5(content).hexdigest(),
                "headers": dict(e.headers) if e.headers else {},
                "ok": e.code < 400
            }
    except:
        return None

def get_baseline(target: str, port: int, proto: str) -> dict | None:
    """
    Requisição para path aleatório inexistente.
    Se servidor retornar 200 para isso, é soft 404.
    """
    random_path = f"/audit-check-{uuid.uuid4().hex[:10]}"
    url = f"{proto}://{target}:{port}{random_path}"
    return make_request(url)

def detect_active_protocol(target: str, port: int) -> str:
    """Detecta se o servidor responde em HTTPS ou HTTP."""
    https_result = make_request(f"https://{target}:{port}/", timeout=3)
    if https_result and https_result["status"] != 0:
        return "https"
    return "http"

def is_soft_404(response: dict, baseline: dict) -> bool:
    """
    Verifica se é soft 404 comparando com baseline.
    Servidor com soft 404 retorna 200 para qualquer path.
    """
    if baseline is None:
        return False
    if baseline["status"] != 200:
        return False
    # Mesmo hash → conteúdo idêntico → soft 404
    if response["hash"] == baseline["hash"]:
        return True
    # Tamanho muito próximo (±5%) → provavelmente soft 404
    if baseline["size"] > 0:
        diff = abs(response["size"] - baseline["size"]) / baseline["size"]
        if diff < 0.05:
            return True
    return False

def scan_port(target: str, port: int, info: dict) -> dict | None:
    """Testa se porta TCP está aberta."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        if sock.connect_ex((target, port)) == 0:
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
                "banner": banner or None,
                "type": "port"
            }
        sock.close()
    except:
        pass
    return None

def run_http_checks(target: str, port: int) -> list:
    """
    Roda HTTP checks com validação rigorosa de falsos positivos.
    Só reporta findings com evidência real.
    """
    findings = []

    # Detecta protocolo ativo
    proto = detect_active_protocol(target, port)

    # Obtém baseline para detectar soft 404
    baseline = get_baseline(target, port, proto)

    # Se o próprio baseline falhou, servidor não está respondendo
    if baseline is None:
        return findings

    # Verifica se é soft 404 com path extra para confirmar
    baseline2 = get_baseline(target, port, proto)
    soft_404 = False
    if baseline and baseline2:
        if baseline["status"] == 200 and baseline2["status"] == 200:
            if baseline["hash"] == baseline2["hash"]:
                soft_404 = True

    # HTTP checks — só roda se não for soft 404 confirmado
    seen_paths = set()
    for check in HTTP_CHECKS:
        path = check["path"]
        if path in seen_paths:
            continue
        seen_paths.add(path)

        url = f"{proto}://{target}:{port}{path}"
        response = make_request(url)

        if not response:
            continue

        # Ignora erros, não encontrados e redirecionamentos
        if response["status"] in [401, 403, 404, 405, 500, 502, 503]:
            continue

        # Ignora redirecionamentos — servidor redireciona paths inexistentes
        if 300 <= response["status"] < 400:
            redirect_location = response["headers"].get("location", "")
            baseline_location = baseline["headers"].get("location", "") if baseline else ""
            # Se redireciona para o mesmo lugar que o baseline → falso positivo
            if redirect_location == baseline_location:
                continue
            # Se redireciona para a raiz ou home → falso positivo
            if redirect_location in ["/", "/?", "/#", "/home", "/index.html"]:
                continue
            # Se o baseline também redireciona → comportamento padrão do servidor
            if baseline and 300 <= baseline["status"] < 400:
                continue

        # Verifica falso positivo
        if soft_404 or is_soft_404(response, baseline):
            continue

        # Finding válido
        if response["status"] < 400:
            findings.append({
                "port": port,
                "service": check["label"],
                "risk": check["risk"],
                "context": f"Endpoint {path} acessível via {proto.upper()} — HTTP {response['status']}.",
                "banner": f"HTTP {response['status']}",
                "type": "http"
            })

    # Headers de segurança
    root_url = f"{proto}://{target}:{port}/"
    root_response = make_request(root_url)
    if root_response and root_response["status"] < 400:
        headers = {k.lower(): v for k, v in root_response["headers"].items()}
        for h in HTTP_SECURITY_HEADERS:
            if h.lower() not in headers:
                findings.append({
                    "port": port,
                    "service": f"Header ausente: {h}",
                    "risk": "ATTENTION",
                    "context": f"Header de segurança '{h}' não configurado.",
                    "banner": None,
                    "type": "header"
                })

    return findings

def run_scan(target: str) -> dict:
    results = []
    web_ports = []

    # Scan TCP paralelo
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
                    "HTTP", "HTTPS", "HTTP-Alt", "HTTPS-Alt",
                    "HTTP-Dev", "Node/React", "Flask/Dev",
                    "Vite/Dev", "Angular/Dev"
                ]:
                    web_ports.append(result["port"])

    # HTTP checks apenas nos web ports encontrados
    for port in web_ports:
        http_findings = run_http_checks(target, port)
        results.extend(http_findings)

    # Ordena por risco
    risk_order = {"CRITICAL": 0, "ATTENTION": 1, "COMMON": 2}
    results.sort(key=lambda x: risk_order.get(x["risk"], 3))

    return {
        "target": target,
        "total_open_ports": len([r for r in results if r["type"] == "port"]),
        "total_findings": len(results),
        "results": results
    }
