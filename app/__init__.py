from datetime import datetime

from flask import Flask, render_template, request, redirect, make_response, url_for, render_template_string
from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = '<KEY>'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


"""
flask db init 
flask db migrate
flaks db upgrade
"""


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(80), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or user.password != request.form['password']:
            return redirect(url_for('login'))
        login_user(user, remember=True)
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/load-posts')
def load_posts():
    posts = Post.query.all()
    posts = [(post, Like.query.filter_by(post=post.id).count()) for post in posts]
    return render_template('load-posts.html', posts=posts)


@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_file = request.files['image']

        if image_file:
            image_path = 'static/uploads/' + title + '.jpg'
            image_file.save(image_path)

            post = Post(title=title, content=content, image=image_path)
            db.session.add(post)
            db.session.commit()

            return "<p>Post created successfully!</p>", 200
        else:
            return "<p>Error: Image is required.</p>", 400

    return render_template('add-post.html')


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get(post_id)
    comments = Comment.query.filter_by(post=post_id)
    return render_template('post-detail.html', post_id=post_id, post=post, comments=comments)


@app.route('/post/<int:post_id>/add-comment', methods=['POST'])
def add_comment_post(post_id):
    text = request.form['commentText']
    comment = Comment(content=text, post=post_id)
    db.session.add(comment)
    db.session.commit()
    response = make_response(render_template('comments-list.html', comments=Comment.query.filter_by(post=post_id)))
    response.headers['HX-Trigger'] = 'update_post_data'
    return response


@app.route('/post/<int:post_id>/add-like', methods=['POST'])
def add_like(post_id):
    like = Like(post=post_id)
    db.session.add(like)
    db.session.commit()
    like_count = Like.query.filter_by(post=post_id).count()
    response = make_response(str(like_count))
    response.headers['HX-Trigger'] = 'update_post_data'
    return response


@app.route('/test')
def htmx():
    response = make_response()
    response.headers['HX-Redirect'] = f'{url_for("add_post")}'
    return response


@app.route('/update-post/<int:post_id>', methods=['GET', 'POST'])
def update_post(post_id):
    pass

@app.route('/profile/get-data')
def profile_data():
    return render_template('profile.html', user=current_user)
@app.route('/profile/edit', methods=['GET'])
def edit_profile():
    return render_template('edit-profile.html', user=current_user)

@app.route('/profile/update_profile', methods=['POST'])
def update_profile():
    current_user.username = request.form['username']
    db.session.commit()
    response = make_response()
    response.headers['HX-Trigger'] = 'update_profile_data'
    response.status_code = 204
    return render_template('cancel-edit.html', user=current_user)


@app.route('/search-posts', methods=['GET'])
def search_posts():
    query = request.args.get('query', '')
    if query:
        posts = Post.query.filter(Post.title.contains(query)).all()
    else:
        posts = Post.query.all()

    posts = [(post, Like.query.filter_by(post=post.id).count()) for post in posts]
    return render_template('load-posts.html', posts=posts)


# AJAX - Async JavaScript and XML
if __name__ == '__main__':
    app.run(debug=True)
