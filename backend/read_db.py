import sqlite3
import json

conn = sqlite3.connect('scanner_pro.db')
cursor = conn.cursor()
cursor.execute("SELECT target, total_open_ports, results FROM scan_results ORDER BY id DESC LIMIT 5;")
rows = cursor.fetchall()

for row in rows:
    print(f"Target: {row[0]}")
    print(f"Open Ports: {row[1]}")
    results = json.loads(row[2])
    print(f"Total Findings: {len(results)}")
    for r in results:
        print(f"  - {r['service']} on port {r['port']} ({r['risk']}) - {r['type']}")
    print("-" * 20)

conn.close()
