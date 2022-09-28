import argparse
import json
import logging
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

from parse_tululu_books import check_for_redirect, download_books


logger = logging.getLogger(__file__)

BOOKS_DETAILS_JSON_FILENAME = 'books_details.json'
QUERY_TIMEOUT = 30


def create_parser():
    """Создаёт парсер параметров командной строки."""

    parser = argparse.ArgumentParser(
            description='Скачивает с сайта tululu.org тексты книг в подпапку books, '
                        'а обложки книг в подпапку images '
                        'для книг из каталога "Научная фантастика".'
    )
    parser.add_argument('-s', '--start_page', type=int, default=1,
                        help='номер страницы каталога "Научная фантастика", '
                             'начиная с которой происходит скачивание')
    parser.add_argument('-e', '--end_page', type=int, default=0,
                        help='номер страницы каталога "Научная фантастика", '
                             'заканчивая которой происходит скачивание')
    return parser


def get_books_urls(start_page, end_page):
    """Получает полные url книг из указанного диапазона страниц каталога фантастики."""

    real_end_page = get_real_endpage()
    if start_page > real_end_page:
        logger.warning(
            f'Запрошены страницы {start_page}-{end_page}, '
            f'но в каталоге всего {real_end_page} страниц.'
        )
        return []

    end_page = min(end_page, real_end_page)
    books_urls = []
    for page_number in range(start_page, end_page+1):
        category_page_url = f'https://tululu.org/l55/{page_number}/'
        page_books_urls = get_parsed_category_page(category_page_url)['books_urls']
        books_urls.extend([urljoin(category_page_url, book_url) for book_url in page_books_urls])
        page_number += 1

    return books_urls


def get_parsed_category_page(category_page_url):
    """Получает полные url книг из указанной страницы каталога фантастики."""

    while True:
        try:
            response = requests.get(category_page_url)
            response.raise_for_status()
            check_for_redirect(response)
            return parse_category_page(response.content)
        except requests.HTTPError:
            logger.warning(
                'Возникла ошибка HTTPError. '
                f'Возможно, страница каталога {category_page_url} отсутствует на сайте.'
            )
        except requests.exceptions.ConnectionError:
            logger.warning(
                f'При загрузке страницы {category_page_url} '
                'возникла ошибка соединения с сайтом.'
            )
            time.sleep(QUERY_TIMEOUT)
            continue
        break
    return None


def get_real_endpage():
    """Получает с сайта реальное количество страниц каталога."""

    page_number = 1
    category_page_url = f'https://tululu.org/l55/{page_number}/'
    return get_parsed_category_page(category_page_url)['pages_count']


def parse_category_page(response_content):
    """Парсит контент страницы категории книг с сайта tululu.org."""

    soup = BeautifulSoup(response_content, 'lxml')

    books_tags = soup.select('.d_book')
    books_urls = [book_tag.select_one('a')['href'] for book_tag in books_tags]

    pages_count = int(soup.select('a.npage')[-1].text)

    return {'books_urls': books_urls, 'pages_count': pages_count}


def main():
    logger.setLevel(logging.INFO)
    logging.basicConfig(filename='library-restyle.log', filemode='w')

    parser = create_parser()
    args = parser.parse_args()

    if not (start_page := args.start_page):
        start_page = 1

    if end_page := args.end_page:
        if start_page > end_page:
            start_page, end_page = end_page, start_page
    else:
        end_page = start_page

    books_urls = get_books_urls(start_page, end_page)
    if books_urls:
        books_details = download_books(books_urls)

        if books_details:
            with open(BOOKS_DETAILS_JSON_FILENAME, 'w', encoding='utf8') as json_file:
                json.dump(books_details, json_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
