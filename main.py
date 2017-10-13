from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))

    blogs = db.relationship("Blog", 
               backref="user")
    
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(360))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#    owner_id = db.relationship("User", backref="blogs")
   
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('login')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        if user and user.password != password:
            flash('User password incorrect', 'error')
            return redirect('/login')
        if not user:
            flash('This user does not exist','error')
            return redirect('/login')

    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #TODO - validate
        if not username or len(username) < 3:
            flash('Please enter a valid user name, must be more than 3 characters.', 'error')
            return redirect('signup')
        if not password or len(password) < 3:
            flash('Please enter a password, must be more than 3 characters.', 'error')
            return redirect('signup')
        if not verify:
            flash('Please verify password', 'error')
            return redirect('signup')
        if username and password != verify:
            flash('Passwords do not match', 'error')
            return redirect('signup')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return "<h1>Duplicate User</h1>"

    return render_template('signup.html')

"""
@app.route('/', methods=['POST','GET'])
def ahsomething():

    owner = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        blog_title = request.form['title']
        new_blog = Blog(blog_title, owner)
        db.session.add(new_blog)
        db.session.commit()

    blogss = Blog.query.filter_by(owner_id=owner).all()
    return render_template('main_blog_page.html')
    
"""    
@app.route('/blog', methods=['POST','GET'])
def index():

    id = request.args.get('id')
    
    if id :
        this_post = Blog.query.filter_by(id=id).all()
        return render_template('display_post.html',this_post=this_post)
    else:
        entries = Blog.query.all()
        return render_template('/main_blog_page.html',entries=entries)


@app.route('/newpost', methods=['POST','GET'])
def newpost():
    return render_template('/add_a_blog_entry.html')


@app.route('/newentry', methods=['POST'])
def newentry():
    title = request.form['title']
    body = request.form['body']
    title_error =''
    body_error = ''

    #print("im here")
    if title == '':
        title_error = "Please fill in the title."
    if body == '':
        body_error = "Please fill in the body."

    if title_error or body_error:
        flash('Please provide the title and body for your entry','error')
        return render_template('/add_a_blog_entry.html',title=title,
            body=body,body_error="Please fill in the body.",
            title_error="Please fill in the title")
    else:
        new_entry = Blog(title, body)
        db.session.add(new_entry)
        db.session.commit()

        
        this_post = Blog.query.filter_by(title=title,body=body).all()
        return render_template('display_post.html',this_post=this_post)
        


if __name__ == '__main__':
    app.run()