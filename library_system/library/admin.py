from django.contrib import admin
from .models import Book, Transaction, UserProfile

# Customize Book admin
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'copies_available')
    search_fields = ('title', 'author', 'isbn')  # Enable searching by title, author, and ISBN
    list_filter = ('author', 'published_date')  # Add a filter by author and publication date

# Customize Transaction admin
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'date_checked_out', 'date_returned', 'is_overdue')
    search_fields = ('user__username', 'book__title')  # Enable searching by username and book title
    list_filter = ('date_checked_out', 'date_returned')  # Filter by date
    readonly_fields = ('date_checked_out', 'date_returned')  # Make these fields read-only

    # Custom method to display if a transaction is overdue
    def is_overdue(self, obj):
        return obj.is_overdue()
    is_overdue.boolean = True  # Show a boolean icon for overdue status
    is_overdue.short_description = 'Overdue'

# Customize UserProfile admin
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_membership', 'is_active')
    search_fields = ('user__username', 'user__email')  # Enable searching by username and email
    list_filter = ('is_active',)  # Add a filter for active/inactive users

    # To view related User details in the UserProfile admin panel
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'

# Register your models and custom admin classes
admin.site.register(Book, BookAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
