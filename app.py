# all imports
from email.policy import default
from enum import unique
from pickle import FALSE
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import desc, false
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import bcrypt

# create flask app
app = Flask(__name__)


# create sqlite URI to app
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'


# create login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# create user loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# create post db class
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    smalldesc = db.Column(db.String(100), nullable=False, default='N/A')
    link = db.Column(db.String(2000), nullable=True)
    key_project = db.Column(db.String(1), nullable=False, default='0')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return 'Blog post ' + str(self.id)


# create user db class
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


# create login form class
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


# main home page
@app.route('/')
def index():
    all_posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).all()
    key_posts = BlogPost.query.filter_by(key_project='1').order_by(BlogPost.date_posted.desc()).all()
    return render_template('index.html', posts=all_posts, kposts=key_posts)


# admin login page (use as route for post manage page)
@app.route('/login', methods=['GET', 'POST'])
def login():
    cuser = current_user
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if form.password.data == user.password:
                login_user(user)
                return redirect(url_for('posts_manage'))
    return render_template('login.html', form=form, cuser=cuser)


# logout route
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# posts read-only page
@app.route('/posts', methods=['GET', 'POST'])
def posts():

    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_smalldesc = request.form['smalldesc']
        post_link = request.form['link']
        post_key_project = request.form['key_project']
        new_post = BlogPost(title=post_title, content=post_content, smalldesc=post_smalldesc, link=post_link, key_project=post_key_project)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
        all_posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).all()
        return render_template('posts.html', posts=all_posts)


# posts manage page
@app.route('/posts_manage', methods=['GET', 'POST'])
@login_required
def posts_manage():

    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_smalldesc = request.form['smalldesc']
        post_link = request.form['link']
        post_key_project = request.form['key_project']
        new_post = BlogPost(title=post_title, content=post_content, smalldesc=post_smalldesc, link=post_link, key_project=post_key_project)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts_manage')
    else:
        all_posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).all()
        return render_template('posts_manage.html', posts=all_posts)


# delete post route
@app.route('/posts/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts')


# edit post page
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    post = BlogPost.query.get_or_404(id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.smalldesc = request.form['smalldesc']
        post.content = request.form['content']
        post.link = request.form['link']
        post.key_project = request.form['key_project']
        db.session.commit()
        return redirect('/posts_manage')
    else: 
        return render_template('edit.html', post=post)


# new project page
@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():

    if request.method == 'POST':
        post_title = request.form['title']
        post_smalldesc = request.form['smalldesc']
        post_content = request.form['content']
        post_link = request.form['link']
        post_key_project = request.form['key_project']
        new_post = BlogPost(title=post_title, content=post_content, smalldesc=post_smalldesc, link=post_link, key_project=post_key_project)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts_manage')
    else: 
        return render_template('new_post.html')


if __name__ == "__main__":
    app.run(debug=True)


