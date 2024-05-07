import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dict.settings")

# Initialize Django
django.setup()

# Now you can import your models and perform operations on them
from myapp.models import Questions

# Delete all instances of MyModel
Questions.objects.all().delete()

from django.db import connection

# Drop the Questions table (optional)
with connection.cursor() as cursor:
    cursor.execute("DROP TABLE myapp_questions;")

 
