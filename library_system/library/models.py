from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField()
    copies_available = models.PositiveIntegerField()  # Using PositiveIntegerField to avoid negative values

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.copies_available < 0:
            raise ValidationError("Copies available cannot be negative.")
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_membership = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_checked_out = models.DateTimeField(auto_now_add=True)
    date_returned = models.DateTimeField(null=True, blank=True)

    def is_overdue(self):
        overdue_period = timedelta(days=14)
        return (timezone.now() - self.date_checked_out) > overdue_period and self.date_returned is None

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
