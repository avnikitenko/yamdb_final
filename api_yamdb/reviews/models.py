from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.settings import MAX_REVIEW_SCORE, MIN_REVIEW_SCORE

MODERATOR = 'moderator'
ADMIN = 'admin'

CHOICES = (
    (ADMIN, 'Админ'),
    ('user', 'Пользователь'),
    (MODERATOR, 'Модератор')
)


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='username',
        help_text='Логин пользователя'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='email',
        help_text='Email пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='first_name',
        help_text='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='surname',
        help_text='Фамилия'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='bio',
        help_text='Автобиография пользователя'
    )
    role = models.CharField(
        max_length=20,
        choices=CHOICES,
        default='user',
        verbose_name='role',
        help_text='Роль пользователя'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser


class Category(models.Model):

    name = models.CharField(
        max_length=64,
        verbose_name='name',
        help_text='Наименование категории'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='code',
        help_text='Код категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):

    name = models.CharField(
        max_length=64,
        verbose_name='name',
        help_text='Наименование жанра'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='code',
        help_text='Код жанра'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):

    name = models.CharField(
        max_length=64,
        verbose_name='name',
        help_text='Наименование произведения'
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='year',
        help_text='Год произведения'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='genres',
        help_text='Жанры произведения'
    )
    description = models.TextField(
        null=True,
        verbose_name='description',
        help_text='Описание произведения'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name='titles',
        verbose_name='category',
        help_text='Категория произведения'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='genres',
        verbose_name='title',
        help_text='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='genre',
        help_text='Жанр'
    )

    class Meta:
        verbose_name = 'Жанр-Заголовок'
        verbose_name_plural = 'Жанры-Заголовки'

    def __str__(self):
        return f'{self.title[:15]} - {self.genre[:15]}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='title',
        help_text='Произведение'
    )
    text = models.TextField(
        verbose_name='text',
        help_text='Сопроводительный текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='author',
        help_text='Автор оценки'
    )
    score = models.PositiveIntegerField(
        validators=(
            MinValueValidator(MIN_REVIEW_SCORE),
            MaxValueValidator(MAX_REVIEW_SCORE)
        ),
        verbose_name='score',
        help_text='Оценка (значение)'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='publication_date',
        help_text='Дата публикации оценки'
    )

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_author_title'
            ),
        )

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='review',
        help_text='Оценка'
    )
    text = models.TextField(
        verbose_name='text',
        help_text='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='author',
        help_text='Автор комментария'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='publication_date',
        help_text='Дата публикации комментария'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]
