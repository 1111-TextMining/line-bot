from django.contrib import admin
from line_bot_app.models import *

class User_Note_Admin(admin.ModelAdmin):
    list_display = ('uid', 'notes', 'mdt')

class User_Message_Admin(admin.ModelAdmin):
    list_display = ('uid', 'mtext', 'rtext', 'ner_result', 'mdt')

admin.site.register(User_Note, User_Note_Admin)
admin.site.register(User_Message, User_Message_Admin)
