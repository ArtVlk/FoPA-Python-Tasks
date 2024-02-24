import argparse
import os
import pathlib
import re
import signal
import sys
import urllib.request
import threading
from typing import Optional
from urllib.error import URLError, HTTPError

URL = "https://habr.com"
IMAGES = re.compile(r'<img src=\"')


def load_content(url: str) -> Optional[bytes]:
    try:
        return urllib.request.urlopen(url, timeout=8).read()
    except (HTTPError, URLError):
        return None


def extract_images(article_link):
    data = load_content(f"{URL}{article_link}").decode("utf-8")

    if data is not None:
        start = data.find(r'<div id="post-content-body">')
        end = data.find(r'</div>', start)
        inner_content = data[start:end]
        all_images = IMAGES.finditer(inner_content)
        images = []
        for image in all_images:
            start_ref = image.end()
            end_ref = inner_content.find(r'"', start_ref)
            images.append(inner_content[start_ref:end_ref])
        return images

    else:
        return


def sanitize_folder_name(den):
    chars = r'\|/<>*?:'
    for char in chars:
        den = den.replace(char, '_')
    return den


def download_articles_images(title, link):
    images = extract_images(link)
    if images:
        title = sanitize_folder_name(title)
        os.makedirs(title, exist_ok=True)
        for ref in images:
            content = load_content(ref)
            if content is not None:
                name = ref[ref.rfind('/') + 1:]
                path = os.path.join(title, name)
                with open(path, "wb") as img:
                    img.write(content)
            else:
                return

    else:
        return


class Shutdown:
    def __init__(self, thread):
        self.threads = thread
        self.event = threading.Event()
        signal.signal(signal.SIGINT, self.exit_graceful)
        signal.signal(signal.SIGTERM, self.exit_graceful)

    def exit_graceful(self, signum, frame):
        self.event.set()
        self.wait_threads(self.threads)

    @staticmethod
    def wait_threads(threads):
        while threads:
            threads.pop().join()


def run_scraper(threads_num: int, articles_num: int, output_dir: pathlib.Path) -> None:
    thread_list = []
    gs = Shutdown(thread_list)

    if not (os.path.exists(output_dir)):
        os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)

    content = load_content(URL).decode("utf-8")
    headers = re.compile(r'<h2.*<\/h2>')
    name = re.compile(r'<span>(.*)<\/span>')
    href = re.compile(r'<a href=\"(.*)\"')
    article_list = re.findall(headers, content)[:articles_num]

    for link in article_list:
        if gs.event.is_set():
            break

        while len(thread_list) >= threads_num:
            for thread in thread_list:
                if not thread.is_alive():
                    thread_list.remove(thread)
                    break

        article_title = re.search(name, link).group(1)
        article_link = re.search(href, link).group(1)
        article_link = article_link[:article_link.find(r'"', 1)]
        thread = threading.Thread(
            target=download_articles_images(article_title, article_link))
        thread_list.append(thread)
        thread.start()
    Shutdown.wait_threads(thread_list)


def main():
    name = os.path.basename(sys.argv[0])
    par = argparse.ArgumentParser(
        usage=f'{name} [ARTICLES_NUMBER] THREAD_NUMBER OUT_DIRECTORY',
        description='Habr parser',
    )
    par.add_argument(
        '-n',
        type=int,
        default=25,
        help='Number of articles to be processed',
    )
    par.add_argument(
        'threads',
        type=int,
        help='Number of threads to be run',
    )
    par.add_argument(
        'out_dir',
        type=pathlib.Path,
        help='Directory to download habr images',
    )

    args = par.parse_args()
    run_scraper(args.threads, args.n, args.out_dir)


if __name__ == '__main__':
    main()
