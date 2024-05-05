import json
import random
from flask import render_template, request, redirect, jsonify, flash
from flask_login import current_user, login_user, logout_user, login_required
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from app import app, db
from app.models import Card, User, Book, Conection, Level
from app.forms import LoginForm, RegistrationForm
from sqlalchemy import and_


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/login")
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, admin=form.admin.data, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Parabéns, agora você é um usuário!')
        return redirect("/login")
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        user_id = current_user.id
        user = User.query.filter_by(id=user_id).first()
        admin = user.get_admin()
        if admin == 2:
            return redirect("/admin")
        else:
            return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Nome ou senha incorreta','Erro de login')
            return redirect("/login")
        login_user(user, remember=form.remember_me.data)
        admin = user.get_admin()
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
        user_id = current_user.id
        user = User.query.filter_by(id=user_id).first()
        u_id = user.id
        book = Book.query.filter_by(id_book=user.id_book).first()
        cards = Card.query.filter_by(book_id=user.id_book).all()
        for card in cards:
            card_id = card.id
            connection = Conection.query.filter_by(id_student=u_id,id_card=card_id).first()
            if connection is None:
                connection = Conection(u_id,card_id,1)
                db.session.add(connection)
        db.session.commit()
        connections = Conection.query.filter_by(id_student=user.id).filter(Conection.n_answer<4).order_by(Conection.n_answer).first()
        # connections = Conection.query.filter_by(id_student=user.id).filter(Conection.n_answer<4).all()
        # connections_id = [connection.id_card for connection in connections]
        connections_id = connections.id_card
        # cards = Card.query.filter_by(book_id=user.id_book).filter(Card.id.in_(connections_id)).all()
        card = Card.query.filter_by(book_id=user.id_book,id=connections_id).first()
        # card = random.choice(cards)
        total_cards = len(cards)
    except:
        total_cards = 0
        card = None

    return render_template("index.html",user=user, book=book,\
                            card=card,total_cards=total_cards,connections=connections)

@app.route("/<int:u_id><int:card_id>/somar", methods=["POST"])
def somar_conection(u_id,card_id):
    connection = Conection.query.filter_by(id_student=u_id,id_card=card_id).first()
    if connection is not None:
        id_connection = connection.get_id()
        id = Conection.query.get(id_connection)
        id.n_answer += 1
    else:
        connection = Conection(u_id,card_id,1)
        db.session.add(connection)
    db.session.commit()
    return redirect("/")

@app.route("/<int:u_id><int:card_id>/subtrair", methods=["POST"])
def subtrair_conection(u_id,card_id):
    connection = Conection.query.filter_by(id_student=u_id,id_card=card_id).first()
    if connection is not None:
        id_connection = connection.get_id()
        id = Conection.query.get(id_connection)
        id.n_answer = 0
    else:
        connection = Conection(u_id,card_id,0)
        db.session.add(connection)
    db.session.commit()
    return redirect("/")

@app.route("/<int:u_id>/resetar", methods=["POST"])
def resetar_conection(u_id):
    connection = Conection.query.filter_by(id_student=u_id).all()
    if connection is not None:
        for c in connection:
            c.n_answer = 0
    else:
        pass
    db.session.commit()
    return redirect("/")

@app.route("/admin")
@login_required
def admin():
    try:
        cards = Card.query.all()
        books = Book.query.all()
        random_card = random.choice(cards)
        random_book = random.choice(books)
        total_cards = len(cards)
        all_books_len = len(books)
    except:
        random_card = None
        total_cards = 0
        all_books_len = 0
        random_book = 0

    return render_template("admin.html", card=random_card, book=random_book, total_cards=total_cards, all_books_len=all_books_len)


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
        book_id = request.form["book_id"]
        chapter = request.form["chapter"]

        card = Card(topic, question, plural, answer,book_id, chapter)
        db.session.add(card)
        db.session.commit()

        return redirect("/admin")

@app.route("/book/new", methods=["GET", "POST"])
def new_book():
    if request.method == "GET":
        all_books = Book.query.all()
        return render_template("new_book.html", all_books=all_books)
    else:     
        head = request.form["head"]
        chapter = request.form["chapter"]
        id_level = request.form["id_level"]

        book = Book(head, chapter,id_level)
        db.session.add(book)
        db.session.commit()

        return redirect("/admin")
    
