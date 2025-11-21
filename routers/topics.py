from fastapi import APIRouter, HTTPException
from typing import Optional
from database import create_entity, get_entities, update_entity, delete_entity, logger
from models import Topic

router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("/")
def create_topic(topic: str, expected_audience: str):
    """Создание тематики"""
    return create_entity(Topic(topic=topic, expected_audience=expected_audience))


@router.get("/")
def get_topics(topic: Optional[str] = None):
    """Получение тематик (всех или по названию)"""
    result = get_entities(Topic, topic)
    if topic and not result:
        raise HTTPException(status_code=404, detail="Topic not found")
    return result


@router.put("/{topic}")
def update_topic(topic: str, expected_audience: str):
    """Обновление тематики"""
    result = update_entity(Topic, topic, {'expected_audience': expected_audience})
    if not result:
        raise HTTPException(status_code=404, detail="Topic not found")
    return result


@router.delete("/{topic}")
def delete_topic(topic: str):
    """Удаление тематики"""
    result = delete_entity(Topic, topic)
    if not result:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"message": "Topic deleted successfully"}
