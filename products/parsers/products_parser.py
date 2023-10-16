# Request и Response. Все взаимодействия между клиентом (в нашем случае консолью Python) и
# API разделены на запрос (request) и ответ (response):
# request содержит данные запроса API: базовый URL, конечную точку, используемый метод, заголовки и т. д.
# response содержит соответствующие данные, возвращаемые сервером, в том числе контент, код состояния и заголовки.
from bs4 import BeautifulSoup

HOST = 'https://naviline.ru/electronics'

HEADERS = {
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Chrome/99.0.4844.84 Gecko/20100101 Firefox/87.0',
    'accept': '*/*',
}


def get_product_characteristics(soup):
    data = dict()
    characteristics_container = soup.find('div', id='properties')
    if not characteristics_container:
        data['characteristics'] = []
        return data
    characteristics = characteristics_container.find_all('dl')
    characteristics_dict = dict()
    for characteristic in characteristics:
        characteristics_dict[characteristic.find('dt').get_text(strip=True)] = \
            characteristic.find('dd').get_text(strip=True)
    data['characteristics'] = characteristics_dict
    return data


def get_product_equipments(soup):
    data = dict()
    equipments_container = soup.find('div', id='equipment')
    if not equipments_container:
        data['equipments'] = []
        return data
    equipments = equipments_container.find_all('dl')
    equipments_dict = dict()
    for equipment in equipments:
        equipments_dict[equipment.find('dt').get_text(strip=True)] = equipment.find('dd').get_text(strip=True)
    data['equipments'] = equipments_dict
    return data


def get_product_descriptions(soup):
    descriptions_container = soup.find('div', id='description')
    texts_list = []
    contents = descriptions_container.contents
    for content in contents:
        if content.name == 'h3':
            if content.string:
                title = content.string
                title = title.replace(u'\xa0', u' ')
                texts_list.append('title: ' + title)
        elif content.name == 'p':
            if content.img:
                texts_list.append('img_url: ' + content.img.get('src'))
            elif content.iframe:
                texts_list.append('iframe_url: ' + content.iframe.get('src'))
            elif content.string:
                text = content.string
                text = text.replace(u'\xa0', u' ')
                texts_list.append('text: ' + text)
        elif content.name == 'ul':
            li_containers = content.find_all('li')
            if li_containers:
                for li in li_containers:
                    if li.string:
                        text = li.string
                        text = text.replace(u'\xa0', u' ')
                        texts_list.append('text: ' + text)

    return texts_list


def get_product_images(soup):
    images_container = soup.find('div', id='productImages')
    images = images_container.find_all('li')
    if not images:
        return []
    images_urls = []
    for image in images:
        add_image = image.find('img').get('src')
        if add_image.startswith('http'):
            images_urls.append(add_image)
        else:
            images_urls.append(HOST + add_image)
    return images_urls


def get_main_description(soup):
    data = dict()
    description_container = soup.find('div', class_='product-description-short')
    if not description_container:
        data['main_description'] = []
        return data
    texts = description_container.find_all('p')
    all_text = []
    for text in texts:
        description = text.get_text(strip=True)
        description = description.replace(u'\xa0', u' ')
        all_text.append(description)
    data['main_description'] = all_text
    return data


#def get_accessories(soup):
#    data = dict()
#    accessories_container = soup.find('div', class_='product-list infinite-list')
#    if not accessories_container:
#        data['accessories'] = []
#        return data
#    accessories = accessories_container.find_all('li')
#    accessories_list = []
#    for accessory in accessories:
#        accessories_list.append({
#            'title': accessory.find('a', class_='product-name').get_text(strip=True),
#            'link': HOST + accessory.find('a', class_='product-name').get('href'),
#        })
#    data['accessories'] = accessories_list
#    return data

def get_title(soup):
    title = soup.find('h1')
    if title is not None:
        return title.text
    else:
        return ''


def get_price(soup):
    price = soup.find('div', class_='price').get_text(strip=True)
    price = price.replace(u'\xa0', u'')
    price = price[:-3]
    return price


def get_category(soup):
    category_container = soup.find('ol', class_='breadcrumb')
    li_cont = category_container.find_all('li')
    category = li_cont[-2].find('a').get_text(strip=True)
    # category = get_text(li_cont[-2].find('a'))
    return category


def get_data_from_page(response_text):
    data = dict()
    soup = BeautifulSoup(response_text, 'html.parser')
    data['title'] = get_title(soup)
    data['price'] = get_price(soup)
    data['original_link'] = soup.find('a', id='product-original-link').get_text(strip=True)
    data['category'] = get_category(soup)
    data['main_description'] = get_main_description(soup)['main_description']
    data['characteristics'] = get_product_characteristics(soup)['characteristics']
    data['equipments'] = get_product_equipments(soup)['equipments']
    data['images_urls'] = get_product_images(soup)
    #data['accessories'] = get_accessories(soup)['accessories']
    data['descriptions'] = get_product_descriptions(soup)
    return data


if __name__ == '__main__':
    print('Nothing is called')
