import logging
from typing import List, Dict, Any, Type

from database import session_scope, create_entity_s

logger = logging.getLogger(__name__)


def load(
        model_class: Type,
        records: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Загружает данные в БД
    Возвращает статистику загрузки
    """
    logger.info(f"Загрузка {len(records)} записей в {model_class.__tablename__}")

    stats = {
        'total': len(records),
        'success': 0,
        'failed': 0,
        'errors': []
    }

    with session_scope() as session:
        for idx, record_data in enumerate(records):
            try:
                entity = model_class(**record_data)
                create_entity_s(session, entity)
                stats['success'] += 1
            except Exception as e:
                stats['failed'] += 1
                error_msg = f"Запись {idx + 1}: {e}"
                stats['errors'].append(error_msg)
                logger.error(error_msg)

    logger.info(
        f"Загрузка завершена: {stats['success']} успешно, "
        f"{stats['failed']} ошибок"
    )

    return stats


def visualize_stats(stats: Dict[str, Any], model_class: Type) -> str:
    """Создает текстовую сводку результатов загрузки"""
    lines = [
        "=" * 60,
        f"РЕЗУЛЬТАТЫ ЗАГРУЗКИ: {model_class.__tablename__}",
        "=" * 60,
        f"Всего записей:      {stats['total']}",
        f"Загружено успешно:  {stats['success']}",
        f"Ошибок:             {stats['failed']}",
        f"Процент успеха:     {stats['success'] / stats['total'] * 100:.1f}%",
    ]

    if stats['errors']:
        lines.append("\nОШИБКИ:")
        lines.append("-" * 60)
        for error in stats['errors'][:10]:  # Показываем первые 10 ошибок
            lines.append(f"  • {error}")

        if len(stats['errors']) > 10:
            lines.append(f"  ... и еще {len(stats['errors']) - 10} ошибок")

    lines.append("=" * 60)

    return "\n".join(lines)
