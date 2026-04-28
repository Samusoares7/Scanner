import socket
from app.scanner.ports import PORTS

def run_scan(target: str):
    open_ports = []
    for port, info in PORTS.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((target, port))
            if result == 0:
                open_ports.append({
                    "port": port,
                    "service": info["service"],
                    "risk": info["risk"]
                })
            sock.close()
        except:
            continue
    return {
        "target": target,
        "total_open_ports": len(open_ports),
        "results": open_ports
    }
