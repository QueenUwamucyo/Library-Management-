from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Book, Transaction
from django.utils import timezone
from datetime import timedelta
from django.core import mail
from rest_framework_simplejwt.tokens import RefreshToken


class LibraryTestCase(TestCase):

    def setUp(self):
        # Create a user and an admin
        self.user = User.objects.create_user(username='john', email='john@example.com', password='password123')
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
        self.book = Book.objects.create(title='Test Book', author='Test Author', isbn='1234567890123', published_date='2023-01-01', copies_available=2)

        # Set up API clients with JWT authentication
        self.client = APIClient()
        self.admin_client = APIClient()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token_for_user(self.user))
        self.admin_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token_for_user(self.admin_user))

    def get_token_for_user(self, user):
        """Helper method to generate JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_book_checkout(self):
        # Test user checking out a book
        response = self.client.post('/api/transactions/', {'user': self.user.id, 'book': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that book copies available decreased
        self.book.refresh_from_db()
        self.assertEqual(self.book.copies_available, 1)

    def test_book_return(self):
        # Test returning a checked out book
        response = self.client.post('/api/transactions/', {'user': self.user.id, 'book': self.book.id})
        transaction_id = response.data['id']
        return_response = self.client.post(f'/api/transactions/{transaction_id}/return_book/')
        self.assertEqual(return_response.status_code, status.HTTP_200_OK)

        # Check that book copies available increased
        self.book.refresh_from_db()
        self.assertEqual(self.book.copies_available, 2)

    def test_prevent_double_return(self):
        # Test that a book cannot be returned twice
        response = self.client.post('/api/transactions/', {'user': self.user.id, 'book': self.book.id})
        transaction_id = response.data['id']

        # Return the book once
        return_response = self.client.post(f'/api/transactions/{transaction_id}/return_book/')
        self.assertEqual(return_response.status_code, status.HTTP_200_OK)

        # Try to return the book again, should fail
        double_return_response = self.client.post(f'/api/transactions/{transaction_id}/return_book/')
        self.assertEqual(double_return_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(double_return_response.data['error'], 'Book already returned')

    def test_overdue_check_sends_email(self):
        # Test that email notifications are sent for overdue books
        response = self.client.post('/api/transactions/', {'user': self.user.id, 'book': self.book.id})
        transaction_id = response.data['id']

        # Manually set the checkout date to more than 14 days ago
        transaction = Transaction.objects.get(id=transaction_id)
        transaction.date_checked_out = timezone.now() - timedelta(days=15)
        transaction.save()

        # Check for overdue books as admin
        overdue_response = self.admin_client.post('/api/transactions/check_overdue/')
        self.assertEqual(overdue_response.status_code, status.HTTP_200_OK)

        # Check that the transaction is overdue
        self.assertTrue(overdue_response.data[0]['is_overdue'])

        # Check that an email has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify the email details
        email = mail.outbox[0]
        self.assertEqual(email.subject, f'Overdue Book: {self.book.title}')
        self.assertIn(f'Dear {self.user.username}', email.body)
        self.assertIn(self.book.title, email.body)
        self.assertEqual(email.to, [self.user.email])

    def test_prevent_multiple_checkout_of_same_book(self):
        # Test that a user cannot check out the same book twice without returning it
        response = self.client.post('/api/transactions/', {'user': self.user.id, 'book': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Try to check out the same book again without returning it
        duplicate_checkout_response = self.client.post('/api/transactions/', {'user': self.user.id, 'book': self.book.id})
        self.assertEqual(duplicate_checkout_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(duplicate_checkout_response.data['detail'], 'You have already checked out this book.')
