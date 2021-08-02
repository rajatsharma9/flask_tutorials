from flask import Flask, render_template, request, redirect, url_for, flash, session # noqa
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required, LoginManager, UserMixin, current_user
import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'super secret key'
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
sess = Session()
sess.init_app(app)

# configrations of our DataBase with MySQL.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:''@localhost/codingThunder'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Here We Defining Our Models:


class User(db.Model, UserMixin):
    """Models for User."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100))
    user_posts = db.relationship(
        "Post",
        backref='user',
        cascade="all, delete, delete-orphan")

    def __repr__(self):
        """Function to represent Data in Terminal."""
        return f"<User(user_id:{self.id}, user_name:{self.fullName})>" # noqa


class Post(db.Model):
    """Models for user Post."""

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(30), nullable=False)
    post_subtitle = db.Column(db.String(80), nullable=False)
    post_content = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    posted_by = db.relationship("User", backref="post")

    def __init__(self, data):
        """Here we create constructor of this class."""
        self.post_title = data.get('post_title')
        self.post_subtitle = data.get('post_subtitle')
        self.post_content = data.get('post_content')

    def __repr__(self):
        """Function to represent Data in Terminal."""
        return f"<Post(post_id:{self.id}, title:{self.post_title})>"

# here we defining Views:


@app.route('/')
def home():
    """Show the Home Page for users."""
    return render_template('home.html')


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    """Here we use Http methods for creating our post by using forms."""
    if request.method == 'POST':
        data = {
            'post_title': request.form['title'],
            'post_subtitle': request.form['subtitle'],
            'post_content': request.form['content'],
        }
        post_object = Post(data)
        post_object.user_id = current_user.id
        db.session.add(post_object)
        db.session.commit()
    return render_template('createPost.html')


@app.route('/show_all_post/<int:user_id>')
def user_post(user_id):
    """Here we get/show the all Post of user by user_id."""
    user_posts = Post.query.filter(Post.user_id == user_id).order_by(
        Post.created_date.desc()).all()

    return render_template('showAllPost.html', user_posts=user_posts)


@app.route('/update_post/<int:post_id>', methods=['GET', 'POST'])
def update(post_id):
    """Here we use Http methods for updating the Post when user clickon update button."""
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        update_post_object = Post.query.filter_by(id=post_id).first()
        update_post_object.post_title = post_title
        update_post_object.post_content = post_content
        db.session.add(update_post_object)
        db.session.commit()
        return redirect(
            url_for('user_post', user_id=update_post_object.user_id)
        )

    user_post = Post.query.filter_by(id=post_id).first()
    return render_template('update.html', user_post=user_post)


@app.route('/delete_post/<int:post_id>')
def delete(post_id):
    """Here we delete the Post when user click on delete button."""
    user_post_object = Post.query.filter_by(post_id=post_id).first()
    db.session.delete(user_post_object)
    db.session.commit()
    return redirect(url_for('user_post', user_id=user_post_object.user_id))


@app.route('/about')
def about():
    """Show the loged in user post."""
    return render_template('about.html')


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    """Show signUP page."""
    if request.method == 'POST':
        fullName = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # if this returns a user, then the email already exists in database
        user = User.query.filter_by(email=email).first()

        # if a user is found, we want to redirect back to signup page so user can try again
        if user:
            flash('A user already exists with that email address.')
            return redirect(url_for('login'))

        # create new user with the form data. Hash the password so plaintext version isn't saved.
        new_user_object = User(fullName=fullName, email=email, username=username, password=bcrypt.generate_password_hash(password))
        db.session.add(new_user_object)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signUp.html')


@login_manager.user_loader
def load_user(user_id):
    """Since the user_id is just the primary key of our user table, use it in the query for the user."""
    return User.query.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Show the Login Page."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            session["user"] = user
            login_user(user)
            flash('Login Successfully')
            return redirect(url_for("user_post", user_id=user.id))

        flash('Invalid username/password combination')
        return redirect(url_for('login'))

    return render_template('logIn.html')


@app.route('/logout')
def logout():
    """Logout the current user."""
    session["user"] = None
    logout_user()
    return render_template("home.html")


if __name__ == '__main__':
    app.run(debug=True)
