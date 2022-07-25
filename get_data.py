import sqlite3
from pathlib import Path
from bs4 import BeautifulSoup as bs


def _create_table(db_name) -> None:
    db_con = sqlite3.connect(db_name)
    cur = db_con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS letters
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        letter TEXT UNIQUE
    )
    ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS words
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        letter_id INTEGER,
        word TEXT UNIQUE,
        FOREIGN KEY (letter_id) REFERENCES letters (id)
    )
    ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS paragraphs
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        letter_id INTEGER,
        word_id INTEGER,
        paragraph TEXT UNIQUE,
        FOREIGN KEY (letter_id) REFERENCES letters (id),
        FOREIGN KEY (word_id) REFERENCES words (id)
    )
    ''')
    db_con.commit()
    db_con.close()


def get_data(db_name='sqlite3.quotes') -> None:
    # Подключение к БД
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    # Создаю таблицы
    _create_table(db_name)
    # Открываю основную страницу и забираю все буквы
    with open('pages/master_page.html', 'r') as main_page:
        soup = bs(main_page.read(), 'lxml')
    h2_titles = [
        title.text for title in soup.find_all('h2', class_='h2 title')
        ]
    # Все буквы пишу в бд, таблица letters
    for letter in h2_titles:
        cur.execute('INSERT OR IGNORE INTO letters VALUES(NULL, ?)', (letter))
    # Получаю все файлы html и захожу в цикл
    for page in Path('pages').rglob('*.html'):
        if 'master' not in str(page):
            with open(str(page), 'r') as f:
                soup = bs(f.read(), 'lxml')
            title = soup.find('h1', class_='text-center').text.strip()
            paragraphs = [
                paragraph.text for paragraph in soup.find_all('p', class_='txt')
                ]
            quotes = {
                title: [
                    paragraph.replace('\u2009', '') for paragraph in paragraphs
                    ]
                }
            # Захожу в цикл со словами и текстами
            for word, paragraphs in quotes.items():
                # Получаю id первой буквы слова из бд и записываю слово в бд
                cur.execute('SELECT id FROM letters WHERE letter = ?', word[0])
                id_letter = cur.fetchone()[0]
                cur.execute(
                    'INSERT OR IGNORE INTO words VALUES(NULL, ?, ?)',
                    (id_letter, word)
                    )
                print(f'[+] - [WORD] - {word}')
                # Получаю id слова из бд и записываю текст в бд
                for paragraph in paragraphs:
                    cur.execute('SELECT id FROM words WHERE word = ?', (word,))
                    id_word = cur.fetchone()[0]
                    cur.execute(
                        'INSERT OR IGNORE INTO paragraphs VALUES(NULL, ?, ?, ?)',
                        (id_letter, id_word, paragraph))
    con.commit()
    con.close()


if __name__ == '__main__':
    db_name = 'sqlite3.quotes'
    get_data(db_name)
