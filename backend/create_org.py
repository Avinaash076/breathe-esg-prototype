#!/usr/bin/env python
import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ingestion.models import Organization

default_id = uuid.UUID('00000000-0000-0000-0000-000000000001')

org, created = Organization.objects.get_or_create(
    id=default_id,
    defaults={'name': 'Default Organization'}
)
print(f"Organization {'created' if created else 'already exists'}: {org.name} (ID: {org.id})")
