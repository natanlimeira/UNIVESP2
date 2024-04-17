from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Integer)
    id_level = db.Column(db.Integer, db.ForeignKey('level.id_level'), default=1) #id_nivel
    id_book = db.Column(db.Integer, db.ForeignKey('book.id_book'),default=1) #id_livro

    def __init__(self, username, email, admin, phone):
       self.username = username
       self.email = email
       self.admin = admin
       self.phone = phone

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return self.id

    def get_username(self):
        return self.username

    def get_admin(self):
        return self.admin
    
    def get_level(self):
        return self.id_level
    
    def set_level(self, level):
        self.id_level = level

    def get_book(self):
        return self.id_book
    
    def set_book(self, book):
        self.id_book = book

class Card(db.Model):
    id = db.Column(db.Integer, primary_key = True) #id_vocabuloi
    category = db.Column(db.String(100), default=0)
    topic = db.Column(db.String(100)) #genero
    question = db.Column(db.String(100000)) #voc_descricao
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    plural = db.Column(db.String(100000)) #plural
    answer = db.Column(db.String(100000)) #traducao
    book_id = db.Column(db.Integer, db.ForeignKey('book.id_book')) #id_livro
    chapter = db.Column(db.Integer, db.ForeignKey('book.chapter')) #capitulo
   
    def __init__(self, topic, question, plural, answer,book_id, chapter):
       self.topic = topic
       self.question = question
       self.answer = answer
       self.plural = plural
       self.book_id = book_id
       self.chapter = chapter

    def get_id(self):
        return self.id
   
class Book(db.Model):
   id_book = db.Column(db.Integer, primary_key = True) #id_livro
   head = db.Column(db.String(1000)) #Título
   chapter = db.Column(db.Integer()) #capítulo
   id_level = db.Column(db.Integer, db.ForeignKey('level.id_level')) #id_nivel

   def __init__(self, head, chapter, id_level):
       self.head = head
       self.chapter = chapter
       self.id_level = id_level

class Level(db.Model):
   id_level = db.Column(db.Integer, primary_key = True) #id_nivel
   description = db.Column(db.Integer()) #Descrição

   def __init__(self, description):
       self.description = description

class Conection(db.Model):
    id = db.Column(db.Integer, primary_key = True) #id_conection
    id_student = db.Column(db.Integer, db.ForeignKey('user.id')) #id_estudante
    id_card = db.Column(db.Integer, db.ForeignKey('card.id')) #id_card
    n_answer = db.Column(db.Integer()) #Número de respostas corretas

    def __init__(self, id_student,id_card,n_answer=0):
       self.id_student = id_student
       self.id_card = id_card
       self.n_answer = n_answer

    def get_id(self):
        return self.id

@login.user_loader
def load_user(id):
    return User.query.get(int(id))