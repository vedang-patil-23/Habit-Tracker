from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habits.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    habits = db.relationship('Habit', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    frequency = db.Column(db.String(50), nullable=False)  # 'daily' or 'weekly'
    goal = db.Column(db.Integer, nullable=True) # e.g., 5 times a week
    start_date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    completions = db.relationship('HabitCompletion', backref='habit', lazy=True, cascade="all, delete-orphan")

class HabitCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    completion_date = db.Column(db.Date, nullable=False, default=datetime.date.today)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    today = datetime.date.today()
    user_habits = current_user.habits
    
    for habit in user_habits:
        habit.completed_today = False
        if habit.frequency == 'daily':
            completion = HabitCompletion.query.filter_by(habit_id=habit.id, completion_date=today).first()
            if completion:
                habit.completed_today = True
        elif habit.frequency == 'weekly':
            # For weekly habits, check completions within the current week
            week_start = today - datetime.timedelta(days=today.weekday())
            week_end = week_start + datetime.timedelta(days=6)
            completions_this_week = HabitCompletion.query.filter(
                HabitCompletion.habit_id == habit.id,
                HabitCompletion.completion_date >= week_start,
                HabitCompletion.completion_date <= week_end
            ).count()
            habit.completions_this_week = completions_this_week
            habit.completed_today = completions_this_week >= habit.goal if habit.goal else False # Simplified for display

    # Prepare habit data for FullCalendar
    events = []
    # Temporarily hardcode events for debugging calendar rendering issue
    events.append({'title': 'Test Daily Habit', 'start': '2025-06-01', 'classNames': ['fc-event-done'], 'color': '#28a745'})
    events.append({'title': 'Test Weekly Habit', 'start': '2025-06-05', 'classNames': ['fc-event-missed'], 'color': '#e74c3c'})
    events.append({'title': 'Another Test Habit', 'start': '2025-06-10', 'classNames': [], 'color': '#5d6d7e'})

    # Original logic for generating events (commented out for testing)
    # for habit in user_habits:
    #     completions = HabitCompletion.query.filter_by(habit_id=habit.id).all()
    #     completed_dates = {c.completion_date for c in completions}

    #     today = datetime.date.today()
    #     delta = today - habit.start_date

    #     for i in range(delta.days + 1):
    #         current_date = habit.start_date + datetime.timedelta(days=i)
    #         if current_date > today:
    #             continue

    #         event_class_name = ''
    #         event_title = habit.name
    #         event_color = '#5d6d7e'

    #         if habit.frequency == 'daily':
    #             if current_date in completed_dates:
    #                 event_class_name = 'fc-event-done'
    #                 event_color = '#28a745'
    #             else:
    #                 event_class_name = 'fc-event-missed'
    #                 event_title += ' (Missed)'
    #                 event_color = '#e74c3c'
    #         elif habit.frequency == 'weekly':
    #             week_start = current_date - datetime.timedelta(days=current_date.weekday())
    #             week_end = week_start + datetime.timedelta(days=6)
    #             completions_this_week = HabitCompletion.query.filter(
    #                 HabitCompletion.habit_id == habit.id,
    #                 HabitCompletion.completion_date >= week_start,
    #                 HabitCompletion.completion_date <= week_end
    #             ).count()

    #             if habit.goal and completions_this_week >= habit.goal:
    #                 event_class_name = 'fc-event-done'
    #                 event_color = '#28a745'
    #             elif current_date <= today:
    #                 event_class_name = 'fc-event-missed'
    #                 event_title += ' (Goal not met)'
    #                 event_color = '#e74c3c'

    #         events.append({
    #             'title': event_title,
    #             'start': current_date.strftime('%Y-%m-%d'),
    #             'classNames': [event_class_name] if event_class_name else [],
    #             'id': habit.id,
    #             'color': event_color
    #         })

    return render_template('index.html', habits=user_habits, today=today, events=json.dumps(events))

@app.route('/add_habit', methods=['GET', 'POST'])
@login_required
def add_habit():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        frequency = request.form.get('frequency')
        goal = request.form.get('goal')
        start_date_str = request.form.get('start_date')
        
        goal = int(goal) if goal else None
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else datetime.date.today()

        if not name or not frequency:
            flash('Name and Frequency are required.', 'danger')
            return redirect(url_for('add_habit'))

        new_habit = Habit(name=name, description=description, frequency=frequency, goal=goal, start_date=start_date, user=current_user)
        db.session.add(new_habit)
        db.session.commit()
        flash('Habit added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_habit.html', today=datetime.date.today())

@app.route('/edit_habit/<int:habit_id>', methods=['GET', 'POST'])
@login_required
def edit_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user != current_user:
        flash('You do not have permission to edit this habit.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        habit.name = request.form.get('name')
        habit.description = request.form.get('description')
        habit.frequency = request.form.get('frequency')
        habit.goal = int(request.form.get('goal')) if request.form.get('goal') else None
        start_date_str = request.form.get('start_date')
        habit.start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else datetime.date.today()
        
        db.session.commit()
        flash('Habit updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('edit_habit.html', habit=habit)

@app.route('/delete_habit/<int:habit_id>', methods=['POST'])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user != current_user:
        flash('You do not have permission to delete this habit.', 'danger')
        return redirect(url_for('index'))
    db.session.delete(habit)
    db.session.commit()
    flash('Habit deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle_completion/<int:habit_id>', methods=['POST'])
@login_required
def toggle_completion(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user != current_user:
        flash('You do not have permission to toggle completion for this habit.', 'danger')
        return redirect(url_for('index'))

    today = datetime.date.today()
    completion = HabitCompletion.query.filter_by(habit_id=habit.id, completion_date=today).first()

    if completion:
        db.session.delete(completion)
        flash('Habit marked as incomplete for today.', 'info')
    else:
        new_completion = HabitCompletion(habit_id=habit.id, completion_date=today)
        db.session.add(new_completion)
        flash('Habit marked as complete for today!', 'success')
    
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', current_year=datetime.datetime.utcnow().year)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5005) 