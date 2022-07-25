import requests
from pathlib import Path
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent


def get_master_page(url=None) -> bool:
    if url is not None:
        response = requests.get(url).text
        with open('pages/master_page.html', 'w') as file:
            file.write(response)
        return True
    return False


def _create_folder() -> None:
    Path('pages').mkdir(exist_ok=True)


def get_all_pages():
    # url главной страницы
    url = 'https://azbyka.ru/otechnik/Biblia/tsitaty-iz-biblii'
    # Создаю папку для страниц
    _create_folder()
    # Получаю главную траницу и если все ок, то продолжаю
    if get_master_page(url):
        pages = []
        user_agent = UserAgent()
        # Открываю сохраненную главную страницу
        with open('pages/master_page.html', 'r') as f:
            master_page = f.read()
        soup_master_page = bs(master_page, 'lxml')
        # Получаю все теги a
        tags_a = soup_master_page.find_all('a')
        # Итерируюсь по всем тегам a и фильтрую результат
        for a in tags_a:
            try:
                if not a['href'].startswith('.'):
                    continue
                else:
                    pages.append(url + a['href'].split('.')[-1])
            except KeyError:
                pass
        # Итерируюсь по полученным ссылкам и загружаю страницы
        for page in pages:
            response = requests.get(
                page, headers={'User-Agent': user_agent.random}
                ).text
            with open(f'pages/{page.split("/")[-1]}.html', 'w') as html:
                html.write(response)
            print(f'[+] [{page.split("/")[-1]} of {len(pages)}] {page}')


if __name__ == '__main__':
    get_all_pages()
