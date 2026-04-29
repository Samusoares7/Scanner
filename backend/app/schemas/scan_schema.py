from pydantic import BaseModel
from typing import List, Optional

class ScanRequest(BaseModel):
    target: str

class PortResult(BaseModel):
    port: int
    service: str
    risk: str
    context: Optional[str] = None
    banner: Optional[str] = None
    type: Optional[str] = "port"

class ScanResponse(BaseModel):
    target: str
    total_open_ports: int
    total_findings: int
    results: List[PortResult]
