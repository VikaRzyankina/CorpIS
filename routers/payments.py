from fastapi import APIRouter, HTTPException
from typing import Optional
from database import get_entities, update_entity
from models import Payment

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/")
def get_payments(payment_id: Optional[int] = None):
    """Получение оплат (всех или по ID)"""
    result = get_entities(Payment, payment_id)
    if payment_id and not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    return result


@router.put("/{payment_id}/status")
def update_payment_status(payment_id: int, paid: bool):
    """Обновление статуса оплаты"""
    result = update_entity(Payment, payment_id, {'paid': paid})
    if not result:
        raise HTTPException(status_code=404, detail="Payment not found")
    return result
