from datetime import time
from random import random
from typing import Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import config


class CompetitorScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Referer': 'https://stomatorg.ru/'
        })

    def search_product(self, article: str) -> dict[str, str | None]:
        descriptions = []
        for competitor in config.CONFIG['competitors']:
            try:
                search_url = self._get_search_url(competitor, article)
                response = self.session.get(search_url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                product_url = self._find_product_page(soup, competitor, article)
                if product_url:
                    product_description = self._get_product_description(competitor, product_url)
                    if product_description:
                        descriptions.append(product_description)
                else:
                    print(f"Product {article} not found on {competitor}")

            except Exception as e:
                print(f"Error searching on {competitor} with query '{article}': {str(e)}")
                continue

        if descriptions:
            combined_meta_description = self._combined_meta_description(descriptions)
            return combined_meta_description

    def _get_search_url(self, competitor: str, article: str) -> str | None:
        query = article.replace(' ', '+')
        if 'el-dent.ru' in competitor:
            return f"{competitor}/search/?words={query}"
        elif 'aveldent.ru' in competitor:
            return f"{competitor}/index.php?route=product/search&search={query}"
        elif 'www.nika-dent.ru' in competitor:
            return f"{competitor}/search/?q={query}"
        elif 'w-stom.ru' in competitor:
            return f"{competitor}/search/index.php?q={query}"
        # elif 'med-orto.ru' in competitor:
        #     return f"{competitor}/search/?area=site1&search_query={query}"
        else:
            return f"{competitor}/search?q={query}"

    def _find_product_page(self, soup: BeautifulSoup, competitor: str, article: str) -> str | None:
        """Пытается найти описание на странице товара)"""
        try:
            if 'el-dent.ru' in competitor:
                products = soup.find_all('div', class_='col --product-card')
                for product in products:
                    competitor_article = product.find('a', href=True, class_='product__caption').get_text(strip=True)
                    if article in competitor_article:
                        link = product.find('a', href=True, class_='product__caption')
                        if link:
                            return urljoin(competitor, link['href'])

            elif 'aveldent.ru' in competitor:
                products = soup.find_all('div', class_='product-thumb transition')
                for product in products:
                    competitor_article = product.find('meta', itemprop='mpn', content=True)['content']
                    if competitor_article == article:
                        link = product.find('a', href=True, itemprop='url')
                        if link:
                            return urljoin(competitor, link['href'])

            elif 'www.nika-dent.ru' in competitor:
                products = soup.find_all('div', class_='product-item loadmore_item')
                for product in products:
                    title = product.find('div', class_='descr-block').get_text(strip=True)
                    if article in title:
                        link = product.find('div', class_='item-manufacturer').find('a', href=True, class_='item-link')
                        if link:
                            return urljoin(competitor, link['href'])

            elif 'w-stom.ru' in competitor:
                products = soup.find_all('div', class_='productTable')
                if products:
                    title = products[0].find('div', class_='productColText')
                    if title:
                        link = title.find('a', href=True, class_='name')
                        if link:
                            return urljoin(competitor, link['href'])

        except Exception as e:
            print(f"Error in direct description check: {str(e)}")
            return None

    def _get_product_description(self, competitor: str, url: str) -> Optional[dict[str, str | None]]:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            if 'el-dent.ru' in competitor:
                meta_keywords = soup.find('meta', attrs={'name': 'keywords', 'content': True})['content']
                meta_description = soup.find('meta', attrs={'name': 'description', 'content': True})['content']
                meta_title = soup.find('meta', attrs={'property': 'og:title', 'content': True})['content']
                h2 = soup.find('h2').get_text(strip=True)
                top_description = soup.find('p', class_='vadim-p').get_text(strip=True)
                basic_description = soup.find('div', itemprop='description', class_='product-card__tabs-content order-1 active').get_text(strip=True)
                return {
                    'competitor': competitor,
                    'meta_title': meta_title if meta_title else "",
                    'meta_keywords': meta_keywords if meta_keywords else "",
                    'meta_description': meta_description if meta_description else "",
                    'h2': h2 if h2 else "",
                    'top_description': top_description if top_description else "",
                    'basic_description': basic_description if basic_description else "",
                }

            elif 'aveldent.ru' in competitor:
                meta_keywords = soup.find('meta', attrs={'name': 'keywords', 'content': True})['content']
                meta_description = soup.find('meta', attrs={'name': 'description', 'content': True})['content']
                meta_title = soup.find('meta', attrs={'property': 'og:title', 'content': True})['content']
                h2 = soup.find('h1').get_text(strip=True)
                top_description = ""
                css_selector = 'div.span12.description[itemprop="description"], p.span12.description[itemprop="description"]'
                basic_description = soup.select_one(css_selector).get_text(strip=True)

                return {
                    'competitor': competitor,
                    'meta_title': meta_title if meta_title else "",
                    'meta_keywords': meta_keywords if meta_keywords else "",
                    'meta_description': meta_description if meta_description else "",
                    'h2': h2 if h2 else "",
                    'top_description': top_description if top_description else "",
                    'basic_description': basic_description if basic_description else "",
                }
            elif 'www.nika-dent.ru' in competitor:
                meta_keywords = soup.find('meta', attrs={'name': 'keywords', 'content': True})['content']
                meta_description = soup.find('meta', attrs={'name': 'description', 'content': True})['content']
                meta_title = soup.find('meta', attrs={'property': 'og:title', 'content': True})['content']
                h2 = ""
                top_description = soup.find('div', class_='info-content').find('p').get_text(strip=True)
                basic_description = soup.find('div', class_='info-content').get_text(strip=True)

                return {
                    'competitor': competitor,
                    'meta_title': meta_title if meta_title else "",
                    'meta_keywords': meta_keywords if meta_keywords else "",
                    'meta_description': meta_description if meta_description else "",
                    'h2': h2 if h2 else "",
                    'top_description': top_description if top_description else "",
                    'basic_description': basic_description if basic_description else "",
                }

            elif 'w-stom.ru' in competitor:
                meta_keywords = soup.find('meta', attrs={'name': 'keywords', 'content': True})['content']
                meta_description = soup.find('meta', attrs={'name': 'description', 'content': True})['content']
                meta_title = soup.find('meta', attrs={'property': 'og:title', 'content': True})['content']
                h2 = ""
                top_description = ""
                basic_description = soup.find('div', id='detailText').get_text(strip=True)

                return {
                    'competitor': competitor,
                    'meta_title': meta_title if meta_title else "",
                    'meta_keywords': meta_keywords if meta_keywords else "",
                    'meta_description': meta_description if meta_description else "",
                    'h2': h2 if h2 else "",
                    'top_description': top_description if top_description else "",
                    'basic_description': basic_description if basic_description else "",
                }
            else:
                ""
        except Exception as e:
            return None


    # Объединяем описания от разных конкурентов
    def _combined_meta_description(self, descriptions) -> Optional[dict[str, str]]:
        combined_meta_title = '\n'.join([desc['meta_title'] for desc in descriptions if desc['meta_title']])
        combined_meta_keywords = '\n'.join([desc['meta_keywords'] for desc in descriptions if desc['meta_keywords']])
        combined_meta_description = '\n'.join([desc['meta_description'] for desc in descriptions if desc['meta_description']])
        combined_h2 = '\n'.join([desc['h2'] for desc in descriptions if desc['h2']])
        combined_top_description = '\n'.join([desc['top_description'] for desc in descriptions if desc['top_description']])
        combined_basic_description = '\n'.join([desc['basic_description'] for desc in descriptions if desc['basic_description']])
        return {
            'meta_title': combined_meta_title if combined_meta_title else "",
            'meta_keywords': combined_meta_keywords if combined_meta_keywords else "",
            'meta_description': combined_meta_description if combined_meta_description else "",
            'h2': combined_h2 if combined_h2 else "",
            'top_description': combined_top_description if combined_top_description else "",
            'basic_description': combined_basic_description if combined_basic_description else "",
        }


if __name__ == "__main__":
    scraper = CompetitorScraper()
    description = scraper.search_product("51202/")
    print(description)
