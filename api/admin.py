from django.contrib import admin
from .models import Profile

''' adminDashbord にProfileモデルを表示、操作する。 '''
admin.site.register(Profile)
