# Dental First Product Description Generator

## Описание проекта

Автоматизация создания уникальных и SEO-оптимизированных описаний товаров для сайта [Dental First](https://dental-first.ru). Скрипты собирают описания с сайтов конкурентов, генерируют на их основе новые тексты с помощью нейросети, оформляют их согласно правилам верстки из Figma и формируют мета-информацию (Title, Description, Keywords). Итоговые данные сохраняются в Google Таблице для последующего импорта на сайт.

---

## Основные задачи

1. Сбор описаний товаров с сайтов конкурентов по артикулам.
2. Генерация уникальных описаний через нейросеть.
3. Формирование мета-тегов для SEO.
4. Сохранение результатов в Google Sheets.

---

## Используемые сайты конкурентов

- https://el-dent.ru
- https://www.nika-dent.ru
- https://aveldent.ru
  
---

## Технологии и модули

- Python 3.x
- `CompetitorScraper` — сбор данных с конкурентов
- `DescriptionGenerator` — генерация описаний через нейросеть
- `DentalFirstParser` — парсинг товаров с сайта Dental First
- `GoogleSheetsHandler` — работа с Google Sheets API
- Измерение времени выполнения для оценки производительности

---

## Структура проекта

- `main.py` — основной скрипт запуска
- `scraper.py` — сбор описаний конкурентов
- `generator.py` — генерация уникальных текстов
- `parser.py` — парсинг товаров Dental First
- `google_sheets.py` — взаимодействие с Google Sheets
- `config.py` — конфигурация с ключами и параметрами

---

## Инструкция по запуску

1. Установите зависимости.
2. Настройте `config.py`:
   - `client_secret` — ключ для нейросети
   - `google_creds_file` — учетные данные Google API
   - `spreadsheet_id` — ID Google Таблицы
   - `dental_first_url` — URL раздела товаров
3. Запустите:

4. По завершении в консоли будет время работы и количество обработанных товаров.
5. Результаты доступны в Google Таблице.

---

## Формат выходных данных в Google Sheets

| Колонка            | Описание                     |
|--------------------|------------------------------|
| URL                | Ссылка на товар Dental First |
| DF Номенклатура    | Название товара              |
| Бренд              | Производитель                |
| Страна             | Страна производства          |
| DF Артикул         | Артикул товара               |
| DF META TITLE      | Мета-заголовок               |
| DF KEYWORDS        | Ключевые слова               |
| DF Meta Description| Мета-описание                |
| DF <h2>            | Заголовок второго уровня     |
| DF верхнее описание| Верхнее описание             |
| DF основное описание| Основное описание            |
| DF ID              | Внутренний ID товара         |
| SIM                | Дополнительное поле          |

---

## Особенности

- Генерируемые описания требуют проверки и возможной доработки.
- Время выполнения выводится для контроля производительности.

---

