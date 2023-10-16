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


def get_manufacturers():
    soup = get_soup()
    manufacturers_container = soup.find('ul', id='property_vendor')
    li_categories = manufacturers_container.find_all('li')

    manufacturer_list = []
    for li in li_categories:
        text = li.find('label').get_text(strip=True)
        text = ''.join([i for i in text if not i.isdigit()])
        manufacturer_list.append(text)

    return manufacturer_list


if __name__ == '__main__':
    print(get_manufacturers())
