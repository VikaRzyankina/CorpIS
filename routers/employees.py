from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from database import create_entity, get_entities, update_entity, delete_entity, session_scope, \
    create_entity_s
from models import Employee, TeamParticipation

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("/")
def create_employee(full_name: str, email: str, phone: str, position: str, hire_date: Optional[datetime] = None):
    """Создание сотрудника"""
    if hire_date is None:
        hire_date = datetime.now().date()
    return create_entity(Employee(
        full_name=full_name,
        email=email,
        phone=phone,
        hire_date=hire_date,
        position=position,
        dismissed=False
    ))


@router.get("/")
def get_employees(employee_id: Optional[int] = None):
    """Получение сотрудников (всех или по ID)"""
    result = get_entities(Employee, employee_id)
    if employee_id and not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result


@router.put("/{employee_id}")
def update_employee(employee_id: int, update_data: dict):
    """Обновление сотрудника"""
    result = update_entity(Employee, employee_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result


@router.delete("/{employee_id}")
def delete_employee(employee_id: int):
    """Удаление сотрудника"""
    result = delete_entity(Employee, employee_id)
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


@router.post("/{employee_id}/teams/{team_id}")
def set_employee_team_participation(employee_id: int, team_id: int, active: bool):
    """Установка состояния участия сотрудника в команде"""
    with session_scope() as session:
        # Ищем существующую запись
        stmt = select(TeamParticipation).where(
            TeamParticipation.employee == employee_id,
            TeamParticipation.team == team_id
        )
        existing_participation = session.scalar(stmt)

        if existing_participation:
            if existing_participation.active == active:
                return existing_participation
            else:
                existing_participation.active = active
                existing_participation.last_update = datetime.now()
                session.commit()
                return existing_participation
        else:
            return create_entity_s(session, TeamParticipation(
                last_update=datetime.now(),
                active=active,
                employee=employee_id,
                team=team_id
            ))


@router.get("/{employee_id}/teams")
def get_employee_team_participation(employee_id: int, active: Optional[bool] = None):
    """Получение состояния участия сотрудника в командах"""
    with session_scope() as session:
        stmt = select(TeamParticipation).where(TeamParticipation.employee == employee_id)

        if active is not None:
            stmt = stmt.where(TeamParticipation.active == active)

        participations = list(session.scalars(stmt).all())
        return participations
