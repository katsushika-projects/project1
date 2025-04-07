from uuid import uuid4

from django.db import models


class University(models.Model):
    class Meta:
        app_label = "campuses"

    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Campus(models.Model):
    class Meta:
        app_label = "campuses"

    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    campus = models.CharField(max_length=100)

    def __str__(self):
        return self.campus
