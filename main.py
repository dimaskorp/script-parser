import time
import config
from generator import DescriptionGenerator
from google_sheets import GoogleSheetsHandler
from parser import DentalFirstParser
from scraper import CompetitorScraper


def process_products(product_urls: str, secret_key: str, google_creds: str, spreadsheet_id: str):
    start_time = time.time()

    # Инициализация компонентов
    parser = DentalFirstParser()
    scraper = CompetitorScraper()
    generator = DescriptionGenerator(secret_key)
    sheets = GoogleSheetsHandler(google_creds, spreadsheet_id)
    products = parser.parse_products(product_urls)

    # Создаем лист в таблице
    sheet_name = 'Product Descriptions'
    headers = [
        "URL", "DF Номенклатура", "Бренд", "Страна", "DF Артикул",
        "DF META TITLE", "DF KEYWORDS", "DF Meta Description", "DF <h2>",
        "DF верхнее описание", "DF основное описание", "DF ID", "SIM"
    ]
    results = []
    combined_descriptions = []
    total = len(products)

    for idx, product in enumerate(products, start=1):
        # Вывод прогресса
        progress_percent = (idx / total) * 100
        print(f"Progress: {progress_percent:.2f}% ({idx}/{total})")
        try:
            article_number = product["article_number"]
            combined_description = scraper.search_product(article_number)
            if not combined_description:
                print(f"No descriptions found for {article_number}")
                continue

            # # Генерируем новое описание
            # generated = generator.generate_description(combined_description)
            # if not generated:
            #     print(f"Failed to generate description for {article_number}")
            #     continue
            #
            # results.append(generated)

            if combined_description:
                print(f"Descriptions found for {article_number}")
                combined_descriptions.append({
                    'URL': product['url'],
                    'DF Номенклатура': product['nomenclature'],
                    'Бренд': product['brand'],
                    'Страна': product['country'],
                    'DF Артикул': product['article_number'],
                    'DF META TITLE': combined_description['meta_title'],
                    'DF KEYWORDS': combined_description['meta_keywords'],
                    'DF Meta Description': combined_description['meta_description'],
                    'DF <h2>': combined_description['h2'],
                    'DF верхнее описание': combined_description['top_description'],
                    'DF основное описание': combined_description['basic_description'],
                    'DF ID': product['id'],
                    'SIM': product['sim'], }
                )

        except Exception as e:
            print(f"Error processing {product}: {str(e)}")
            continue

    # Записываем результаты в Google Sheets
    if combined_descriptions:
        sheets.create_sheet(sheet_name, headers)
        sheets.append_data(sheet_name, combined_descriptions, headers)

    end_time = time.time()
    print(f"Processing completed in {end_time - start_time:.2f} seconds")
    print(f"Processed {len(results)} products out of {len(product_urls)}")

    return results


if __name__ == "__main__":
    # Конфигурация
    PRODUCT_URLS = config.CONFIG["dental_first_url"]
    OPENAI_KEY = config.CONFIG["client_secret"]
    GOOGLE_CREDS = config.CONFIG["google_creds_file"]
    SPREADSHEET_ID = config.CONFIG["spreadsheet_id"]

    # Запуск обработки
    process_products(PRODUCT_URLS, OPENAI_KEY, GOOGLE_CREDS, SPREADSHEET_ID)
