from django.contrib import admin

from recipes.models import (Ingredient, IngredientRecipe, Link, Recipe, Tag,
                            TagRecipe, UserFavourite, UserShoppingCart)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'favourite_count'
    )
    search_fields = (
        'name', 'author'
    )
    list_filter = (
        'tags',
    )
    filter_horizontal = (
        'ingredients', 'tags'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit'
    )
    search_fields = (
        'name',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(UserFavourite)
class UserFavouriteAdmin(admin.ModelAdmin):
    pass


@admin.register(UserShoppingCart)
class UserShoppingCartAdmin(admin.ModelAdmin):
    pass


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    pass


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    pass
