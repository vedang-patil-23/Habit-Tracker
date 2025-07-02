# Habit Tracker (Summer 2023)

> **Note:** This project was developed in summer 2023 as a personal project to track daily habits and build consistency. It's being uploaded to GitHub at a later date.

A Flask-based Habit Tracker application that helps you build and maintain good habits through consistent tracking and visualization of your progress.

## Features
- 📱 **User Authentication**: Secure login/logout system
- ➕ **Habit Management**: Add, edit, and delete habits
- 📅 **Daily/Weekly Tracking**: Mark habits as complete
- 📊 **Progress Visualization**: Track streaks and completion rates
- 🎨 **Responsive Design**: Works on desktop and mobile devices
- 📈 **Habit Analytics**: View your consistency and improvement over time

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd habit-tracker
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python init_db.py
   ```
   Default credentials:
   - Admin: `admin` / `admin123`
   - Viewer: `viewer` / `view123`

5. **Run the application**
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5005`

## 🛠 Deployment

### Local Deployment
1. Update the configuration in `app.py` for production:
   - Set `DEBUG = False`
   - Update `SECRET_KEY` with a strong secret
   - Configure a production database (SQLite is used by default for development)

2. For better performance, consider using a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5005 app:app
   ```

### Cloud Deployment (e.g., Heroku, PythonAnywhere)
1. Create a `Procfile` with:
   ```
   web: gunicorn app:app
   ```
2. Set environment variables:
   - `FLASK_APP=app.py`
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secret-key`

## 📝 Project Structure
```
habit_tracker/
├── app.py             # Main application file
├── init_db.py         # Database initialization
├── requirements.txt   # Dependencies
├── static/            # Static files (CSS, JS, images)
└── templates/         # HTML templates
```

## 📅 About This Project
- **Created**: Summer 2023
- **Purpose**: Personal project to track daily habits and learn web development
- **Tech Stack**: Python, Flask, SQLAlchemy, HTML/CSS/JavaScript

## 🔒 Security Note
- Change default credentials before deploying to production
- Use environment variables for sensitive information
- Consider implementing HTTPS in production