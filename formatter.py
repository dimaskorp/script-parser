import re
from typing import Dict


import re
from typing import Dict


class DentalFirstFormatter:
    def __init__(self):
        self.rules = {
            'headers': '<h3 class="product-subtitle" style="font-size:13px; text-align:center; text-align:justify;">{}</h3>',
            'paragraphs': '<p class="product-text" style="text-align:justify;">{}</p>',
            'lists': '<ul class="product-features">{}</ul>',
            'list_items': '<li class="product-feature">{}</li>',
            'bold': '<strong>{}</strong>',
            'italic': '<em>{}</em>'
        }

    def format_text(self, text: str) -> str:
        # Разбиваем текст на строки
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        formatted_parts = []
        list_buffer = []

        def flush_list():
            nonlocal list_buffer
            if list_buffer:
                formatted_items = ''.join(self.rules['list_items'].format(item) for item in list_buffer)
                formatted_parts.append(self.rules['lists'].format(formatted_items))
                list_buffer = []

        for line in lines:
            # Обработка списков (маркированных строк)
            if line.startswith(('- ', '* ')):
                list_buffer.append(line[2:].strip())
                continue
            else:
                # Если накоплен список, то сначала его обработать
                flush_list()

            # Обработка заголовков (оканчиваются на двоеточие)
            if line.endswith(':'):
                header_text = line.rstrip(':').strip()
                formatted_parts.append(self.rules['headers'].format(header_text))
                continue

            # Обычный абзац
            formatted_parts.append(self.rules['paragraphs'].format(line))

        # В конце проверить, остался ли незавершённый список
        flush_list()

        return '\n'.join(formatted_parts)

    def format_meta(self, meta: Dict[str, str]) -> Dict[str, str]:
        formatted_meta = {}
        for key in ['title', 'meta_description', 'keywords']:
            value = meta.get(key, '')
            # Удаление HTML-тегов
            cleaned = re.sub(r'<[^>]+>', '', value)
            # Удаление лишних пробелов и переносов
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            # Обрезка по длине для title и description
            if key == 'title' and len(cleaned) > 60:
                cleaned = cleaned[:57].rstrip() + '...'
            if key == 'meta_description' and len(cleaned) > 160:
                cleaned = cleaned[:157].rstrip() + '...'
            formatted_meta[key] = cleaned
        return formatted_meta


if __name__ == "__main__":
    formatter = DentalFirstFormatter()
    description = formatter.format_text(
        "title': '** Праймер для стеклоиономерного пломбировочного материала Vitremer 6,5 мл (1 шт.), Бренд 3M', 'meta_description': '** Праймер Vitremer от 3M обеспечивает надежную адгезию стеклоиономерных материалов к тканям зуба. Оптимальное сцепление, простота применения, быстрая полимеризация. Официальный продукт от производителя.', 'keywords': '** праймер Vitremer, стеклоиономерный материал, адгезия пломб, стоматологический праймер, 3M Vitremer, пломбировочные материалы', 'text': '**  \n\n<h3>Праймер для стеклоиономерного пломбировочного материала Vitremer 6,5 мл (1 шт.), Бренд 3M</h3>  \n\n<h3>Праймер Vitremer - надежная адгезия для прочных пломб</h3>  \n\n**Товар от производителя 3M - это** профессиональное решение для улучшения сцепления стеклоиономерных материалов с тканями зуба.  \n\n<h3>Назначение</h3>  \nПраймер Vitremer предназначен для подготовки поверхности эмали и дентина перед нанесением стеклоиономерных пломбировочных материалов. Он обеспечивает:  \n- Устранение смазанного слоя.  \n- Улучшение смачивания поверхности.  \n- Максимальную адгезию материала даже при использовании больших порций.  \n\n<h3>Состав</h3>  \nПродукт содержит компоненты, которые:  \n- Активно взаимодействуют с тканями зуба.  \n- Формируют стабильный связующий слой.  \n- Совместимы с фотополимеризацией.  \n\n<h3>Характеристики</h3>  \n- Объем: 6,5 мл.  \n- Артикул: 7100143168.  \n- Время нанесения: 30 секунд.  \n- Время сушки: 15 секунд.  \n- Время полимеризации: 20 секунд.  \n\n<h3>Преимущества</h3>  \n- Гарантирует прочное сцепление пломбы с зубом.  \n- Подходит для работы с эмалью и дентином.  \n- Упрощает процедуру пломбирования.  \n- Экономичен в использовании.  \n\n<h3>Инструкция по применению</h3>  \n1. Нанесите праймер на поверхность зуба на 30 секунд.  \n2. Высушите струей воздуха в течение 15 секунд.  \n3. Проведите фотополимеризацию в течение 20 секунд.  \nПри необходимости повторите нанесение.  \n\n<h3>Комплектация</h3>  \n- Праймер Vitremer (1 флакон, 6,5 мл).")

    print(description)