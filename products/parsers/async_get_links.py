import asyncio
import aiohttp


HOST = 'https://naviline.ru'
URL = 'https://naviline.ru/electronics'
MAX_SM = 50
RESULT = []
total_checked = 0


async def get_one(url, session):
    global total_checked

    async with session.get(url) as response:
        # Ожидаем ответа и блокируем таск
        page_content = await response.text()
        # Получаем информацию об игре и сохраняем в лист
        page_content = page_content + f'<a id="product-original-link">{url}</a>'
        RESULT.append(page_content)
        total_checked += 1


async def bound_fetch(sm, url, session):
    try:
        async with sm:
            await get_one(url, session)
    except Exception as e:
        pass


async def run(urls, len_sm):
    tasks = []

    sm = asyncio.Semaphore(len_sm)
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0"}
    # Опять же оставляем User-Agent, чтобы не получить ошибку от сайта
    async with aiohttp.ClientSession(headers=headers) as session:
        for url in urls:
            # собираем таски и добавляем в лист для дальнейшего ожидания.
            task = asyncio.ensure_future(bound_fetch(sm, url, session))
            tasks.append(task)
        # ожидаем завершения всех наших задач
        await asyncio.gather(*tasks)


def async_get_links(urls):
    # Запускаем наш парсер
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(urls, MAX_SM))
    loop.run_until_complete(future)


def get_urls(pages=65):
    urls = []
    for i in range(1, pages + 1):
        url = URL + f'?page={i}'
        urls.append(url)
    return urls


if __name__ == '__main__':
    urls = get_urls()
    async_get_links(urls)