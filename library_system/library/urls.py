from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookViewSet, TransactionViewSet, UserProfileViewSet, UserRegisterView, UserLoginView, DeleteUserView, 
    UpdateUserView, UserLogoutView, BookSearchView, NotificationViewSet, FineView, AdminStatsView, 
    MostBorrowedBooksView, BulkBookUploadView, BulkBookDeleteView
)

# Create a default router to register viewsets
router = DefaultRouter()
router.register(r'books', BookViewSet, basename='books')  # Register BookViewSet
router.register(r'transactions', TransactionViewSet, basename='transactions')  # Register TransactionViewSet
router.register(r'profiles', UserProfileViewSet, basename='profiles')  # Register UserProfileViewSet
router.register(r'notifications', NotificationViewSet, basename='notifications')  # Register NotificationViewSet

# Define the URL patterns
urlpatterns = [
    # Include the default router's URLs
    path('', include(router.urls)),

    # User registration and authentication
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    # User management (delete and update user)
    path('users/<int:userId>/delete/', DeleteUserView.as_view(), name='delete_user'),
    path('users/<int:userId>/update/', UpdateUserView.as_view(), name='update_user'),

    # Book operations
    path('books/<int:pk>/', BookViewSet.as_view({'get': 'retrieve'}), name='retrieve_book'),  # Get a specific book
    path('books/<int:pk>/update/', BookViewSet.as_view({'put': 'update'}), name='update_book'),  # Update a book
    path('books/<int:pk>/delete/', BookViewSet.as_view({'delete': 'destroy'}), name='delete_book'),  # Delete a book
    path('books/search/', BookSearchView.as_view(), name='book_search'),  # Search books by title or ISBN
    path('books/borrowed/', MostBorrowedBooksView.as_view(), name='borrowed_books'),  # Get the most borrowed books (Admin only)

    # Bulk book operations (Admin only)
    path('books/bulk_delete/', BulkBookDeleteView.as_view(), name='bulk_delete_books'),
    path('books/bulk_upload/', BulkBookUploadView.as_view(), name='bulk_upload_books'),

    # Transaction operations (borrow and return books)
    path('transactions/<int:pk>/return_book/', TransactionViewSet.as_view({'post': 'return_book'}), name='return_book'),

    # User-specific profile
    path('user/profile/', UserProfileViewSet.as_view({'get': 'retrieve'}), name='user_profile'),

    # Admin stats and fines
    path('admin/stats/', AdminStatsView.as_view(), name='admin_stats'),
    path('fines/', FineView.as_view(), name='fines'),
]
