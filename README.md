# Library Management System API

## Overview

The **Library Management System** is a backend application built with **Django** and **Django REST Framework (DRF)**. It provides API endpoints for managing users, books, transactions (borrowing and returning books), overdue notifications, and fines. The system is role-based, with admins having the ability to manage books and users, while authenticated users can borrow and return books. The project is designed with scalability and security in mind, using JWT for user authentication and role-based permissions.

---

## Features

- **User Management**:
  - User registration and login (JWT-based).
  - User profile retrieval and updates.
  - Admins can delete or update users.

- **Book Management**:
  - CRUD operations for books (admins only).
  - Search for books by title or ISBN.
  - Bulk book upload and delete (admins only).

- **Transactions**:
  - Borrow and return books.
  - Track overdue books and calculate fines for late returns.

- **Notifications**:
  - Receive notifications for overdue books.
  
- **Admin Stats**:
  - View statistics for total books, users, and borrowed books.
  
- **Fine Management**:
  - Calculate and display fines for overdue books.

---

## Tech Stack

- **Backend**: Django, Django REST Framework (DRF)
- **Database**: PostgreSQL (or other databases supported by Django)
- **Authentication**: JWT (JSON Web Tokens)
- **Others**: Django REST Framework Simple JWT, Python

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/library-management-system.git
cd library-management-system
```

### 2. Create a Virtual Environment

```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Database

In the project root, create a `.env` file with your database credentials:

```bash
DATABASE_URL=postgres://<username>:<password>@localhost:5432/<database_name>
```

Alternatively, modify `settings.py` to include your database credentials directly if you're not using an `.env` file.

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

The server will be running at `http://127.0.0.1:8000/`.

---

## API Endpoints

### Authentication

- **Register**: `POST /api/register/`
  - Register a new user.

- **Login**: `POST /api/login/`
  - Log in a user and receive access/refresh tokens.

- **Logout**: `POST /api/logout/`
  - Invalidate the user’s JWT token.

### User Management

- **Delete User**: `DELETE /api/users/<int:userId>/delete/`
  - Delete a specific user (admins or the user themselves).
  
- **Update User**: `PUT /api/users/<int:userId>/update/`
  - Update user details (admins or the user themselves).
  
- **Get User Profile**: `GET /api/user/profile/`
  - Get the authenticated user’s profile.

### Book Management

- **Add Book**: `POST /api/books/`
  - Add a new book (admins only).

- **Get Book**: `GET /api/books/<int:pk>/`
  - Get details of a specific book.

- **Update Book**: `PUT /api/books/<int:pk>/update/`
  - Update book details (admins only).

- **Delete Book**: `DELETE /api/books/<int:pk>/delete/`
  - Delete a specific book (admins only).

- **Search Books**: `GET /api/books/search/?name=<book_name>&isbn=<isbn>`
  - Search books by name or ISBN.

- **Bulk Upload Books**: `POST /api/books/bulk_upload/`
  - Upload multiple books via a file (admins only).

- **Bulk Delete Books**: `DELETE /api/books/bulk_delete/`
  - Delete multiple books by their IDs (admins only).

### Transaction Management

- **Borrow Book**: `POST /api/transactions/`
  - Borrow a book by providing the `book_id` (authenticated users only).

- **Return Book**: `POST /api/transactions/<int:pk>/return_book/`
  - Return a borrowed book (only by the user who borrowed it).

### Notifications

- **Get Notifications**: `GET /api/notifications/`
  - Get notifications for overdue books (authenticated users).

### Fines

- **Get Fines**: `GET /api/fines/`
  - View fines for overdue books (authenticated users).

### Admin Statistics

- **Get Stats**: `GET /api/admin/stats/`
  - View statistics for the total number of books, users, and currently borrowed books (admins only).

### Most Borrowed Books

- **Get Most Borrowed Books**: `GET /api/books/borrowed/`
  - View the list of the most borrowed books (admins only).

---

## Permissions and Roles

- **Admin Users**: Can manage books, users, bulk operations, and view system stats.
- **Authenticated Users**: Can borrow/return books, view their profile, and view overdue notifications.
- **Public Users**: Can register and search for books but need to log in to borrow books.

---

## Testing

To run tests:

```bash
python manage.py test
```

Ensure to have some test data or mock the database for running tests effectively.

---

## Future Enhancements

- **Email Notifications**: Sending email reminders for overdue books.
- **Frontend**: Develop a frontend using React or Vue.js for a complete user interface.
- **Advanced Search**: Implement more filters for book searches (e.g., by genre, author, publication year).

---

## Contribution

Contributions are welcome! If you’d like to contribute, please follow the steps below:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

---

## License

This project is licensed under the MIT License.

