from flask import Flask, render_template, request, redirect, url_for  # noqa
from flask_sqlalchemy import SQLAlchemy
import datetime


app = Flask(__name__)
app.config['DEBUG'] = True


# configrations of our DataBase with MySQL.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:''@localhost/codingThunder'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Here We Defining Our Models:


class User(db.Model):
    """Models for User."""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_posts = db.relationship(
        "Post",
        backref='user',
        cascade="all, delete, delete-orphan")

    def __repr__(self):
        """Function to represent Data in Terminal."""
        return f"<User(user_id:{self.user_id}, user_name:{self.fullName})>" # noqa


class Post(db.Model):
    """Models for user Post."""

    __tablename__ = 'posts'

    post_id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(30), nullable=False)
    post_subtitle = db.Column(db.String(80), nullable=False)
    post_content = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    posted_by = db.relationship("User", backref="post")

    def __init__(self, data):
        """Here we create constructor of this class."""
        self.post_title = data['post_title']
        self.post_content = data['post_content']
        self.user_id = data['user_id']

    def __repr__(self):
        """Function to represent Data in Terminal."""
        return f"<Post(post_id:{self.post_id}, title:{self.post_title})>"

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
            'post_content': request.form['content'],
            'user_id': 1}
        post_object = Post(data)
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
        update_post_object = Post.query.filter_by(post_id=post_id).first()
        update_post_object.post_title = post_title
        update_post_object.post_content = post_content
        db.session.add(update_post_object)
        db.session.commit()
        return redirect(
            url_for('user_post', user_id=update_post_object.user_id)
        )

    user_post = Post.query.filter_by(post_id=post_id).first()
    return render_template('update.html', user_post=user_post)


@app.route('/delete_post/<int:post_id>')
def delete(post_id):
    """Here we delete the Post when user click on delete button."""
    user_post_object = Post.query.filter_by(post_id=post_id).first()
    db.session.delete(user_post_object)
    db.session.commit()
    return redirect(url_for('user_post', user_id=user_post_object.user_id))
    # return render_template('/')


@app.route('/about')
def about():
    """Show the loged in user post."""
    return render_template('about.html')


@app.route('/signUp')
def signUp():
    """Show signUP page."""
    return render_template('signUp.html')


@app.route('/login')
def login():
    """Show the Login Page."""
    return render_template('logIn.html')


@app.route('/logout')
def logout():
    """Show the Log out Page."""
    return render_template('logOut.html')


if __name__ == '__main__':
    app.run(debug=True)
