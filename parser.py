from typing import List, Dict, Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import config


class DentalFirstParser:
    def __init__(self):

        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; Bot/1.0)'})

    def parse_products(self, url: str) -> List[Dict[str, str]]:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            product_information = []
            product_blocks = soup.find('div', class_='set-row block-card ajaxelem')

            product_cards = product_blocks.find_all('div', class_='set-card block')

            for block in product_cards:
                try:
                    # Извлечение информации о продукте
                    link_elem = block.find('a', class_='di_b c_b', href=True)
                    link = urljoin(url, link_elem['href']) if link_elem else None
                    if link:
                        product_info = self._get_product_info(link)
                        if product_info:
                            product_information.append({
                                'url': product_info['url'],
                                'nomenclature': product_info['nomenclature'],
                                'brand': product_info['brand'],
                                'country': product_info['country'],
                                'article_number': product_info['article_number'],
                                'meta_title': product_info['meta_title'],
                                'meta_keywords': product_info['meta_keywords'],
                                'meta_description': product_info['meta_description'],
                                'h2': "",
                                'top_description': "",
                                'basic_description': product_info['description'],
                                'id': product_info['id'],
                                'sim': product_info['sim'],
                            })
                except Exception as e:
                    print(f"Error parsing product block: {str(e)}")
                    continue

            return product_information

        except Exception as e:
            print(f"Error parsing Dental First catalog: {str(e)}")
            return []

    def _get_product_info(self, url: str) -> Optional[Dict[str, str]]:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_url_tag = soup.find('meta', property='og:url', content=True)['content']
            meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords', 'content': True})['content']
            meta_description_tag = soup.find('meta', property='og:description', content=True)['content']
            meta_description_clean_text = ' '.join(line.strip() for line in meta_description_tag.splitlines() if line.strip())
            title_tag = soup.find('h1', class_='main-slider__title', itemprop='name')
            desc_tag = soup.find('div', class_='tab__text', id='descr-text')
            brand_tag = soup.find('span', itemprop='brand').find('a')
            meta_title_tag = soup.find('meta', property='og:title', content=True)['content']
            country_tag = brand_tag.find_next('span')
            article_number_tag = soup.find('span', class_='pass_aticul')
            id_tag = soup.find('span', class_='pass_id')
            product_code_tag = soup.find('span', class_='pass_kodtovara')

            url = meta_url_tag if meta_url_tag else None
            nomenclature = title_tag.get_text(strip=True) if title_tag else None
            brand = brand_tag.get_text(strip=True) if brand_tag else None
            country = self.get_value_after_label(country_tag, "Страна:") if country_tag else None
            article_number = self.get_value_after_label(article_number_tag, "Артикул:") if article_number_tag else None
            meta_title = meta_title_tag if meta_title_tag else None
            meta_keywords = meta_keywords_tag if meta_keywords_tag else None
            meta_description = meta_description_clean_text if meta_description_clean_text else None
            id = self.get_value_after_label(id_tag, "ID:") if id_tag else None
            product_code = self.get_value_after_label(product_code_tag, "Код товара:") if product_code_tag else None
            description = desc_tag.get_text(' ', strip=True) if desc_tag else None

            return {
                'url': url,
                'nomenclature': nomenclature,
                'brand': brand,
                'country': country,
                'article_number': article_number,
                'meta_title': meta_title,
                'meta_keywords': meta_keywords,
                'meta_description': meta_description,
                'description': description,
                'id': id,
                'sim': product_code,
            }
        except Exception as e:
            print(f"Error getting description from {url}: {str(e)}")
            return None

    def get_value_after_label(self, span, label):
        if span:
            text = span.get_text(separator=' ', strip=True)
            if text.startswith(label):
                return text[len(label):].strip()
        return None


if __name__ == "__main__":
    parser = DentalFirstParser()
    products = parser.parse_products(config.CONFIG['dental_first_url'])
    print(products)
