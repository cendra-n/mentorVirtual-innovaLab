from django.contrib import admin
from .models import UserProfile, UserConfig

admin.site.register(UserProfile)
admin.site.register(UserConfig)
