from services.products_services import get_eng_translated_text

from categories.models import Category
from categories.parsers.categories_parser import get_categories


def create_categories_and_set_them_main_images() -> None:
    """Создает категории и задает им main_image поля"""

    categories_titles = get_categories()
    for title in categories_titles:
        eng_title = get_eng_translated_text(title)
        category = Category(eng_title=eng_title, title=title)
        category.main_image = f'categories_images/{eng_title}.jpeg'
        category.save()

