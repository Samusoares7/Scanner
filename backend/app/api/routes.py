from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.scan_schema import ScanRequest
from app.scanner.scan import run_scan
from app.database import get_db
from app.models import ScanResult
from app.auth import verify_password, create_access_token, get_current_user, FAKE_USER
import json

router = APIRouter()

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != FAKE_USER["username"]:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    if not verify_password(form_data.password, FAKE_USER["password"]):
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/scan")
def start_scan(request: ScanRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    result = run_scan(request.target)
    db_scan = ScanResult(
        target=result["target"],
        total_open_ports=result["total_open_ports"],
        results=json.dumps(result["results"])
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return result

@router.get("/scans")
def get_scans(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    scans = db.query(ScanResult).all()
    return [
        {
            "id": s.id,
            "target": s.target,
            "total_open_ports": s.total_open_ports,
            "results": json.loads(s.results),
            "created_at": s.created_at
        }
        for s in scans
    ]

@router.get("/scans/{id}")
def get_scan_by_id(id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    scan = db.query(ScanResult).filter(ScanResult.id == id).first()
    if not scan:
        return {"error": "Scan não encontrado"}
    return {
        "id": scan.id,
        "target": scan.target,
        "total_open_ports": scan.total_open_ports,
        "results": json.loads(scan.results),
        "created_at": scan.created_at
    }
