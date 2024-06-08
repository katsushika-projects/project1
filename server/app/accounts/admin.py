from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Block

class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", )
    ordering = ("email", )

User = get_user_model()
admin.site.register(User, UserAdmin)
admin.site.register(Block)
