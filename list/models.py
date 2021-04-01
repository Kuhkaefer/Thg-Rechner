from django.db import models

# Create your models here.
class Emissions(models.Model):
    name        = models.TextField()
    description = models.TextField()
    value       = models.TextField()
