from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from api_yamdb.settings import EXC_NAME, MAX_REVIEW_SCORE, MIN_REVIEW_SCORE


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'bio', 'role')

    def validate(self, data):
        if 'username' not in data:
            return data

        if data['username'] == EXC_NAME:
            raise serializers.ValidationError(
                {'username': f'username can not be "{EXC_NAME}"'})
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        if data['username'] == EXC_NAME:
            raise serializers.ValidationError(
                {'username': f'username can not be "{EXC_NAME}"'})
        return data


class TokenSerializer(TokenObtainPairSerializer):
    confirmation_code = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'token': str(refresh.access_token),
        }

    def validate(self, data):
        return get_object_or_404(User, username=data['username'])


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        lookup_field = 'slug'
        fields = ('name', 'slug')


class TitleSerializerPostPatchDel(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        queryset=Genre.objects.all(),
        slug_field='slug'
    )
    category = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:

        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category')
        read_only_fields = ('id',)


class TitleSerializerGet(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = GenreSerializer(many=False, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:

        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        read_only_fields = ('id', 'rating')

    def get_rating(self, obj):
        return obj.reviews.all().aggregate(
            Avg('score')
        ).get('score__avg')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        lookup_field = 'slug'
        fields = ('name', 'slug')


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('id', 'pub_date', 'author', 'title',)

    def validate(self, data):
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        search_title = get_object_or_404(Title, id=title_id)
        if self.partial:
            return data
        if Review.objects.filter(
            author=self.context['request'].user,
            title=search_title,
        ).exists():
            raise serializers.ValidationError(
                'Отзыв пользователя на произведение уже существует')
        return data

    def validate_score(self, value):
        if value > MAX_REVIEW_SCORE or value < MIN_REVIEW_SCORE:
            raise serializers.ValidationError(
                f'Оценка должна быть в диапазоне от {MIN_REVIEW_SCORE}'
                f' до {MAX_REVIEW_SCORE}'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('id', 'pub_date', 'author', 'review',)
