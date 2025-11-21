from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from database import get_entities, update_entity, delete_entity, session_scope, \
    create_entity_s
from models import Contract, Payment

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("/")
def create_contract(processing_employee: int,
                    client: int, amount: int,
                    implementation_deadline: Optional[datetime] = None, signing_date: Optional[datetime] = None):
    """Создание договора"""

    if signing_date is None:
        signing_date = datetime.now().date()
    with session_scope() as session:
        payment = create_entity_s(session, Payment(
            amount=amount,
            paid=False
        ))
        return create_entity_s(session, Contract(
            signing_date=signing_date,
            implementation_deadline=implementation_deadline,
            processing_employee=processing_employee,
            client=client,
            payment=payment.id
        ))


@router.get("/")
def get_contracts(contract_id: Optional[int] = None):
    """Получение договоров (всех или по ID)"""
    result = get_entities(Contract, contract_id)
    if contract_id and not result:
        raise HTTPException(status_code=404, detail="Contract not found")
    return result


@router.put("/{contract_id}")
def update_contract(contract_id: int, update_data: dict):
    """Обновление договора"""
    result = update_entity(Contract, contract_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Contract not found")
    return result


@router.delete("/{contract_id}")
def delete_contract(contract_id: int):
    """Удаление договора"""
    result = delete_entity(Contract, contract_id)
    if not result:
        raise HTTPException(status_code=404, detail="Contract not found")
    return {"message": "Contract deleted successfully"}
