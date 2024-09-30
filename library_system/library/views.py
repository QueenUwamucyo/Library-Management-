from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Book, Transaction
from .serializers import UserSerializer, BookSerializer, TransactionSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = Book.objects.all()
        title = self.request.query_params.get('title', None)
        author = self.request.query_params.get('author', None)
        isbn = self.request.query_params.get('isbn', None)
        available = self.request.query_params.get('available', None)

        if title is not None:
            queryset = queryset.filter(title__icontains=title)
        if author is not None:
            queryset = queryset.filter(author__icontains=author)
        if isbn is not None:
            queryset = queryset.filter(isbn=isbn)
        if available is not None:
            queryset = queryset.filter(copies_available__gt=0)

        return queryset

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        book_id = request.data.get('book')
        user_id = request.data.get('user')

        try:
            book = Book.objects.get(id=book_id)
            user = User.objects.get(id=user_id)
        except (Book.DoesNotExist, User.DoesNotExist):
            return Response({'error': 'Book or user does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if book.copies_available <= 0:
            return Response({'error': 'Book is not available'}, status=status.HTTP_400_BAD_REQUEST)

        book.copies_available -= 1
        book.save()

        transaction = Transaction.objects.create(book=book, user=user)
        serializer = TransactionSerializer(transaction)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        transaction = self.get_object()
        book = transaction.book

        book.copies_available += 1
        book.save()

        transaction.date_returned = timezone.now()
        transaction.save()

        serializer = TransactionSerializer(transaction)

        return Response(serializer.data)