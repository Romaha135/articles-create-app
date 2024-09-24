from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id

@app.route('/')
@app.route('/home')
def index():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template('index.html', articles=articles)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template('posts.html', articles=articles)

@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get_or_404(id)
    return render_template('post_detail.html', article=article)

@app.route('/posts/<int:id>/delete', methods=['POST'])
def post_delete(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')  # Redirect to posts after deletion
    except:
        db.session.rollback()
        return 'An error occurred while deleting the article.'
    

@app.route('/posts/<int:id>/update', methods=['POST',  'GET'])

def post_update(id):
    article  = Article.query.get_or_404(id)
    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/posts')  # Redirect to posts after deletion
        except:
            return  'An error occurred while updating the article.'
    else:
        
        return  render_template('post_update.html', article=article)
    

@app.route('/search')
def search():
    query = request.args.get('article_name')  # Ensure this matches the input name in your search form
    if query:
        # Use ilike for case-insensitive search in title, intro, and text
        articles = Article.query.filter(
            Article.title.ilike(f'%{query}%') |
            Article.intro.ilike(f'%{query}%') |
            Article.text.ilike(f'%{query}%')
        ).all()
    else:
        articles = []
    
    return render_template('search_results.html', articles=articles, query=query)




    


@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title=title, intro=intro, text=text, date=datetime.utcnow())
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return 'An error occurred while creating the article.'
    else:
        return render_template('create-article.html')

if __name__ == '__main__':
    app.run(debug=True)
