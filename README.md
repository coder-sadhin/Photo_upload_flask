# Social Media Web Application

A modern, full-stack social media web application built with Flask, featuring a sleek mobile-first UI design similar to popular social media platforms.

## Features

- **Authentication**: User registration, login, logout, password reset
- **User Profiles**: View and edit profiles, profile picture, cover photo, bio
- **Posts**: Create posts with text and media, like, save, comment
- **Comments & Replies**: Nested comments with likes
- **Follow System**: Follow/unfollow users, followers/following lists
- **Notifications**: Real-time notifications for likes, comments, follows
- **Dashboard**: Analytics-style dashboard with activity overview
- **Dark Mode**: Toggle dark/light theme
- **Search**: Search users by username or name
- **Explore**: Discover public posts from all users

## Tech Stack

- **Backend**: Flask 3.0, Flask-SQLAlchemy, Flask-Migrate, Flask-Login
- **Frontend**: HTML5, Tailwind CSS, JavaScript, jQuery
- **Database**: SQLite (migration-ready for PostgreSQL)
- **Media**: Pillow for image processing

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   flask init-db
   flask create-default-files
   ```

6. Run the application:
   ```bash
   python app.py
   ```

## Database Migration to PostgreSQL

The application is designed to be database-agnostic. To migrate to PostgreSQL:

1. Install PostgreSQL adapter:
   ```bash
   pip install psycopg2-binary
   ```

2. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/social_media
   ```

3. The application will automatically use PostgreSQL.

## Project Structure

```
├── app/
│   ├── __init__.py          # App factory
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   ├── follow.py
│   │   ├── notification.py
│   │   ├── password_reset.py
│   │   └── media.py
│   ├── routes/              # Route handlers
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── posts.py
│   │   ├── comments.py
│   │   ├── favorites.py
│   │   ├── notifications.py
│   │   └── main.py
│   ├── forms/               # WTForms
│   │   ├── auth_forms.py
│   │   ├── profile_forms.py
│   │   └── post_forms.py
│   └── services/            # Business logic
│       ├── notification_service.py
│       └── media_service.py
├── templates/               # Jinja2 templates
│   ├── base.html
│   ├── auth/
│   ├── main/
│   ├── users/
│   ├── posts/
│   ├── favorites/
│   └── notifications/
├── static/                  # Static files
│   └── uploads/            # User uploaded media
├── config.py               # Configuration
├── database_config.py      # Database configuration
├── app.py                  # Application entry point
└── requirements.txt
```

## API Routes

- `/` - Landing page
- `/home` - Home timeline
- `/explore` - Explore public posts
- `/dashboard` - User dashboard
- `/auth/register` - User registration
- `/auth/login` - User login
- `/auth/logout` - User logout
- `/auth/forgot-password` - Password reset request
- `/auth/reset-password/<token>` - Password reset
- `/auth/change-password` - Change password
- `/profile/<username>` - View profile
- `/profile/edit` - Edit profile
- `/followers/<username>` - Followers list
- `/following/<username>` - Following list
- `/favorites` - Saved posts
- `/notifications` - Notifications
- `/post/create` - Create post
- `/post/<id>` - View post
- `/post/<id>/like` - Like post
- `/post/<id>/save` - Save post
- `/search` - Search users

## Development

Run in development mode:
```bash
python app.py
```

The application will be available at `http://localhost:5000`.

# 👨‍💻 Author

Md. Akkas Ali
