from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from recipes.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                           redirect_from_short_link)
from users.views import MyUserViewSet, subscribe

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'users', MyUserViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/users/<int:pk>/subscribe/', subscribe, name='subscribe'),
    path('s/<str:slug>/', redirect_from_short_link, name='redirect'),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
]
