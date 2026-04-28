import json

def generate_report(scan_result: dict) -> str:
    return json.dumps(scan_result, indent=2)
