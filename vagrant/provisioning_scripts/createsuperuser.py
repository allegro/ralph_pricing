#!/usr/bin/python
import os
import django
# from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scrooge.settings")
from django.conf import settings
settings._setup()
# django.setup()

print('Updating superuser info')
u = User.objects.get(username='scrooge')
u.set_password('scrooge')
u.is_superuser = True
u.is_staff = True
u.save()
