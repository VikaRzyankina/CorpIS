import argparse
import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import inspect as sa_inspect

from database import session_scope, get_entities_s
from etl.extractor import extract, SUPPORTED_FORMATS
from etl.loader import load, visualize_stats
from etl.transformer import transform, TABLE_MAPPING

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s\t%(levelname)s:\t%(message)s',
)
logger = logging.getLogger(__name__)


def import_data(file_path: str, table_name: str = None):
    """Импорт данных из файла в БД"""
    print(f"\n{'=' * 60}")
    print(f"ИМПОРТ ДАННЫХ")
    print(f"{'=' * 60}")

    # Extract
    print(f"\nИзвлечение данных из {file_path}")
    records, columns = extract(file_path)
    print(f"   Извлечено {len(records)} записей, {len(columns)} колонок")

    # Transform
    print(f"\nТрансформация и валидация")
    model_class, transformed = transform(
        records,
        table_name=table_name,
        columns=columns
    )
    print(f"   Таблица: {model_class.__tablename__}")
    print(f"   Валидировано {len(transformed)}/{len(records)} записей")

    if len(transformed) < len(records):
        print(f"   Пропущено невалидных записей: {len(records) - len(transformed)}")

    # Load
    print(f"\nЗагрузка в БД")
    stats = load(model_class, transformed)

    # Визуализация
    print("\n" + visualize_stats(stats, model_class))

    if stats['failed'] > 0:
        print(f"\nЗагрузка завершена с ошибками!", file=sys.stderr)
        return False

    print("\nИмпорт успешно завершен!")
    return True


def export_data(table_name: str, output_path: str):
    """Экспорт данных из БД в файл"""
    print(f"\n{'=' * 60}")
    print(f"ЭКСПОРТ ДАННЫХ")
    print(f"{'=' * 60}")

    # Получаем модель
    table_name_lower = table_name.lower()
    model_class = TABLE_MAPPING.get(table_name_lower)

    if not model_class:
        raise ValueError(
            f"Неизвестная таблица: {table_name}. "
            f"Доступные: {', '.join(TABLE_MAPPING.keys())}"
        )

    print(f"\nИзвлечение данных из таблицы: {model_class.__tablename__}")

    # Получаем данные из БД
    with session_scope() as session:
        entities = get_entities_s(session, model_class)

    if not entities:
        print(f"   Таблица {model_class.__tablename__} пуста")
        return False

    print(f"   Извлечено {len(entities)} записей")

    # Преобразуем в словари
    records = []
    for entity in entities:
        record = {}
        # Получаем инспектор для правильного маппинга атрибутов
        state = sa_inspect(entity)
        for attr in state.mapper.column_attrs:
            # attr.key - это имя Python атрибута (topic)
            value = getattr(entity, attr.key)
            # attr.columns[0].name - имя колонки в БД (тематика)
            record[attr.columns[0].name] = value
        records.append(record)

    # Создаем DataFrame
    df = pd.DataFrame(records)

    # Определяем формат по расширению
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nСохранение в файл: {output_path}")

    if output_path.suffix.lower() == '.csv':
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
    elif output_path.suffix.lower() in {'.xls', '.xlsx'}:
        df.to_excel(output_path, index=False, engine='openpyxl')
    elif output_path.suffix.lower() == '.ods':
        df.to_excel(output_path, index=False, engine='odf')
    else:
        raise ValueError(f"Неподдерживаемый формат файла: {output_path.suffix}")

    print(f"   Сохранено {len(records)} записей")
    print(f"\nЭкспорт успешно завершен!")
    return True


