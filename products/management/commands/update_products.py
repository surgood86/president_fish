import requests

from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from django.core.files.base import ContentFile

from products.models import (
    Product,
    ProductProperties,
    ProductImages,
    ProductEquipments,
    ProductDescriptions,
)

from categories.parsers.manufacturers_parser import get_manufacturers
from products.parsers import async_parse

from categories.models import Category, Subcategory

from services.categories_set_main_images import create_categories_and_set_them_main_images
from services.products_services import get_eng_translated_text

from transliterate import translit
class Command(BaseCommand):
    help = 'Parse data from site and save in db'
    NEED_HOST = 'https://naviline.ru'
# Метод add_arguments () определяет аргумент командной строки num_products, который указывает количество
# продуктов, которые необходимо спарсить.
    def add_arguments(self, parser):
        parser.add_argument('num_products', type=str, help='total products for parsing')

    def get_subcategory(self, data):
        category_dict = {
            'навигатор': 'Навигаторы',
            'радар': 'Навигаторы',
            'видео': 'Видеокамеры',
            'камер': 'Видеокамеры',
            'Garmin': 'Часы Garmin',
            'аксессуар': 'Аксессуары',
            'картплоттер': 'Эхолоты',
            'эхолот': 'Эхолоты',
            'электромотор': 'Электромоторы',
            'радио': 'Рации',
            'креплени': 'Аксессуары',
            'кабел': 'Аксессуары',
            'чехл': 'Аксессуары'
        }
        subcategory = Subcategory(eng_title=get_eng_translated_text(data['category']), title=data['category'])
        for keyword, title in category_dict.items():
            if keyword in data['category'].lower():
                category = Category.objects.get(title=title)
                subcategory.category = category
                break
        subcategory.save()
        return subcategory
# Методы
    # get_correct_manufacturer(), get_saved_product(), save_charactericstics(),
    # save_equipments(), save_descriptions() и save_images()
    # являются вспомогательными и используются для сохранения полученных данных в базе данных.
    def get_correct_manufacturer(self, data):
        manufacturers_list = get_manufacturers()
        title = data['title']
        category = data['category']
        manufacturer = ''
        for m in manufacturers_list:
            if m.lower() != 'gp':
                if m.lower() in title.lower() or m.lower() in category.lower():
                    manufacturer = m
        if not manufacturer:
            if 'gp' in title.lower() or 'gp' in category.lower():
                manufacturer = 'GP'
        if not manufacturer:
            manufacturer = 'Прочие'
        return manufacturer

    def get_saved_product(self, data):
        price = int(data['price'].split()[0])

        if len(data['main_description']) == 1:
            main_description = data['main_description'][0]
        elif len(data['main_description']) > 1:
            main_description = data['main_description'][0]
            for i in range(1, len(data['main_description'])):
                main_description += ' ' + data['main_description'][i]
        else:
            main_description = ''


        product = Product(
            eng_title=get_eng_translated_text(data['title']), # Функция get_saved_product напрямую передаёт данные через data!!!
            title=data['title'],
            price=price,
            original_link=data['original_link'],
            main_description=main_description,
            manufacturer=self.get_correct_manufacturer(data)
        )


        if Category.objects.filter(title=data['category']):

            category = Category.objects.get(title=data['category'])

            product.category = category

        else:
            if Subcategory.objects.filter(title=data['category']):

                subcategory = Subcategory.objects.get(title=data['category'])
                product.subcategory = subcategory
                product.category = subcategory.category
            else:

                subcategory = self.get_subcategory(data)
                product.subcategory = subcategory
                product.category = subcategory.category

        product.save()

        return product

    def save_charactericstics(self, data, product):
        for ch in data['characteristics']:
            product_property = ProductProperties(title=ch, text=data['characteristics'][ch])
            product_property.product = product
            product_property.save()

    def save_equipments(self, data, product):
        for e in data['equipments']:
            product_equipment = ProductEquipments(title=e, text=data['equipments'][e])
            product_equipment.product = product
            product_equipment.save()

    def save_descriptions(self, data, product):
        for d in data['descriptions']:
            product_description = ProductDescriptions()
            if d.startswith('title'):
                product_description.title = d[7:]
            elif d.startswith('text'):
                product_description.text = d[6:]
            elif d.startswith('img'):
                img_url = d[9:]
                if not img_url.startswith('http'):
                    img_url = self.NEED_HOST + img_url
                product_description.some_link = img_url
            elif d.startswith('iframe'):
                iframe_url = d[12:]
                if not iframe_url.startswith('http'):
                    iframe_url = self.NEED_HOST + iframe_url
                product_description.some_link = iframe_url
            product_description.product = product
            product_description.save()

    def save_images(self, data, product): # тут всё ок
        images_urls = data['images_urls']
        if images_urls:
            for i in data['images_urls']:
                image_name = i.split('/')[-1]
                image_r = requests.get(i, stream=True)
                image_bytes = ContentFile(image_r.content)
                product_image = ProductImages()
                product_title = translit(product.title[:5], 'ru', reversed=True)
                product_image.image = ImageFile(image_bytes, name=(str(product_title) + '_' + image_name))
                #product_image.image = ImageFile(image_bytes, name=(str(product.title[:5]) + '_' + image_name))
                product_image.product = product
                product_image.save()
# Метод handle() является основным методом команды, который использует все
    # вышеперечисленные вспомогательные методы для сохранения данных в базе данных.
    def handle(self, *args, **kwargs):
        create_categories_and_set_them_main_images()  # """Создает категории и задает им main_image поля"""

        num_products = kwargs['num_products']

        all_data = async_parse.get_products_data(num_products=num_products)  # передаём всю спарсинную инфу в all_data

        for data in all_data: # тут всё ок
            product = self.get_saved_product(data)
            self.save_charactericstics(data, product)
            self.save_equipments(data, product)
            self.save_descriptions(data, product)
            self.save_images(data, product)
