"""
This file controls the administrative interface for tobacco_analytics' main app
"""

from django.contrib import admin
from .models import DjangoPerson

admin.site.register(DjangoPerson)
