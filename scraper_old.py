import logging
import re
import time
import random
from typing import Dict, Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompetitorScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://www.google.com/'
        })

    def search_product(self) -> list[dict[str, str | None]]:
        # Добавляем задержку между запросами
        time.sleep(random.uniform(*config.CONFIG['request_delay']))

        descriptions = []

        for competitor in config.CONFIG['competitors']:
            try:
                search_url = self._get_search_url(competitor)
                response = self.session.get(search_url)
                if response.status_code == 401:
                    print(f"Authorization required for {competitor}, trying with cookies...")
                    product_description = self._try_with_cookies(competitor)
                    if product_description:
                        descriptions.append({
                            'competitor': competitor,
                            'title': competitor,
                            'description': product_description
                        })
                    continue  # чтобы не вызвать raise_for_status ниже
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                url_products = self._find_product_page(soup, competitor)

                if not url_products:
                    print(f"Не найдено товаров у {competitor}")
                    continue

                for product in url_products:
                    link = product.find('a')
                    if link:
                        product_info = self._get_product_description(competitor, urljoin(competitor, link['href']))
                        if product_info:
                            print(f"Сайт: {competitor}")
                            print(f"Название: {product_info['title']}")
                            print(f"Описание: {product_info['description']}")
                            descriptions.append({
                                'competitor': competitor,
                                'title': product_info['title'],
                                'description': product_info['description']
                            })
            except Exception as e:
                print(f"Error searching on {competitor}': {str(e)}")
                continue

        return descriptions

    def _try_with_cookies(self, competitor: str) -> str | None:
        """Попытка доступа с использованием cookies

        Аргументы:
        competitor (str): URL конкурента, на котором выполняется поиск товара.

        Возвращает:
        str | None: Описание продукта, если оно найдено, иначе None.
        """
        try:
            # Получаем cookies с главной страницы конкурента
            self.session.get(competitor)
            time.sleep(2)  # Пауза для гарантии получения cookies

            # Формируем URL для поиска товаров
            search_url = self._get_search_url(competitor)
            response = self.session.get(search_url)

            if response.status_code == 200:
                # Парсим ответ
                soup = BeautifulSoup(response.text, 'html.parser')

                # Ищем страницы продуктов
                url_products = self._find_product_page(soup, competitor)
                for product in url_products:
                    link = product.find('a')
                    if link:
                        # Возвращаем описание продукта
                        return self._get_product_description(competitor, urljoin(competitor, link['href']))

        except Exception as e:
            # Логируем ошибку, если что-то пошло не так
            print(f"Ошибка при использовании cookies на {competitor}: {str(e)}")
        return None

    @staticmethod
    def _find_product_page(soup: BeautifulSoup, competitor: str) -> Optional[list[BeautifulSoup]]:
        """Пытается найти описание на странице товара)"""
        try:
            if 'el-dent.ru' in competitor:
                return soup.find_all('div', class_='col --product-card')
            elif 'stomatorg.ru' in competitor:
                return soup.find_all('div', class_='itemListElement')
            elif 'www.nika-dent.ru' in competitor:
                return soup.find_all('div', class_='product-item loadmore_item')
            elif 'aveldent.ru' in competitor:
                return soup.find_all('div', class_='span3 item_prod')
        except Exception as e:
            print(f"Error in direct description check: {str(e)}")

        return None

    @staticmethod
    def _get_search_url(competitor: str) -> str | None:
        if 'el-dent.ru' in competitor:
            return f"{competitor}/adgezivy-i-bondy-5-pokoleniya.html?v[12]=2"
        elif 'stomatorg.ru' in competitor:
            return f"{competitor}/catalog/adgezivnye_materialy/"
        elif 'www.nika-dent.ru' in competitor:
            return f"{competitor}/catalog/terapiya/adgezivy/adgezivy-5-pokoleniya/filter/b24_proizvoditel-is-374421/apply/"
        elif 'aveldent.ru' in competitor:
            return f"{competitor}/stomatologicheskie-materiali/adgezivnie-materialy/adgezivi-brand-3M"
        else:
            return f"{competitor}/search?q"

    def _get_product_description(self, competitor: str, url: str) -> Optional[Dict[str, str]]:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            if 'el-dent.ru' in competitor:
                title_tag = soup.find('h1', class_='product-card__title title-sm')
                desc_tag = soup.find('div', itemprop='description', class_='product-card__tabs-content order-1 active')
            elif 'stomatorg.ru' in url:
                title_tag = soup.find('div', class_='col-12').find('h1')
                desc_tag = soup.find('div', class_='tabs')
            elif 'www.nika-dent.ru' in url:
                title_tag = soup.find('h1', class_='product-name header2 item-link')
                desc_tag = soup.find('div', class_='tabs-content__item active')
            elif 'aveldent.ru' in url:
                title_tag = soup.find('div', class_='span12').find('h1')
                desc_tag = soup.find('p', class_='span12 description')
            else:
                title_tag = soup.find('h1')
                desc_tag = soup.find('div', class_=re.compile('description|desc', re.I))
            title = title_tag.get_text(strip=True) if title_tag else None
            desc = desc_tag.get_text(strip=True) if desc_tag else None

            return {
                'title': title,
                'description': desc
            }
        except Exception as e:
            print(f"Error getting description from {url}: {str(e)}")
            return None


if __name__ == "__main__":
    scraper2 = CompetitorScraper()
    description = scraper2.search_product()
    print(description)
