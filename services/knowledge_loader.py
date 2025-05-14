from pathlib import Path
from typing import Optional, Tuple
from utils.logging import logger


def load_section_knowledge(
        section: str) -> Tuple[Optional[str], Optional[str]]:
    """Загружает базу знаний для указанного раздела"""
    try:
        if not section or '.' not in section:
            return None, None

        # Обработка основных разделов (например "3.")
        if section.endswith('.'):
            main_part = section.split('.')[0]
            # Для основных разделов берем первый подраздел
            section = f"{main_part}.1"

        main_part, sub_part = section.split('.', 1)
        main_part = main_part.strip()
        sub_part = sub_part.split()[0].strip()  # Берем только номер

        # Определяем папку
        folder_map = {
            '1': 'cadrovik_1',
            '2': 'admin_2',
            '3': 'employee_3',
            '4': 'signer_4',
            '5': 'sogl_5',
            '6': 'process_6',
            '7': 'stl_cadr_7',
            '8': 'stl_candidat_8',
            '9': 'stl_9',
            '10': 'stl_10',
            '11': 'stl_11',
            '12': 'stl_12',
            '13': 'stl_13'
        }

        folder = folder_map.get(main_part)
        if not folder:
            return None, None

        # Формируем имя файла
        if main_part == '5':  # Особый случай
            file_name = '5.txt'
        else:
            file_name = f"{main_part}_{sub_part}.txt"

        # Полный путь к файлу
        file_path = Path(__file__).parent.parent / 'utils' / folder / file_name

        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():  # Проверяем, что файл не пустой
                    return content, str(file_path)

        logger.warning(f"Файл не найден или пуст: {file_path}")
        return None, None

    except Exception as e:
        logger.error(f"Ошибка загрузки раздела {section}: {str(e)}")
        return None, None
