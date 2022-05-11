from django.contrib import admin
from .models import Profile, Message

''' adminDashbord にProfileモデルを表示、操作する。 '''
admin.site.register(Profile)
admin.site.register(Message)