from api.pagination import PostsPagination
from api.permissions import IsAdmin, IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, RegistrationSerializer,
                             ReviewSerializer, TitleSerializerGet,
                             TitleSerializerPostPatchDel, TokenSerializer,
                             UserSerializer)
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from reviews.models import Category, Genre, Review, Title, User

from api_yamdb.settings import CONFIRMATION_EMAIL, EXC_NAME


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PostsPagination
    permission_classes = (permissions.IsAuthenticated, IsAdmin)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def get_object(self):
        username = self.kwargs['username']
        if username == EXC_NAME:
            return self.request.user
        return super().get_object()

    def perform_update(self, serializer):
        if self.request.user.role == 'user':
            serializer.save(role='user')
        else:
            serializer.save()


@api_view(('POST', ))
def registration_view(request):
    serializer = RegistrationSerializer(data=request.data)
    data = {}
    serializer.is_valid(raise_exception=True)

    user = serializer.save()
    data['email'] = user.email
    data['username'] = user.username
    token = default_token_generator.make_token(user)
    send_mail(
        'Вам код для входа на сайт Yamdb',
        f'Пароль: {token}',
        CONFIRMATION_EMAIL,
        (user.email,),
        fail_silently=True)

    return Response(data)


@api_view(('POST',))
@permission_classes((permissions.AllowAny,))
def create_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = get_object_or_404(User, username=request.data['username'])
    if default_token_generator.check_token(user,
                                           request.data['confirmation_code']):
        token = serializer.get_token(user)
        return Response(token, status=status.HTTP_200_OK)
    return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(mixins.DestroyModelMixin, mixins.CreateModelMixin,
                      mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PostsPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(mixins.DestroyModelMixin, mixins.CreateModelMixin,
                   mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PostsPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PostsPagination

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TitleSerializerGet
        return TitleSerializerPostPatchDel

    def get_queryset(self):
        queryset = Title.objects.all()
        genre = self.request.query_params.get('genre')
        category = self.request.query_params.get('category')
        name = self.request.query_params.get('name')
        year = self.request.query_params.get('year')
        if genre is not None:
            return queryset.filter(genre__slug=genre)
        if category is not None:
            return queryset.filter(category__slug=category)
        if name is not None:
            return queryset.filter(name__contains=name)
        if year is not None:
            return queryset.filter(year=year)
        return queryset


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = PostsPagination

    def get_queryset(self):
        search_title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return search_title.reviews.all()

    def perform_create(self, serializer):
        search_title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=search_title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = PostsPagination

    def get_queryset(self):
        search_review = get_object_or_404(Review, id=self.kwargs['review_id'])
        return search_review.comments.all()

    def perform_create(self, serializer):
        search_review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=search_review)
