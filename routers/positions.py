from fastapi import APIRouter, HTTPException
from typing import Optional
from database import create_entity, get_entities, update_entity, delete_entity
from models import Position

router = APIRouter(prefix="/positions", tags=["positions"])


@router.post("/")
def create_position(position: str, responsibilities: str):
    """Создание должности"""
    return create_entity(Position(position=position, responsibilities=responsibilities))


@router.get("/")
def get_positions(position: Optional[str] = None):
    """Получение должностей (всех или по названию)"""
    result = get_entities(Position, position)
    if position and not result:
        raise HTTPException(status_code=404, detail="Position not found")
    return result


@router.put("/{position}")
def update_position(position: str, responsibilities: str):
    """Обновление должности"""
    result = update_entity(Position, position, {'responsibilities': responsibilities})
    if not result:
        raise HTTPException(status_code=404, detail="Position not found")
    return result


@router.delete("/{position}")
def delete_position(position: str):
    """Удаление должности"""
    result = delete_entity(Position, position)
    if not result:
        raise HTTPException(status_code=404, detail="Position not found")
    return {"message": "Position deleted successfully"}
