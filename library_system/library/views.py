from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import logout
from .models import Book, Transaction, UserProfile
from .serializers import BookSerializer, TransactionSerializer, UserSerializer, UserProfileSerializer, UserLoginSerializer
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.parsers import FileUploadParser
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# User Registration
class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            UserProfile.objects.create(user=user)
            return Response({ 
                'message': 'User created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Create JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Login successful.',
                'user': {
                    'username': user.username,
                    'email': user.email
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)

# Delete User (Admin or user themselves)
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, userId):
        user = get_object_or_404(User, id=userId)

        # Allow only admin or the user themselves to delete
        if request.user != user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete this user.")

        user.delete()
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


# Update User (Admin or user themselves)
class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, userId):
        user = get_object_or_404(User, id=userId)

        # Allow only admin or the user themselves to update
        if request.user != user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to update this user.")

        serializer = UserSerializer(user, data=request.data, partial=True)  # Partial allows updating some fields
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User updated successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# BookViewSet: Handles adding, updating, retrieving, and deleting books
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        # Only admins can create, update, or delete books
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        # Authenticated users can list and retrieve books
        return [IsAuthenticated()]


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can log out

    def post(self, request):
        try:
            # Extract the refresh token from the request data
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

# Search Books by name or ISBN
class BookSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        name = request.query_params.get('name')
        isbn = request.query_params.get('isbn')
        queryset = Book.objects.all()

        if name:
            queryset = queryset.filter(title__icontains=name)
        if isbn:
            queryset = queryset.filter(isbn=isbn)

        serializer = BookSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Notification View
class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Example logic to fetch notifications (like overdue books)
        overdue_transactions = Transaction.objects.filter(user=request.user, date_returned__isnull=True)
        notifications = []
        for transaction in overdue_transactions:
            if transaction.is_overdue():
                notifications.append(f"Book '{transaction.book.title}' is overdue.")

        return Response(notifications, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        # Placeholder for logic to mark notification as read
        return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)


# Fine View
class FineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fines = {}
        transactions = Transaction.objects.filter(user=request.user, date_returned__isnull=True)
        total_fine = 0

        for transaction in transactions:
            if transaction.is_overdue():
                overdue_days = transaction.overdue_days()
                fine = overdue_days * 2  # Assume a fine of 2 units per overdue day
                total_fine += fine
                fines[transaction.book.title] = f'{fine} units fine for {overdue_days} overdue days.'

        return Response({
            'total_fine': total_fine,
            'details': fines
        }, status=status.HTTP_200_OK)


# Admin Stats View
class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Example logic for retrieving stats
        num_books = Book.objects.count()
        num_users = User.objects.count()
        num_borrowed_books = Transaction.objects.filter(date_returned__isnull=True).count()
        stats = {
            "total_books": num_books,
            "total_users": num_users,
            "total_books_borrowed": num_borrowed_books,
        }
        return Response(stats, status=status.HTTP_200_OK)


# Most Borrowed Books View (Admin)
class MostBorrowedBooksView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        most_borrowed_books = Transaction.objects.values('book').annotate(count=models.Count('book')).order_by('-count')[:10]
        return Response(most_borrowed_books, status=status.HTTP_200_OK)


# Bulk Book Operations
class BulkBookUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [FileUploadParser]

    def post(self, request):
        file = request.FILES['file']
        # Logic to handle bulk upload of books using file
        return Response({"message": "Books uploaded successfully."}, status=status.HTTP_201_CREATED)


class BulkBookDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request):
        book_ids = request.data.get('book_ids', [])
        if not book_ids:
            return Response({"error": "No book IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        Book.objects.filter(id__in=book_ids).delete()
        return Response({"message": "Books deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# Transaction ViewSet
# TransactionViewSet: Handles borrowing and returning books
class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Handles borrowing a book (creates a transaction).
        """
        book_id = request.data.get('book_id')
        user = request.user

        # Get the book object
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Book does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the book is available for borrowing
        if book.copies_available <= 0:
            return Response({'error': 'No copies available for this book'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the transaction (borrow the book)
        transaction = Transaction.objects.create(user=user, book=book, date_checked_out=timezone.now())
        book.copies_available -= 1  # Decrease available copies
        book.save()

        serializer = TransactionSerializer(transaction)
        return Response({
            'message': 'Book borrowed successfully.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """
        Handles returning a book (updates a transaction).
        """
        transaction = self.get_object()

        if transaction.date_returned is not None:
            return Response({'error': 'Book has already been returned.'}, status=status.HTTP_400_BAD_REQUEST)

        # Mark the book as returned and increase available copies
        transaction.date_returned = timezone.now()
        transaction.book.copies_available += 1
        transaction.book.save()
        transaction.save()

        serializer = self.get_serializer(transaction)
        return Response({
            'message': 'Book returned successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)



# UserProfile ViewSet
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        # Allow users to retrieve only their profile
        instance = UserProfile.objects.get(user=request.user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
