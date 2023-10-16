from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from categories.models import Category

User = get_user_model()


class Product(models.Model):
    eng_title = models.CharField(max_length=500, unique=True, primary_key=True)
    title = models.CharField(max_length=500)
    price = models.PositiveIntegerField()
    original_link = models.URLField(null=True, blank=True)
    main_description = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    manufacturer = models.CharField(max_length=50, default='Прочие')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    users = models.ManyToManyField(User)

    class Meta:
        ordering = ['-title']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail', args=[str(self.eng_title)])


class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products_images/')

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'


class ProductProperties(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    text = models.CharField(max_length=300)

    class Meta:
        ordering = ['title']
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'


class ProductEquipments(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    text = models.CharField(max_length=300)

    class Meta:
        ordering = ['title']
        verbose_name = 'Комплектующий'
        verbose_name_plural = 'Комплектующие'


class ProductDescriptions(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.TextField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    some_url = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = 'описание'
        verbose_name_plural = 'все описания'