import logging
from datetime import datetime, date
from typing import List, Dict, Any, Type

import pandas as pd

from models import (
    Position, Topic, Employee, Team, Project,
    TeamParticipation, Service, Client, Payment, Contract
)

logger = logging.getLogger(__name__)

# Маппинг названий таблиц на модели
TABLE_MAPPING = {
    'должности': Position,
    'тематики': Topic,
    'сотрудники': Employee,
    'команды': Team,
    'проект': Project,
    'участие_в_команде': TeamParticipation,
    'услуга': Service,
    'клиент': Client,
    'оплата': Payment,
    'договор': Contract,
}

# Маппинг колонок на атрибуты моделей
COLUMN_MAPPING = {
    'должность': 'position',
    'обязанности': 'responsibilities',
    'тематика': 'topic',
    'ожидаемая_аудитория': 'expected_audience',
    'id': 'id',
    'фио': 'full_name',
    'email': 'email',
    'телефон': 'phone',
    'дата_найма': 'hire_date',
    'уволен': 'dismissed',
    'лидер_команды': 'team_leader',
    'договор': 'contract',
    'название': 'name',
    'описание': 'description',
    'проектная_команда': 'project_team',
    'клиент': 'client',
    'последнее_обновление': 'last_update',
    'активен': 'active',
    'сотрудник': 'employee',
    'команда': 'team',
    'обрабатывающий_сотрудник': 'processing_employee',
    'дата_обращения': 'application_date',
    'оплата': 'payment',
    'проект': 'project',
    'реализующая_команда': 'implementing_team',
    'выполнена': 'completed',
    'контактное_лицо': 'contact_person',
    'сумма': 'amount',
    'оплачено': 'paid',
    'дата_подписания': 'signing_date',
    'срок_реализации': 'implementation_deadline',
}


def detect_table(columns: List[str]) -> str:
    """Определяет тип таблицы по колонкам"""
    columns_lower = [c.lower() for c in columns]

    # Уникальные комбинации колонок для каждой таблицы
    signatures = {
        'должности': {'должность', 'обязанности'},
        'тематики': {'тематика', 'ожидаемая_аудитория'},
        'сотрудники': {'фио', 'дата_найма'},
        'команды': {'лидер_команды'},
        'проект': {'название', 'проект'},
        'участие_в_команде': {'сотрудник', 'команда', 'активен'},
        'услуга': {'дата_обращения', 'выполнена'},
        'клиент': {'контактное_лицо'},
        'оплата': {'сумма', 'оплачено'},
        'договор': {'дата_подписания', 'срок_реализации'},
    }

    for table_name, signature in signatures.items():
        if signature.issubset(set(columns_lower)):
            logger.info(f"Определена таблица: {table_name}")
            return table_name

    raise ValueError(
        f"Не удалось определить тип таблицы по колонкам: {columns}"
    )


def transform(
        records: List[Dict[str, Any]],
        table_name: str = None,
        columns: List[str] = None
) -> tuple[Type, List[Dict[str, Any]]]:
    """
    Трансформирует и валидирует данные
    Возвращает: (класс модели, список валидированных данных)
    """
    if table_name is None:
        if columns is None:
            raise ValueError("Необходимо указать table_name или columns")
        table_name = detect_table(columns)

    table_name = table_name.lower()
    model_class = TABLE_MAPPING.get(table_name)

    if not model_class:
        raise ValueError(
            f"Неизвестная таблица: {table_name}. "
            f"Доступные: {', '.join(TABLE_MAPPING.keys())}"
        )

    logger.info(f"Трансформация данных для таблицы {table_name}")

    transformed = []
    errors = []

    for idx, record in enumerate(records):
        try:
            validated = _transform_record(record)
            transformed.append(validated)
        except Exception as e:
            errors.append(f"Запись {idx + 1}: {e}")
            logger.warning(f"Ошибка валидации записи {idx + 1}: {e}")

    if errors:
        logger.warning(f"Обнаружено ошибок: {len(errors)}/{len(records)}")

    logger.info(
        f"Трансформировано {len(transformed)} записей из {len(records)}"
    )

    return model_class, transformed


def _transform_record(
        record: Dict[str, Any]
) -> Dict[str, Any]:
    """Трансформирует одну запись"""
    transformed = {}

    for col_name, value in record.items():
        # Пропуск NaN/None значений
        if pd.isna(value):
            continue

        # Маппинг имени колонки
        col_lower = col_name.lower()
        attr_name = COLUMN_MAPPING.get(col_lower, col_lower)

        # Преобразование типов
        transformed[attr_name] = _convert_value(value, attr_name)

    return transformed


def _convert_value(value: Any, attr_name: str) -> Any:
    """Преобразует значение в нужный тип"""
    # Даты
    if 'date' in attr_name or 'дата' in attr_name:
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except:
                return datetime.strptime(value, '%d.%m.%Y').date()
        elif isinstance(value, datetime):
            return value.date()
        elif isinstance(value, date):
            return value

    # DateTime
    if 'update' in attr_name or 'обновление' in attr_name:
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        elif isinstance(value, datetime):
            return value

    # Boolean
    if isinstance(value, (bool, int)) and attr_name in [
        'dismissed', 'active', 'completed', 'paid',
        'уволен', 'активен', 'выполнена', 'оплачено'
    ]:
        return bool(value)

    # Float для сумм
    if attr_name in ['amount', 'сумма']:
        return float(value)

    # Int для ID
    if attr_name == 'id' or 'id' in attr_name or attr_name.endswith('_id'):
        return int(value)

    # String по умолчанию
    return str(value).strip()
