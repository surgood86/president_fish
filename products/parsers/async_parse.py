import multiprocessing as mp
import sys

from bs4 import BeautifulSoup
import products.parsers.products_parser as pp
import products.parsers.async_get_links as agl


HOST = 'https://naviline.ru'
NUM_PROCESSES = mp.cpu_count()
sys.setrecursionlimit(50000)

def get_products_on_page(response):
    soup = BeautifulSoup(response, 'html.parser')
    products_list = []
    products_container = soup.find('div', class_='product-list infinite-list')
    products = products_container.find_all('li', class_='list-item product-card-short')

    for product in products:
        products_list.append({
            'link': HOST + product.find('a', class_='product-name').get('href'),
        })
    return products_list


def pools_parse(num_pools=NUM_PROCESSES):
    urls = agl.get_urls()
    agl.async_get_links(urls)

    with mp.Pool(num_pools) as p:
        data = p.map(get_products_on_page, agl.RESULT)
    all_data = []
    for d in data:
        all_data.extend(d)
    return all_data


def get_products_data(num_pools=NUM_PROCESSES, num_products='all'):
    pages_data = pools_parse(num_pools)

    products_urls = []
    for d in pages_data:
        products_urls.append(d['link'])
    products_urls = list(set(products_urls))

    agl.total_checked = 0
    agl.RESULT = []
    if num_products != 'all':
        agl.async_get_links(products_urls[:int(num_products)])
    else:
        agl.async_get_links(products_urls)

    with mp.Pool(num_pools) as p:
        data = p.map(pp.get_data_from_page, agl.RESULT)
    return data


if __name__ == '__main__':
    get_products_data(1)