def import_all(input_dir: str):
    """Импорт всех файлов из директории"""
    input_path = Path(input_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Директория не найдена: {input_dir}")

    if not input_path.is_dir():
        raise ValueError(f"Путь не является директорией: {input_dir}")

    # Находим все поддерживаемые файлы
    files = []
    for ext in SUPPORTED_FORMATS:
        files.extend(input_path.glob(f"*{ext}"))

    if not files:
        print(f"В директории {input_dir} не найдено поддерживаемых файлов")
        return False

    print(f"\n{'=' * 60}")
    print(f"МАССОВЫЙ ИМПОРТ")
    print(f"{'=' * 60}")
    print(f"Найдено файлов: {len(files)}\n")

    success_count = 0
    failed_count = 0

    for file_path in sorted(files):
        try:
            print(f"\n{'─' * 60}")
            result = import_data(str(file_path))
            if result:
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
            print(f"\nОшибка импорта {file_path.name}: {e}")
            logger.exception(f"Ошибка импорта {file_path}")

    print(f"\n{'=' * 60}")
    print(f"ИТОГО:")
    print(f"  Успешно: {success_count}")
    print(f"  Ошибок:  {failed_count}")
    print(f"{'=' * 60}\n")

    return failed_count == 0


def export_all(output_dir: str, file_format: str = 'csv'):
    """Экспорт всех таблиц в директорию"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"МАССОВЫЙ ЭКСПОРТ")
    print(f"{'=' * 60}")
    print(f"Таблиц для экспорта: {len(TABLE_MAPPING)}\n")

    success_count = 0
    failed_count = 0

    for table_name in sorted(TABLE_MAPPING.keys()):
        try:
            print(f"\n{'─' * 60}")
            file_name = f"{table_name}.{file_format}"
            file_path = output_path / file_name
            result = export_data(table_name, str(file_path))
            if result:
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
            print(f"\nОшибка экспорта {table_name}: {e}")
            logger.exception(f"Ошибка экспорта {table_name}")

    print(f"\n{'=' * 60}")
    print(f"ИТОГО:")
    print(f"  Успешно: {success_count}")
    print(f"  Ошибок:  {failed_count}")
    print(f"{'=' * 60}\n")

    return failed_count == 0


def main():
    parser = argparse.ArgumentParser(
        description='CLI для ETL процессов',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Команда для выполнения')

    # Команда import
    import_parser = subparsers.add_parser('import', help='Импорт данных из файла в БД')
    import_parser.add_argument('--file', '-f', required=True, help='Путь к файлу для импорта или директория для массового импорта')
    import_parser.add_argument('--table', '-t', help='Название таблицы (опционально, автоопределение)')

    # Команда export
    export_parser = subparsers.add_parser('export', help='Экспорт данных из БД в файл')
    export_group = export_parser.add_mutually_exclusive_group(required=True)
    export_group.add_argument('--table', '-t', help='Название таблицы для экспорта')
    export_group.add_argument('--all', '-a', default=True, action='store_true', help='Экспорт всех таблиц')
    export_parser.add_argument('--output', '-o', required=True, help='Путь для сохранения (файл или директория)')
    export_parser.add_argument('--format', '-fmt', default='csv', choices=['csv', 'xlsx', 'xls', 'ods'],
                               help='Формат файла при экспорте всех таблиц (по умолчанию: csv)')

    # Команда tables
    tables_parser = subparsers.add_parser('tables', help='Показать список доступных таблиц')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'import':
            file_path = Path(args.file)
            if file_path.is_dir():
                # Массовый импорт
                success = import_all(str(file_path))
                exit(0 if success else 1)
            else:
                # Импорт одного файла
                success = import_data(args.file, args.table)
                exit(0 if success else 1)

        elif args.command == 'export':
            if args.all:
                # Массовый экспорт
                success = export_all(args.output, args.format)
                exit(0 if success else 1)
            else:
                # Экспорт одной таблицы
                success = export_data(args.table, args.output)
                exit(0 if success else 1)

        elif args.command == 'tables':
            print("\nДоступные таблицы:\n")
            for table_name in sorted(TABLE_MAPPING.keys()):
                model = TABLE_MAPPING[table_name]
                print(f"  • {table_name:20} → {model.__name__}")
            print()

    except Exception as e:
        print(f"\nОШИБКА: {e}\n", file=sys.stderr)
        logger.exception("Ошибка выполнения команды")
        exit(1)


if __name__ == '__main__':
    import sys

    main()
