from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from .models import Recipe, RecipeLike
from .serializers import RecipeLikeSerializer, RecipeSerializer
from .permissions import IsAuthorOrReadOnly
from rest_framework.pagination import PageNumberPagination

class RecipePagination(PageNumberPagination):
    page_size = 2  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class RecipeListAPIView(generics.ListAPIView):
    """
    A viewset for viewing and editing recipe instances.
    """
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    pagination_class = RecipePagination
    filterset_fields = ('category__name', 'author__username')

    def get_queryset(self):
        # Use select_related to optimize foreign key lookups
        queryset = Recipe.objects.select_related('category', 'author').all()
        return queryset

class RecipeCreateAPIView(generics.CreateAPIView):
    """
    Create: a recipe
    """
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Use select_related to optimize foreign key lookups
        return Recipe.objects.select_related('category', 'author').all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class RecipeAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, Update, Delete a recipe
    """
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        # Use select_related to optimize foreign key lookups
        return Recipe.objects.select_related('category', 'author').all()

class RecipeLikeAPIView(generics.CreateAPIView):
    """
    Like, Dislike a recipe
    """
    serializer_class = RecipeLikeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        new_like, created = RecipeLike.objects.get_or_create(
            user=request.user, recipe=recipe)
        if created:
            new_like.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        like = RecipeLike.objects.filter(user=request.user, recipe=recipe)
        if like.exists():
            like.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
