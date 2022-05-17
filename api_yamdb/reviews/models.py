from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from.validators import validate_year

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(
        unique=True, max_length=50,
        validators=[RegexValidator(regex='^[-a-zA-Z0-9_]+$')]
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['-slug']


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(
        unique=True, max_length=50,
        validators=[RegexValidator(regex='^[-a-zA-Z0-9_]+$')]
    )

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['-name']


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField(
        validators=[validate_year],
    )
    description = models.TextField(null=True, blank=True)
    genre = models.ManyToManyField(Genre, related_name='genres')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='category'
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = ['-name']


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(0)
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Обзор"
        verbose_name_plural = "Обзоры"
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='one_review_per_title'
            )
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-id']
