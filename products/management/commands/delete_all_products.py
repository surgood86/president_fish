import os
from django.core.management.base import BaseCommand

from categories.models import Category


class Command(BaseCommand):
    help = 'delete all objects of Product model'

    def handle(self, *args, **kwargs):
        Category.objects.all().delete()
        #images_location = '/president_fish/static/media/products_images'
        images_location = '/home/tt/PycharmProjects/president_fish/static/media/products_images'
        for file in os.listdir(images_location):
            image_path = os.path.join(images_location, file)
            os.remove(image_path)
