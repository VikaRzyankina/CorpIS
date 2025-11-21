from fastapi import APIRouter, HTTPException
from typing import Optional
from database import create_entity, get_entities, update_entity, delete_entity
from models import Client

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/")
def create_client(contact_person: str, phone: str, email: str):
    """Создание клиента"""
    return create_entity(Client(
        contact_person=contact_person,
        phone=phone,
        email=email
    ))


@router.get("/")
def get_clients(client_id: Optional[int] = None):
    """Получение клиентов (всех или по ID)"""
    result = get_entities(Client, client_id)
    if client_id and not result:
        raise HTTPException(status_code=404, detail="Client not found")
    return result


@router.put("/{client_id}")
def update_client(client_id: int, update_data: dict):
    """Обновление клиента"""
    result = update_entity(Client, client_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Client not found")
    return result


@router.delete("/{client_id}")
def delete_client(client_id: int):
    """Удаление клиента"""
    result = delete_entity(Client, client_id)
    if not result:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted successfully"}
