from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, Transaction, UserProfile
from django.contrib.auth import authenticate


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'published_date', 'copies_available']


# TransactionSerializer: Serializes the Transaction model
class TransactionSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)  # Show book details when viewing transactions
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True, source='book')
    user = serializers.StringRelatedField(read_only=True)  # Show username for the transaction
    is_overdue = serializers.SerializerMethodField()  # Adds 'is_overdue' field to transactions

    class Meta:
        model = Transaction
        fields = ['id', 'book', 'book_id', 'user', 'date_checked_out', 'date_returned', 'is_overdue']

    def get_is_overdue(self, obj):
        """
        Custom method to check if the book is overdue.
        """
        return obj.is_overdue()
    
class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'date_of_membership', 'is_active']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    return user
                else:
                    raise serializers.ValidationError("This account is inactive.")
            else:
                raise serializers.ValidationError("Invalid username or password.")
        else:
            raise serializers.ValidationError("Both username and password are required.")
