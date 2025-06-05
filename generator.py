import re
import uuid
from typing import List, Dict

import requests


class DescriptionGenerator:
    def __init__(self, secret_key: str):
        self.authorization_key = secret_key
        self.token = None
        self.prompt_template = """
        На основе следующего описания товара из стоматологической сферы создай новое, уникальное и SEO-оптимизированное описание:

        {original_description}

        Требования к новому описанию:
        1. Сохранить все ключевые характеристики и преимущества
        2. Использовать профессиональную терминологию
        3. Оптимизировать для SEO (естественное включение ключевых слов)
        4. Длина 150-300 слов
        5. Структурированный текст с абзацами
        6. Уникальность не менее 85%

        Запрещенные символы
        1. Любые тире меняем на дефис - ‘ ‘ и “ ” меняем на « »
        2. Значки типо ®, ™ и тд. - удаляем
        3. Значок мат.степени - удаляем (25 мм² -> 25 мм2)
        3. Значок градуса ° либо убираем (30° С -> 30 С) либо пишем текстом (угол 30 градусов)
        4. Знак умножения “×” меняем на “*”
        5. Знак “±” удаляем или меняем на “около”
        6. Знаки “≥” и “≤” удаляем или меняем на “больше или равно”

        Структура:
        1. заголовок: «Название товара - слоган» (не длиннее одной строки).
        3. Дескрипшен: «Товар от производителя, указать бренд - это ...».
        4. Основное описание с разделами: Назначение, Состав, Характеристики, Преимущества (можно больше или меньше, если нужно).
        5. Комплектация: если товар единичный — копия названия товара в поле Комплектация. Если набор — верстай по стандарту.

        Также создай:
        - Title (до 60 символов)
        - Meta Description (до 160 символов)
        - Keywords (5-7 ключевых слов/фраз)

        Верни ответ в формате:
        Title: ...
        Description: ...
        Keywords: ...
        Text: ...
        """

    def _get_oauth_token(self) -> str:
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': str(uuid.uuid4()),
            'Authorization': f'Basic {self.authorization_key}'
        }
        payload = {'scope': 'GIGACHAT_API_PERS'}
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json().get('access_token')

    def _ensure_token(self):
        if not self.token:
            self.token = self._get_oauth_token()

    def generate_description(self, original_description: str) -> Dict[str, str] or None:
        try:
            self._ensure_token()
            api_url = "https://gigachat.devices.sberbank.ru/api/v1/completions"
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Accept': 'application/json',
                'RqUID': str(uuid.uuid4())
            }
            json_data = {
                "model": "GigaChat",  # или "gigachat-pro", если доступно
                "messages": [
                    {"role": "system", "content": "Ты профессиональный копирайтер для стоматологического e-commerce."},
                    {"role": "user", "content": self.prompt_template.format(original_description=original_description)}
                ]
            }
            response = requests.post(api_url, headers=headers, json=json_data, verify=False)  # Для продакшена укажите verify с сертификатом
            response.raise_for_status()
            generated_text = response.json()['choices'][0]['message']['content']
            return self._parse_generated_text(generated_text)
        except Exception as e:
            print(f"Error generating description: {e}")
            return None

    def _parse_generated_text(self, text: str) -> Dict[str, str]:
        result = {
            'title': '',
            'meta_description': '',
            'keywords': '',
            'text': ''
        }
        title_match = re.search(r'Title:\s*(.+)', text)
        if title_match:
            result['title'] = title_match.group(1).strip()

        desc_match = re.search(r'Description:\s*(.+)', text)
        if desc_match:
            result['meta_description'] = desc_match.group(1).strip()

        keywords_match = re.search(r'Keywords:\s*(.+)', text)
        if keywords_match:
            result['keywords'] = keywords_match.group(1).strip()

        text_match = re.search(r'Text:\s*(.+)', text, re.DOTALL)
        if text_match:
            result['text'] = text_match.group(1).strip()

        return result

    def batch_generate(self, descriptions: List[str]) -> List[Dict[str, str]]:
        return [self.generate_description(desc) for desc in descriptions]


if __name__ == "__main__":

    generator = DescriptionGenerator()
    description = generator.generate_description(
        "Праймер для материала стеклоиономерного пломбировочного Vitremer\n"
        "Функция праймера материала Vitremer™ заключается в изменении смазанного слоя и адекватном смачивании поверхности зубов, "
        "чтобы облегчить адгезию стеклоиономера к структуре зуба, в частности, когда стеклоиономер вносят большой порцией, "
        "превышающей те, которые могут быть просвечены светом.\n"
        "Обеспечивает максимальное сцепление стеклоиономерного пломбировочного материала с тканями зуба.\n"
        "Нанесите праймер в течение 30 секунд на контактные поверхности эмали и дентина. При необходимости праймер можно нанести повторно\n"
        "Высушите праймер струей воздуха в течение 15 секунд\n"
        "Фотополимеризуйте праймер в течение 20 секунд"
    )

    print(description)
