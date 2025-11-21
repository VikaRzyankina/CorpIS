from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional
from database import create_entity, get_entities, update_entity, delete_entity, session_scope, create_entity_s
from models import Service, Payment

router = APIRouter(prefix="/services", tags=["services"])


@router.post("/")
def create_service(processing_employee: int, amount: int, project: int,
                   implementing_team: int, completed: bool = False,
                   application_date: Optional[datetime] = None):
    """Создание услуги с автопометкой даты обращения (если не передана)"""
    if application_date is None:
        application_date = datetime.now().date()

    with session_scope() as session:
        payment = create_entity_s(session, Payment(
            amount=amount,
            paid=False
        ))
        return create_entity(Service(
            processing_employee=processing_employee,
            application_date=application_date,
            payment=payment.id,
            project=project,
            implementing_team=implementing_team,
            completed=completed
        ))


@router.get("/")
def get_services(service_id: Optional[int] = None):
    """Получение услуг (всех или по ID)"""
    result = get_entities(Service, service_id)
    if service_id and not result:
        raise HTTPException(status_code=404, detail="Service not found")
    return result


@router.put("/{service_id}")
def update_service(service_id: int, update_data: dict):
    """Обновление услуги"""
    result = update_entity(Service, service_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Service not found")
    return result


@router.delete("/{service_id}")
def delete_service(service_id: int):
    """Удаление услуги"""
    result = delete_entity(Service, service_id)
    if not result:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"}
