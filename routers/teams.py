from fastapi import APIRouter, HTTPException
from typing import Optional
from database import create_entity, get_entities, update_entity, delete_entity
from models import Team

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/")
def create_team(team_leader: int):
    """Создание команды"""
    return create_entity(Team(team_leader=team_leader))


@router.get("/")
def get_teams(team_id: Optional[int] = None):
    """Получение команд (всех или по ID)"""
    result = get_entities(Team, team_id)
    if team_id and not result:
        raise HTTPException(status_code=404, detail="Team not found")
    return result


@router.put("/{team_id}")
def update_team(team_id: int, team_leader: int):
    """Обновление команды"""
    result = update_entity(Team, team_id, {'team_leader': team_leader})
    if not result:
        raise HTTPException(status_code=404, detail="Team not found")
    return result


@router.delete("/{team_id}")
def delete_team(team_id: int):
    """Удаление команды"""
    result = delete_entity(Team, team_id)
    if not result:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"message": "Team deleted successfully"}
