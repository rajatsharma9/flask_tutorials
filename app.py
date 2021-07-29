from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
import datetime
from sqlalchemy.orm import sessionmaker, relationship


app = Flask(__name__)
app.config['DEBUG'] = True


##Configrations of our DataBase with MySQL.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:''@localhost/codingThunder'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


## Here We Defining Our Models:
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_posts = db.relationship("Post", backref='user',cascade="all, delete, delete-orphan")

    def __repr__(self):
        return f"<User(user_id:{self.user_id},user_name:{self.fullName})>"

class Post(db.Model):
    __tablename__ = 'posts'

    post_id = db.Column(db.Integer,primary_key=True)
    post_title=db.Column(db.String(50),nullable=False)
    post_content=db.Column(db.Text,nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    posted_by = db.relationship("User", backref="post")

    def __repr__(self):
        return f"<Post(post_id:{self.post_id}, title:{self.post_title})"


## here we defining Views:
@app.route('/')
def home():
    # show the Home Page for users
    return render_template('home.html')

## Here we use Http methods for creating our post by using forms. 
@app.route('/create_post',methods=['GET','POST'])
def create_post():
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_object = Post(post_title=post_title,post_content=post_content,user_id=1)
        db.session.add(post_object)
        db.session.commit()
    return render_template('createPost.html')

# Here we get/show the all Post of user by user_id 
@app.route('/show_all_post/<int:user_id>')
def user_post(user_id):
    user_posts = Post.query.filter(Post.user_id==user_id).order_by(Post.created_date.desc()).all()
    return render_template('showAllPost.html',user_posts=user_posts)####

# Here we use Http methods for updateing the Post when user click on update button.
@app.route('/update_post/<int:post_id>',methods=['GET','POST'])
def update(post_id):
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        update_post_object = Post.query.filter_by(post_id=post_id).first()
        update_post_object.post_title = post_title#create dinamic ,naming convi
        update_post_object.post_content = post_content
        db.session.add(update_post_object)
        db.session.commit()
        return redirect(url_for('user_post',user_id=update_post_object.user_id))

    user_post = Post.query.filter_by(post_id=post_id).first()
    return render_template('update.html',user_post = user_post)

# Here we delete the Post when user click on delete button.
@app.route('/delete_post/<int:post_id>')
def delete(post_id):
    user_post_object = Post.query.filter_by(post_id=post_id).first()
    db.session.delete(user_post_object)
    db.session.commit()
    return redirect(url_for('user_post',user_id=user_post_object.user_id))
    # return render_template('/')

@app.route('/about')
def about():
    # show the loged in user post
    return render_template('about.html')

@app.route('/contact')
def contact():
    # show Conacts Details
    return render_template('contact.html')

@app.route('/login')
def login():
    # show the Login Page
    return render_template('logIn.html')

@app.route('/logout')
def logout():
    # show the Log out Page
    return render_template('logOut.html')

if __name__ == '__main__':
    app.run(debug=True)