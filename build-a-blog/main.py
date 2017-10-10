from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:abc123@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(360))

    def __init__(self, title, body):
        self.title = title
        self.body = body

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

    print("im here")
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