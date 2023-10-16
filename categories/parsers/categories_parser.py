import requests
from bs4 import BeautifulSoup


URL = 'https://naviline.ru/electronics'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0',
    'accept': '*/*',
}


def get_soup(url=URL):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def get_categories():
    soup = get_soup()
    categories_container = soup.find('ul', id='property_category')
    li_categories = categories_container.find_all('li')

    categories_list = ['Навигаторы', 'Видеокамеры', 'Аксессуары', 'Эхолоты', 'Электромоторы', 'Весы']
    for li in li_categories:
        text = li.find('label').get_text(strip=True)
        if 'навигатор' not in text.lower() and 'радар' not in text.lower():
            if 'камеры' not in text.lower():
                if 'видео' not in text.lower():
                    if not text.startswith('Garmin'):
                        if 'аксессуар' not in text.lower():
                            if 'картплоттер' not in text.lower():
                                if 'эхолот' not in text.lower():
                                    if 'электромотор' not in text.lower():
                                        if 'радио' not in text.lower():
                                            if 'креплени' not in text.lower():
                                                if 'кабел' not in text.lower():
                                                    if 'чехл' not in text.lower():
                                                        if 'электрони' not in text.lower():
                                                            categories_list.append(text)

    return categories_list


if __name__ == '__main__':
    print(get_categories())
