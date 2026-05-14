from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas import PatientInput
from app.services.ai_service import get_prediction, get_dashboard_result
from app.database.db import SessionLocal
from app.database.models import PredictionRecord

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/predict")
def predict(data: PatientInput, db: Session = Depends(get_db)):

    result = get_prediction(data)

    record = PredictionRecord(
        final_score=result["final_score"],
        risk_level=result["risk_level"],
        microbiome_score=result["modality_scores"]["microbiome"],
        voice_score=result["modality_scores"]["voice"],
        hrv_score=result["modality_scores"]["hrv"],
        inflammation_score=result["modality_scores"]["inflammation"]
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "status": "success",
        "prediction_id": record.id,
        "result": result
    }


@router.get("/dashboard-result")
def dashboard_result():
    return {
        "status": "success",
        "result": get_dashboard_result()
    }


@router.get("/prediction-history")
def prediction_history(db: Session = Depends(get_db)):

    records = db.query(PredictionRecord).order_by(
        PredictionRecord.created_at.desc()
    ).all()

    return {
        "status": "success",
        "history": records
    }