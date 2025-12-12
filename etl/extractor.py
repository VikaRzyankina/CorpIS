import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = {'.csv', '.xls', '.xlsx', '.ods'}


def extract(file_path: str) -> tuple[List[Dict[str, Any]], List[str]]:
    """
    Извлекает данные из файла
    Возвращает: (список строк как словарей, список колонок)
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Неподдерживаемый формат файла. "
            f"Поддерживаются: {', '.join(SUPPORTED_FORMATS)}"
        )

    logger.info(f"Извлечение данных из {file_path}")

    # Чтение файла
    if path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path)
    elif path.suffix.lower() in {'.xls', '.xlsx'}:
        df = pd.read_excel(file_path)
    else:
        df = pd.read_excel(file_path, engine='odf')

    # Преобразование в список словарей
    records = df.to_dict('records')
    columns = df.columns.tolist()

    logger.info(f"Извлечено {len(records)} записей, {len(columns)} колонок")

    return records, columns
