from django.contrib import admin
from .models import Task  # Ensure you're importing the correct model

# Register your models here.
admin.site.register(Task)
