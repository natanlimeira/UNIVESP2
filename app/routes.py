import json
import random
from flask import render_template, request, redirect, jsonify, flash
from flask_login import current_user, login_user, logout_user, login_required
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from app import app, db
from app.models import Card, User, Book, Level
from app.forms import LoginForm, RegistrationForm

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/")
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, admin=form.admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Parabéns, agora você é um usuário!')
        return redirect("/login")
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Nome ou senha incorreta','Erro de login')
            return redirect("/login")
        admin = user.get_admin()
        login_user(user, remember=form.remember_me.data)
        if admin == 2:
            return redirect("/admin")
        else:
            return redirect("/")
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect("/login")    

@app.route("/")
@login_required
def index():
    try:
        u = User.query.get(current_user.id)
        cards = u.posts.all()
        books = set(list(t.topic for t in cards))
        random_card = random.choice(cards)
        total_cards = len(cards)
        all_books_len = len(books)
        all_books = sorted(books)
    except:
        random_card = None
        total_cards = 0
        all_books_len = 0
        all_books = 0

    return render_template("index.html", card=random_card, total_cards=total_cards, all_books_len=all_books_len, all_books=all_books)

@app.route("/admin")
@login_required
def admin():
    # try:
    cards = Card.query.all()
    books = Book.query.all()
    random_card = random.choice(cards)
    total_cards = len(cards)
    all_books_len = len(books)
    # all_books = sorted(books)
    # except:
    #     random_card = None
    #     total_cards = 0
    #     all_books_len = 0
    #     all_books = 0

    return render_template("admin.html", card=random_card, total_cards=total_cards, all_books_len=all_books_len)#, all_books=all_books)


@app.route("/cards/new", methods=["GET", "POST"])
def new_card():
    u = User.query.get(current_user.id)

    if request.method == "GET":
        all_cards = Card.query.all()
        return render_template("new_card.html", all_cards=all_cards)
    else:
        topic = request.form["topic"]
        question = request.form["question"]
        plural = request.form["plural"]
        answer = request.form["answer"]

        # if category == 'code':
        #     #using pygments to store code as html elements for highlighting.
        #     question = highlight(question, PythonLexer(), HtmlFormatter())

        card = Card(topic, question, plural, answer)
        db.session.add(card)
        db.session.commit()

        return redirect("/admin")

@app.route("/book/new", methods=["GET", "POST"])
def new_book():
    if request.method == "GET":
        all_books = Book.query.all()
        return render_template("new_book.html", all_books=all_books)
    else:
        # id_book = request.form["id_book"]      
        head = request.form["head"]
        chapter = request.form["chapter"]
        id_level = request.form["id_level"]

        book = Book(head, chapter,id_level)
        db.session.add(book)
        db.session.commit()

        return redirect("/admin")

# All cards
@app.route("/cards")
def show_cards():
    u = User.query.get(current_user.id)
    cards = sorted(u.posts.all(), key=lambda card:card.topic)
    return render_template("cards.html", cards=cards)

# All cards
@app.route("/cards_admin")
def show_cards_admin():
    all_cards = Card.query.all()
    cards = sorted(all_cards, key=lambda card:card.topic)
    return render_template("cards_admin.html", cards=cards)

# ---------------------------------------------------------------
'''
Can refactor this.

Make a form that given a certain request.form (e.g) it would handle the
constraints.

Like if checkbox == category or topic do first querying, else do second.
'''
# Cards by category: General vs Code
@app.route("/cards/category/<string:card_category>")
def get_card_category(card_category):
    u = User.query.get(current_user.id)
    cards = [c for c in u.posts.all() if c.category == card_category]
    return render_template("cards.html", cards=cards)

# Cards by Topic.
@app.route("/cards/topic/<string:card_topic>")
def get_card_topic(card_topic):
    u = User.query.get(current_user.id)
    cards = [c for c in u.posts.all() if c.topic == card_topic]
    print(cards)
    return render_template("cards.html", cards=cards)

# ---------------------------------------------------------------

# Show card's form with card info populated on form based on card id.
@app.route("/cards/<int:card_id>")
def get_card(card_id):
    u = User.query.get(current_user.id)
    card = [c for c in u.posts.all() if c.id == card_id]
    return render_template("show.html", card=card[0])

@app.route("/cards_admin/<int:card_id>")
def get_card_admin(card_id):
    all_cards = Card.query.all()
    cards = sorted(all_cards, key=lambda card:card.topic)
    card = [c for c in cards if c.id == card_id]
    return render_template("show_admin.html", card=card[0])

# Update card.
@app.route("/cards/<int:card_id>", methods=["POST"])
def edit(card_id):
    # TODO
        # Only show cards respective to user.
    card = Card.query.get(card_id)
    card.question = request.form["question"]
    card.answer = request.form["answer"]
    card.topic = request.form["topic"]
    card.plural = request.form["plural"]
    
    db.session.commit()
    return redirect("/cards_admin")

@app.route("/cards/<int:card_id>/delete", methods=["POST"])
def delete_card(card_id):
    # TODO
        # Only show cards respective to user.
    Card.query.filter_by(id=card_id).delete()
    db.session.commit()
    return redirect("/cards_admin")
