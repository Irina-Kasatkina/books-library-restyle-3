import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    """Заносит в index.html данные о книгах из books_details.json."""

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    with open('books_details.json', 'r', encoding='utf-8') as books_json_file:
        books_json = books_json_file.read()

    books = json.loads(books_json)
    chunked_books = list(chunked(books, 2))

    template = env.get_template('template.html')
    rendered_page = template.render(chunked_books=chunked_books)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    on_reload()

    # Сайт смотреть на 127.0.0.1:5500
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
