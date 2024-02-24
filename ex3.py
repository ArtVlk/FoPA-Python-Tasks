#!/usr/bin/env python3
import sys
import re
from urllib.parse import quote, unquote
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def get_content(name):
    """
    Функция возвращает содержимое вики-страницы name из русской Википедии.
    В случае ошибки загрузки или отсутствия страницы возвращается None.
    """
    try:
        page = urlopen('https://ru.wikipedia.org/wiki/' + quote(name))
        page_content = page.read().decode('utf-8', errors='ignore')
        page.close()
        return page_content
    except (URLError, HTTPError):
        return None


def extract_content(page):
    """
    Функция принимает на вход содержимое страницы и возвращает 2-элементный
    tuple, первый элемент которого — номер позиции, с которой начинается
    содержимое статьи, второй элемент — номер позиции, на котором заканчивается
    содержимое статьи.
    Если содержимое отсутствует, возвращается (0, 0).
    """
    start_tag = '<div class="mw-content-ltr mw-parser-output"'
    end_tag = '<!--esi'
    start = page.find(start_tag)
    if start != -1:
        end = page.find(end_tag, start)
        if end != -1:
            return start, end
    return 0, 0


def extract_links(page, begin, end):
    """
    Функция принимает на вход содержимое страницы и начало и конец интервала,
    задающего позицию содержимого статьи на странице и возвращает все имеющиеся
    ссылки на другие вики-страницы без повторений и с учётом регистра.
    """
    pattern = r'<a\s+href=["\']/wiki/([\w%]*?)["\']'

    page = page[begin:end]
    links = set()
    for match in re.finditer(pattern, page, re.IGNORECASE):
        link = unquote(match.group(1))
        links.add(link)

    return links


def find_chain(start, finish):
    """
    Функция принимает на вход название начальной и конечной статьи и возвращает
    список переходов, позволяющий добраться из начальной статьи в конечную.
    Первым элементом результата должен быть start, последним — finish.
    Если построить переходы невозможно, возвращается None.
    """
    if start != finish:
        route = [[start]]
        colored = set()
        while route:
            way = route.pop(0)
            node = way[-1]
            page = get_content(node)
            if not page:
                continue
            content = extract_content(page)
            if content == (0, 0):
                continue
            if node in colored:
                continue
            colored.add(node)
            links = extract_links(page, content[0], content[1])
            for link in links:
                new_way = list(way)
                new_way.append(link)
                if link == finish:
                    return new_way
                route.append(new_way)
    else:
        return [start]


def main():
    if len(sys.argv) == 2:
        finish = "Философия"
        start = sys.argv[1]
        path = find_chain(start, finish)
        if path:
            print(path)


if __name__ == '__main__':
    main()
