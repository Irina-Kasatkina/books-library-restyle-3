import json
from pathlib import Path, PurePosixPath

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


BOOKS_COUNT_PER_PAGE = 20
BOOKS_COUNT_PER_ROW = 2
BOOKS_DETAILS_JSON_FILENAME = 'books_details.json'
IMAGES_FOLDER = 'images'
PAGES_FOLDER = 'pages'
TEMPLATE_FILENAME = 'template.html'
TEXTS_FOLDER = 'books'


def on_reload():
    """Заносит данные о книгах в html-файлы страниц каталога."""

    template = get_template()
    books_details = get_books_details()
    add_paths_to_books_details(books_details)

    pages_folder_fullpath = Path.cwd() / PAGES_FOLDER
    Path(pages_folder_fullpath).mkdir(parents=True, exist_ok=True)

    splitted_books_by_pages = list(chunked(books_details, BOOKS_COUNT_PER_PAGE))
    pages_count = len(splitted_books_by_pages)
    for current_page_number, books_on_page in enumerate(splitted_books_by_pages, 1):
        render_html_page(current_page_number, template, books_on_page, pages_count)


def get_template():
    """Создаёт из html-файла шаблон для создания html-файлов страниц каталога."""

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template(TEMPLATE_FILENAME)
    return template


def get_books_details():
    """Читает из json-файла информацию о загруженных книгах."""

    with open(BOOKS_DETAILS_JSON_FILENAME, 'r', encoding='utf-8') as books_details_json_file:
        books_details_json = books_details_json_file.read()

    books_details = json.loads(books_details_json)
    return books_details


def add_paths_to_books_details(books_details):
    """Добавляет в детали книги относительные пути к тексту и к картинке обложки."""

    parent_folder = '..'
    texts_folder_path = PurePosixPath(parent_folder, TEXTS_FOLDER)
    images_folder_path = PurePosixPath(parent_folder, IMAGES_FOLDER)

    for book_details in books_details:
        book_details['text_path'] = str(texts_folder_path / book_details['text_filename'])
        book_details['img_src'] = str(images_folder_path / book_details['img_filename'])


def render_html_page(current_page_number, template, books_on_page, pages_count):
    """Генерирует html-страницу из шаблона."""

    splitted_books_by_rows = list(chunked(books_on_page, BOOKS_COUNT_PER_ROW))
    rendered_page = template.render(
        pages_count=pages_count,
        current_page_number=current_page_number,
        splitted_books_by_rows=splitted_books_by_rows,
    )

    page_filepath = Path.cwd() / PAGES_FOLDER  / f'index{current_page_number}.html'
    with open(page_filepath, 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    on_reload()

    # Сайт смотреть на 127.0.0.1:5500
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
