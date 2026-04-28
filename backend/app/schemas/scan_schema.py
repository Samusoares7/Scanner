from pydantic import BaseModel
from typing import List
from datetime import datetime

class ScanRequest(BaseModel):
    target: str

class PortResult(BaseModel):
    port: int
    service: str
    risk: str

class ScanResponse(BaseModel):
    target: str
    total_open_ports: int
    results: List[PortResult]
