from django.db import models
from django.urls import reverse


class Category(models.Model):
    eng_title = models.CharField(max_length=100, unique=True, primary_key=True)
    title = models.CharField(max_length=100)
    main_image = models.ImageField(upload_to='categories_images/', null=True, blank=True)
    main_description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-title']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_detail', args=[str(self.eng_title)])