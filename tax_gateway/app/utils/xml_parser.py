import xml.etree.ElementTree as ET
from typing import Any

def _build_element(tag: str, content: Any) -> ET.Element:
    """
    Рекурсивный помощник для сборки XML-элементов.
    Если content — это словарь, он создает вложенные теги.
    Если это текст/число — записывает как значение тега.
    """
    elem = ET.Element(tag)
    
    if isinstance(content, dict):
        for key, val in content.items():
            elem.append(_build_element(key, val))
    else:
        # Приводим всё к строке (числа, UUID и т.д.)
        elem.text = str(content)
        
    return elem

def dict_to_xml(data: dict) -> str:
    """
    Главная функция конвертации.
    Ожидает словарь с одним корневым ключом, например:
    {"TaxReport": {"Id": "123", "Amount": "100"}}
    """
    if not data or len(data) != 1:
        raise ValueError("Словарь для XML должен содержать ровно один корневой элемент")
    
    # Достаем имя корневого тега (в нашем случае "TaxReport")
    root_tag = list(data.keys())[0]
    root_content = data[root_tag]
    
    # Строим дерево
    root_elem = _build_element(root_tag, root_content)
    
    # Превращаем дерево в готовую строку с правильной кодировкой
    # xml_declaration=True добавит <?xml version="1.0" encoding="utf-8"?> в начало
    xml_bytes = ET.tostring(root_elem, encoding="utf-8", xml_declaration=True)
    
    return xml_bytes.decode("utf-8")