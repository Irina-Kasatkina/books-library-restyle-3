import json
from pathlib import Path, PurePosixPath

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

from constants import BOOKS_DETAILS_JSON_FILEPATH, BOOKS_IMAGES_DIRPATH, BOOKS_TEXTS_DIRPATH


BOOKS_COUNT_PER_PAGE = 20
BOOKS_COUNT_PER_ROW = 2
PAGES_DIRPATH = 'pages'
STATIC_DIRPATH = 'static'
TEMPLATE_FILENAME = 'template.html'


def on_reload():
    """Заносит данные о книгах в html-файлы страниц каталога."""

    template = get_template()
    books_details = get_books_details()
    add_paths_to_books_details(books_details)

    pages_dir_fullpath = Path.cwd() / PAGES_DIRPATH
    Path(pages_dir_fullpath).mkdir(parents=True, exist_ok=True)
    for page_filepath in pages_dir_fullpath.glob('*.html'):
        page_filepath.unlink()

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

    with open(BOOKS_DETAILS_JSON_FILEPATH, 'r', encoding='utf-8') as books_details_json_file:
        books_details = json.load(books_details_json_file)
    return books_details


def add_paths_to_books_details(books_details):
    """Добавляет в детали книги относительные пути к тексту и к картинке обложки."""

    parent_dir = '..'
    texts_dirpath = PurePosixPath(parent_dir, BOOKS_TEXTS_DIRPATH)
    images_dirpath = PurePosixPath(parent_dir, BOOKS_IMAGES_DIRPATH)

    for book_details in books_details:
        book_details['text_path'] = str(texts_dirpath / book_details['text_filename'])
        book_details['img_src'] = str(images_dirpath / book_details['img_filename'])


def render_html_page(current_page_number, template, books_on_page, pages_count):
    """Генерирует html-страницу из шаблона."""

    service_filepaths = get_service_filepaths()
    splitted_books_by_rows = list(chunked(books_on_page, BOOKS_COUNT_PER_ROW))
    rendered_page = template.render(
        service_filepaths=service_filepaths,
        pages_count=pages_count,
        current_page_number=current_page_number,
        splitted_books_by_rows=splitted_books_by_rows,
    )

    page_filepath = Path.cwd() / PAGES_DIRPATH / f'index{current_page_number}.html'
    with open(page_filepath, 'w', encoding="utf8") as file:
        file.write(rendered_page)


def get_service_filepaths():
    """Возвращает пути к служебным файлам: css, js, favicons."""

    parent_dir = '..'
    css_files_dir = 'css'
    favicons_dir = 'favicons'
    js_scripts_dir = 'js'
    service_filepaths = {
        'apple-touch-icon': str(PurePosixPath(parent_dir, STATIC_DIRPATH, favicons_dir, 'apple-touch-icon.png')),
        'icon': str(PurePosixPath(parent_dir, STATIC_DIRPATH, favicons_dir, 'favicon.png')),
        'manifest': str(PurePosixPath(parent_dir, STATIC_DIRPATH, favicons_dir, 'site.webmanifest')),
        'mask-icon': str(PurePosixPath(parent_dir, STATIC_DIRPATH, favicons_dir, 'safari-pinned-tab.svg')),
        'msapplication-config': str(PurePosixPath(parent_dir, STATIC_DIRPATH, favicons_dir, 'browserconfig.xml')),
        'bootstrap.min.css': str(PurePosixPath(parent_dir, STATIC_DIRPATH, css_files_dir, 'bootstrap.min.css')),
        'jquery-3.3.1.slim.min.js': str(PurePosixPath(parent_dir, STATIC_DIRPATH, js_scripts_dir,
                                                      'jquery-3.3.1.slim.min.js')),
        'popper.min.js': str(PurePosixPath(parent_dir, STATIC_DIRPATH, js_scripts_dir, 'popper.min.js')),
        'bootstrap.min.js': str(PurePosixPath(parent_dir, STATIC_DIRPATH, js_scripts_dir, 'bootstrap.min.js')),       
    }
    return service_filepaths


def main():
    on_reload()

    # Сайт смотреть на 127.0.0.1:5500
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
