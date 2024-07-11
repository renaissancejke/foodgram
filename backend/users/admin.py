from django.contrib import admin

from recipes.models import User
from users.models import Subscription


class UserAdmin(admin.ModelAdmin):
    list_display = ('email',
                    'username',
                    'first_name',
                    'last_name',
                    )
    list_filter = ('is_blocked',)
    search_fields = ('email',
                     'username')

    def block_users(self, request, queryset):
        queryset.update(is_blocked=True)

    def unblock_users(self, request, queryset):
        queryset.update(is_blocked=False)


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
