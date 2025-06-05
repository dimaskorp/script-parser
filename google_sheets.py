from typing import List, Dict
import gspread
from google.oauth2.service_account import Credentials


class GoogleSheetsHandler:
    def __init__(self, creds_file, spreadsheet_id):
        self.scope = ['https://www.googleapis.com/auth/spreadsheets']
        self.creds = Credentials.from_service_account_file(creds_file, scopes=self.scope)
        self.client = gspread.authorize(self.creds)
        self.spreadsheet_id = spreadsheet_id

    def create_sheet(self, sheet_name: str, headers: List[str]):
        try:
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                print(f"Лист '{sheet_name}' уже существует.")
                return True
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=len(headers))
                worksheet.append_row(headers)
                print(f"Лист '{sheet_name}' успешно создан с заголовками.")
                return True
        except Exception as e:
            print(f"Ошибка при создании листа: {str(e)}")
            return False

    def append_data(self, sheet_name: str, data: List[Dict[str, str]], headers: List[str]):
        """
        data: список словарей, где ключи соответствуют заголовкам headers (на русском!)
        headers: список заголовков (именно в том порядке, в каком они в таблице)
        """
        try:
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)

            rows = []
            for item in data:
                # Собираем строку в том же порядке, что и заголовки
                row = [item.get(header, '') for header in headers]
                rows.append(row)

            worksheet.append_rows(rows)
            print(f"Добавлено {len(rows)} строк.")
            return True
        except Exception as e:
            print(f"Ошибка при добавлении данных: {str(e)}")
            return False


if __name__ == "__main__":
    # Заголовки в нужном порядке
    headers = [
        "URL", "DF Номенклатура", "Бренд", "Страна", "DF Артикул",
        "DF META TITLE", "DF KEYWORDS", "DF Meta Description", "DF <h2>",
        "DF верхнее описание", "DF основное описание", "DF ID", "SIM"
    ]

    # Пример данных
    data = [
        {
            "URL": "https://dental-first.r",
            "DF Номенклатура": "Фиссулайт набор - 1 мл + 1 мл + 1 мл",
            "Бренд": "ВладМиВа",
            "Страна": "Россия",
            "DF Артикул": "00000000127",
            "DF META TITLE": "Купить Фиссулайт набор - 1 мл + 1 мл + 1 мл | Dental First",
            "DF KEYWORDS": "фиссулайт набор, фиссулайт герметик, светоотверждаемый герметик для фиссур, фиссурный герметик, фиссулайт",
            "DF Meta Description": "Фиссулайт набор - 1 мл + 1 мл + 1 мл в интернет-магазине Dental First. Каталог включает стоматологические товары в широком диапазоне цен. Помощь специалистов, быстрая доставка по всей России.",
            "DF <h2>": "Фиссулайт - надежная изоляция фиссур и углублений.",
            "DF верхнее описание": "*Фиссулайт набор* от компании **ВладМиВа** - это идеальный светоотверждаемый герметик для запечатывания фиссур и анатомических углублений интактных зубов. В составе набора находятся три шприца по 1 мл: паста белая, паста прозрачная и гель для травления эмали на органической основе. Герметик Фиссулайт обладает низкой вязкостью и устойчивостью к истиранию, благодаря чему обеспечивает надежную защиту зубов. Фторирующие компоненты, входящие в его состав, способствуют кариеспротективному эффекту. Яркая цветовая палитра герметиков, доступная в шести цветах, делает процесс лечения более увлекательным для детей, позволяя им выбирать цвет и активно участвовать в лечении. Удобные шприцы с насадками обеспечивают точное и легкое нанесение, что существенно экономит время стоматолога.",
            "DF основное описание": "# Назначение\n- Используется для запечатывания фиссур и других анатомических углублений на здоровых зубах.\n# Состав и основные свойства\n- Герметик Фиссулайт-колор - это светоотверждаемый однокомпонентный материал с низкой вязкостью.\n- Обладает высокой устойчивостью к истиранию и содержит фторирующие компоненты для защиты от кариеса.\n- Доступен в виде пасты (белой, прозрачной и цветной с мерцающим эффектом).\n- Цветные варианты удобны для нанесения и позволяют визуально контролировать процесс запечатывания и дальнейшие проверки.\n- Широкая палитра из 6 цветовых оттенков способствует привлечению внимания маленьких пациентов и дает им возможность участвовать в выборе цвета герметика.\n- Пищевые красители, входящие в состав, соответствуют международным стандартам и не вымываются из отвержденного материала.\n- Позволяет сэкономить время благодаря светоотверждению.\n- Шприцы с насадками обеспечивают легкое и точное нанесение герметика на обработанную фиссуру.\n# Комплектация\n1. Паста белая - 1 мл\n2. Паста прозрачная - 1 мл\n3. Гель для травления эмали на орг. основе - 1 мл",
            "DF ID": "418522",
            "SIM": "418522"
        }
    ]

    googleSheets = GoogleSheetsHandler('credentials.json', '1HCiKa47GkgauWBA9VA-cfsBVYJUtD1LeO4em3QQ6J7c')
    # Создаем лист с заголовками
    googleSheets.create_sheet('Product Descriptions', headers)
    # Добавляем данные
    googleSheets.append_data('Product Descriptions', data, headers)