@app.route("/level/new", methods=["GET", "POST"])
def new_level():
    if request.method == "GET":
        all_levels = Level.query.all()
        return render_template("new_level.html", all_levels=all_levels)
    else:     
        description = request.form["description"]
        level = Level(description)
        db.session.add(level)
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

# All books
@app.route("/books_admin")
def show_books_admin():
    all_books = Book.query.all()
    books = sorted(all_books, key=lambda book:book.id_book)
    return render_template("books_admin.html", books=books)

# All levels
@app.route("/level_admin")
def show_level_admin():
    all_levels = Level.query.all()
    levels = sorted(all_levels, key=lambda level:level.id_level)
    return render_template("level_admin.html", levels=levels)

# All user
@app.route("/user_admin")
def show_user_admin():
    all_users = User.query.all()
    users = sorted(all_users, key=lambda user:user.id)
    return render_template("user_admin.html", users=users)

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

#Editar carta no menu cards_admin
@app.route("/cards_admin/<int:card_id>")
def get_card_admin(card_id):
    all_cards = Card.query.all()
    cards = sorted(all_cards, key=lambda card:card.topic)
    card = [c for c in cards if c.id == card_id]
    return render_template("show_admin.html", card=card[0])

#Editar livro no menu books_admin
@app.route("/books_admin/<int:id_book>")
def get_book_admin(id_book):
    all_books = Book.query.all()
    books = sorted(all_books, key=lambda book:book.id_book)
    book = [c for c in books if c.id_book == id_book]
    return render_template("show_book_admin.html", book=book[0])

#Editar um nível no menu level_admin
@app.route("/level_admin/<int:id_level>")
def get_level_admin(id_level):
    all_level = Level.query.all()
    levels = sorted(all_level, key=lambda level:level.id_level)
    level = [c for c in levels if c.id_level == id_level]
    return render_template("show_level_admin.html", level=level[0])

#Editar um usuário no menu user_admin
@app.route("/user_admin/<int:id>")
def get_user_admin(id):
    all_users = User.query.all()
    users = sorted(all_users, key=lambda user:user.id)
    user = [c for c in users if c.id == id]
    return render_template("show_user_admin.html", user=user[0])

# Update card.
@app.route("/cards_admin/<int:card_id>", methods=["POST"])
def edit_card(card_id):
    # TODO
        # Only show cards respective to user.
    card = Card.query.get(card_id)
    card.question = request.form["question"]
    card.answer = request.form["answer"]
    card.topic = request.form["topic"]
    card.plural = request.form["plural"]
    
    db.session.commit()
    return redirect("/cards_admin")

# Update book.
@app.route("/books_admin/<int:id_book>", methods=["POST"])
def edit_book(id_book):
    # TODO
        # Only show cards respective to user.
    book = Book.query.get(id_book)
    book.head = request.form["head"]
    book.chapter = request.form["chapter"]
    book.id_level = request.form["id_level"]
    
    db.session.commit()
    return redirect("/books_admin")

# Update level.
@app.route("/level_admin/<int:id_level>", methods=["POST"])
def edit_level(id_level):
    # TODO
        # Only show cards respective to user.
    level = Level.query.get(id_level)
    level.description = request.form["description"]
    db.session.commit()
    return redirect("/level_admin")

# Update user.
@app.route("/user_admin/<int:id>", methods=["POST"])
def edit_user(id):
    user = User.query.get(id)
    user.username = request.form["username"]
    user.email = request.form["email"]
    user.phone = request.form["phone"]
    user.id_level = str(request.form["id_level"])
    user.id_book = str(request.form["id_book"])
    db.session.commit()
    return redirect("/user_admin")

@app.route("/cards_admin/<int:card_id>/delete", methods=["POST"])
def delete_card(card_id):
    # TODO
        # Only show cards respective to user.
    Card.query.filter_by(id=card_id).delete()
    db.session.commit()
    return redirect("/cards_admin")

@app.route("/books_admin/<int:id_book>/delete", methods=["POST"])
def delete_book(id_book):
    Book.query.filter_by(id_book=id_book).delete()
    db.session.commit()
    return redirect("/books_admin")

@app.route("/level_admin/<int:id_level>/delete", methods=["POST"])
def delete_level(id_level):
    Level.query.filter_by(id_level=id_level).delete()
    db.session.commit()
    return redirect("/level_admin")

@app.route("/user_admin/<int:id>/delete", methods=["POST"])
def delete_user(id):
    User.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect("/user_admin")
