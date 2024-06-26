# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

# Initialize Flask app
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key'  # random secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
    return app

# Initialize Flask-Login
def initialize_login(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    return login_manager

# Initialize Flask-SQLAlchemy
def initialize_database(app):
    db = SQLAlchemy(app)
    return db

app = create_app()
login_manager = initialize_login(app)
db = initialize_database(app)

# Database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    phone = db.Column(db.Integer)
    portfolios = db.relationship('Portfolio', backref='user', lazy=True)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nickname = db.Column(db.String(100))
    bio = db.Column(db.Text)
    education_degree = db.Column(db.String(100))
    education_major = db.Column(db.String(100))
    education_school = db.Column(db.String(100))
    education_year = db.Column(db.String(10))
    work_position = db.Column(db.String(100))
    work_company = db.Column(db.String(100))
    work_duration = db.Column(db.String(50))
    work_description = db.Column(db.Text)
    projects = db.relationship('Project', backref='portfolio', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(200))

# Login manager callback to reload user object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
def initialize_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            # Handle form submission
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            full_name = request.form['full_name']
            email = request.form['email']
            phone = request.form['phone']
            # Check if passwords match and username is unique
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('signup'))
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists', 'error')
                return redirect(url_for('signup'))
            # Create new user and portfolio
            new_user = User(username=username, password=password, full_name=full_name, email=email,phone=phone)
            # new_portfolio = Portfolio(
            #     user=new_user,
            #     full_name=full_name,
            #     email=email,
            #     phone=phone
            # )
            db.session.add(new_user)
            # db.session.add(new_portfolio)
            db.session.commit()
            flash('Account created successfully', 'success')
            # Redirect to index after successful signup
            return redirect(url_for('index'))
        else:
            # Render the signup form
            return render_template('signup.html')

    @app.route('/login', methods=['POST'])
    def login():
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('index'))

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        user = current_user
        return render_template('dashboard.html', user=user)

    @app.route('/add_portfolio', methods=['GET', 'POST'])
    @login_required
    def add_portfolio():
        if request.method == 'POST':
            user = current_user
            # full_name = user.full_name
            # email = user.email
            # phone = user.phone
            bio = request.form['bio']
            education_degree = request.form['education_degree']
            education_major = request.form['education_major']
            education_school = request.form['education_school']
            education_year = request.form['education_year']
            work_position = request.form['work_position']
            work_company = request.form['work_company']
            work_duration = request.form['work_duration']
            work_description = request.form['work_description']
            nickname = request.form['nickname']
            new_portfolio = Portfolio(
                user=user,
                nickname=nickname,
                # full_name=full_name,
                # email=email,
                # phone=phone,
                bio=bio,
                education_degree=education_degree,
                education_major=education_major,
                education_school=education_school,
                education_year=education_year,
                work_position=work_position,
                work_company=work_company,
                work_duration=work_duration,
                work_description=work_description
            )
            db.session.add(new_portfolio)
            db.session.commit()
            flash('Portfolio created successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            return render_template('add_portfolio.html')
    
    # Add a route to handle creating a new portfolio page
    @app.route('/portfolio/<int:portfolio_id>')
    @login_required
    def portfolio(portfolio_id):
        portfolio = Portfolio.query.get_or_404(portfolio_id)
        return render_template('portfolio.html', user=current_user, portfolio=portfolio)

    # Add a route to handle adding a project to a portfolio
    @app.route('/add_project', methods=['POST'])
    @login_required
    def add_project():
        title = request.form['title']
        url = request.form['url']
        description = request.form['description']
        nickname = request.form['nickname']
        portfolio = Portfolio.query.get_or_404(nickname)
        new_project = Project(title=title, url=url, description=description, portfolio=portfolio)
        db.session.add(new_project)
        db.session.commit()
        return jsonify({'title': title, 'url': url, 'description': description}), 200


# Main function to create and run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    initialize_routes(app)
    app.run(debug=True)
