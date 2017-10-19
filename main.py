from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'display_blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    
    #if db.session['username']:   
    print("inside index")     
    users = User.query.all()
    return render_template('home.html',users=users)

   

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            session['owner_id'] = user.id
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

        if not username or len(username) < 3:
            flash('Please enter a valid user name, must be more than 3 characters.', 'error')
            return redirect('/signup')
        if not password or len(password) < 3:
            flash('Please enter a password, must be more than 3 characters.', 'error')
            return redirect('/signup')
        if not verify:
            flash('Please verify password', 'error')
            return redirect('/signup')
        if username and password != verify:
            flash('Passwords do not match', 'error')
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            new_user = User.query.filter_by(username=username).first()
            session['username'] = username
            session['owner_id'] = new_user.id
            return redirect('/newpost')
        else:
            return "<h1>Duplicate User</h1>"

    return render_template('signup.html')

  
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['POST','GET'])
def display_blogs():

    print("im in blogs")
    user = request.args.get('user')
    id = request.args.get('id')
    
    
    #if we have an id then we want to display the
    #post on a new page, by itself.  This is the blog.id
    # there shouldn't be any links on the final page ok
    # the author's name should be a link that takes you
    # to all of the author's posts
    if id and user:
        print("there is a user")
        this_post = Blog.query.filter_by(id=id).all()
        return render_template('/display_post.html',this_post=this_post,author=user)
    elif id and not user:  #came from singleUser.html
        print("there is NOTTTT a user")
        this_post = Blog.query.filter_by(id=id).all()
        user = User.query.filter_by(id=this_post[0].owner_id).first()
        return render_template('/display_post.html',this_post=this_post,author=user.username)
    elif not id and user: #this is a request from the home page to see all blog 
          #entries from a single author
        print("im in blogsssssssssssssss")
        owner = User.query.filter_by(username=user).first()
        blogs = Blog.query.filter_by(owner_id=owner.id)
        return render_template('/singleUser.html',this_post=blogs,author=owner.username)
    #if we do not have an id we want to display all of
    #the blog posts from all authors
    Users = User.query.all()
    Blogs = Blog.query.all()

    return render_template('/main_blog_page.html',users=Users,blogs=Blogs)


@app.route('/newpost', methods=['POST','GET'])
def newpost():
    return render_template('/add_a_blog_entry.html')


@app.route('/newentry', methods=['POST'])
def newentry():

    if not session['username']:
        return redirect('/login')

    title = str(request.form['title'])
    body = str(request.form['body'])
  
    owner = User.query.filter_by(username=session['username']).first()

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
        new_entry = Blog(title, body, owner)
        db.session.add(new_entry)
        db.session.commit()

        this_post = Blog.query.filter_by(title=title,body=body).first()
        return redirect('/blog?id={0}'.format(this_post.id))
        


if __name__ == '__main__':
    app.run()