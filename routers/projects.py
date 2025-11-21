from typing import Optional

from fastapi import APIRouter, HTTPException

from database import get_entities, update_entity, delete_entity, session_scope, get_entities_s, \
    create_entity_s
from models import Project, Payment, Contract

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/")
def contract_to_project(contract_id: int, name: str, description: str,
                        project_team: int, topic: str):
    """Повышение договора до проекта (только при оплаченной оплате)"""
    with session_scope() as session:
        # Получаем договор и проверяем оплату
        contract = get_entities_s(session, Contract, contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")

        payment = get_entities_s(session, Payment, contract.payment)
        if not payment or not payment.paid:
            raise HTTPException(status_code=400, detail="Payment not completed")

        # Создаем проект
        return create_entity_s(session, Project(
            contract=contract_id,
            name=name,
            description=description,
            project_team=project_team,
            topic=topic,
            client=contract.client
        ))


@router.get("/")
def get_projects(project_name: Optional[str] = None):
    """Получение проектов (всех или по названию)"""
    result = get_entities(Project, project_name)
    if project_name and not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.put("/{project_name}")
def update_project(project_name: str, update_data: dict):
    """Обновление проекта"""
    result = update_entity(Project, project_name, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.delete("/{project_name}")
def delete_project(project_name: str):
    """Удаление проекта"""
    result = delete_entity(Project, project_name)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}
