import os
from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Job, Application, Notification, Message
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'weekearn-super-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weekearn.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_notification(user_id, message):
    notif = Notification(user_id=user_id, message=message)
    db.session.add(notif)
    db.session.commit()

@app.after_request
def add_ngrok_header(response):
    response.headers['ngrok-skip-browser-warning'] = '69420'
    return response

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        city = request.form.get('city')
        phone = request.form.get('phone')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_pw, role=role, city=city, phone=phone)
        db.session.add(new_user)
        db.session.commit()
        
        create_notification(new_user.id, f"Welcome to WeekEarn! You registered as a {role}.")
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'company':
        jobs = Job.query.filter_by(company_id=current_user.id).order_by(Job.created_at.desc()).all()
        return render_template('dashboard_company.html', jobs=jobs)
    else:
        # Student Dashboard: List jobs from all cities by default but allow filtering
        city_filter = request.args.get('city')
        if city_filter:
            available_jobs = Job.query.filter_by(city=city_filter).order_by(Job.created_at.desc()).all()
        else:
            available_jobs = Job.query.order_by(Job.created_at.desc()).all()
            
        my_applications = Application.query.filter_by(student_id=current_user.id).all()
        applied_job_ids = [app.job_id for app in my_applications]
        
        cities = db.session.query(Job.city).distinct().all()
        cities = [c[0] for c in cities]
        
        return render_template('dashboard_student.html', jobs=available_jobs, applied_job_ids=applied_job_ids, cities=cities, selected_city=city_filter)

@app.route('/post_job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role != 'company':
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        city = request.form.get('city')
        location_address = request.form.get('location_address', '')
        date_str = request.form.get('job_date')
        max_spots = int(request.form.get('max_spots'))
        salary = request.form.get('salary', '')
        payment_method = request.form.get('payment_method', '')

        job_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        # Ensure it's weekend (5=Saturday, 6=Sunday)
        if job_date.weekday() not in [5, 6]:
            flash("Jobs can only be posted for weekends (Saturday or Sunday).", "danger")
            return redirect(url_for('post_job'))

        new_job = Job(
            title=title, 
            description=description, 
            company_id=current_user.id, 
            city=city, 
            location_address=location_address,
            job_date=job_date, 
            max_spots=max_spots,
            salary=salary,
            payment_method=payment_method
        )
        db.session.add(new_job)
        db.session.commit()
        
        create_notification(current_user.id, f"You successfully posted a new job: {title} in {city}.")
        flash('Job posted successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('post_job.html')

@app.route('/job_applicants/<int:job_id>')
@login_required
def job_applicants(job_id):
    if current_user.role != 'company':
        return redirect(url_for('dashboard'))
    
    job = Job.query.get_or_404(job_id)
    if job.company_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('dashboard'))
        
    applications = Application.query.filter_by(job_id=job.id).order_by(Application.applied_at.asc()).all()
    return render_template('job_applicants.html', job=job, applications=applications)

@app.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply(job_id):
    if current_user.role != 'student':
        return redirect(url_for('dashboard'))

    job = Job.query.get_or_404(job_id)
    
    # Check if already applied
    existing = Application.query.filter_by(job_id=job.id, student_id=current_user.id).first()
    if existing:
        flash("You have already applied for this job.", "info")
        return redirect(url_for('dashboard'))

    # Process FCFS Application
    accepted_count = Application.query.filter_by(job_id=job.id, status='Accepted').count()
    
    status = 'Rejected'
    if accepted_count < job.max_spots:
        status = 'Accepted'
        msg = f"Congratulations! You secured a spot for {job.title} at {job.company.username} on {job.job_date.strftime('%Y-%m-%d')}."
        create_notification(current_user.id, msg)
        company_msg = f"A new student ({current_user.username}) was selected for your job: {job.title}."
        create_notification(job.company_id, company_msg)
    else:
        msg = f"Sorry, all spots for {job.title} are already filled."
        create_notification(current_user.id, msg)

    application = Application(job_id=job.id, student_id=current_user.id, status=status)
    db.session.add(application)
    db.session.commit()

    if status == 'Accepted':
        flash('Application successful! You got the job (FCFS rule).', 'success')
    else:
        flash('Job is already full.', 'warning')

    return redirect(url_for('dashboard'))

from sqlalchemy import or_, and_

@app.route('/chat/<int:job_id>/<int:other_user_id>', methods=['GET', 'POST'])
@login_required
def chat(job_id, other_user_id):
    job = Job.query.get_or_404(job_id)
    other_user = User.query.get_or_404(other_user_id)
    
    # Ensure current user is either the student or the company of this job
    if current_user.role == 'company' and job.company_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            msg = Message(sender_id=current_user.id, receiver_id=other_user.id, job_id=job.id, content=content)
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('chat', job_id=job.id, other_user_id=other_user.id))
            
    messages = Message.query.filter(
        Message.job_id == job.id,
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == other_user.id),
            and_(Message.sender_id == other_user.id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()
    
    return render_template('chat.html', job=job, other_user=other_user, messages=messages)

@app.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifs)

@app.route('/read_notification/<int:notif_id>')
@login_required
def read_notification(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id == current_user.id:
        notif.is_read = True
        db.session.commit()
    return redirect(url_for('notifications'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # ngrok integration to expose to external networks
    port = 5050
    try:
        from pyngrok import ngrok
        # Open a ngrok tunnel to the dev server on a random free subdomain
        public_url = ngrok.connect(port).public_url
        print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:{port}\"")
        # Update any base URLs or configs if needed
        app.config["BASE_URL"] = public_url
    except ImportError:
        print(" * pyngrok not installed, running on localhost only.")
    except Exception as e:
        print(f" * pyngrok failed: {e}")

    # Run the application using Waitress (Production WSGI Server)
    from waitress import serve
    print(f" * Serving production app on 0.0.0.0:{port}")
    serve(app, host='0.0.0.0', port=port)
