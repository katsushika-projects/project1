from django.contrib import admin

from .models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ("message", "item_id", )

admin.site.register(Message, MessageAdmin)
