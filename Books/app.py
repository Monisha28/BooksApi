from flask import Flask, render_template, request, redirect, url_for
import json
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Book, Author

engine = create_engine('sqlite:///books-collection.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

"""
api functions
"""
from flask import jsonify
import collections
from operator import and_
from sqlalchemy.types import String


def get_books():
    books = session.query(Book).all()
    return jsonify(books=[b.serialize for b in books])

def get_author():
    author = session.query(Author).all()
    return jsonify(author=[a.serialize for a in author])

def add_new_book(title, genre, author_name):
    """Adds a new book to the system"""
    # Get the author's first and last names
    first_name, _, last_name = author_name.partition(" ")

    # Check if book exists
    book = (
        session.query(Book)
        .join(Author)
        .filter(Book.title == title)
        .filter(
            and_(
                Author.first_name == first_name, Author.last_name == last_name
            )
        )
        .one_or_none()
    )

    if book is not None:
        return "Book already exist"

    # Create the new book if needed
    if book is None:
        book = Book(title=title,genre=genre)
    
    # Get the author
    author = (
        session.query(Author)
        .filter(
            and_(
                Author.first_name == first_name, Author.last_name == last_name
            )
        )
        .one_or_none()
    )

    if author is None:
        return "Author name not exist in the table"

    book.author = author
    session.add(book)
    session.commit()

    d = collections.OrderedDict()
    b = session.query(Book).filter_by(title=title).one()    
    d["id"] = b.id
    d["title"] = b.title
    d["genre"] = b.genre
    d["author_id"] = author.author_id
    d["author_firstname"] = author.first_name
    d["author_lastname"] = author.last_name        
    j = json.dumps(d)
    return j

def addAuthor(author_name):
    first_name, _, last_name = author_name.partition(" ")
   
    author = (
        session.query(Author)
        .filter(
            and_(
                Author.first_name == first_name, Author.last_name == last_name
            )
        )
        .one_or_none()
    )

    if author is None:
        author = Author(first_name=first_name, last_name=last_name)
        session.add(author)
        d = collections.OrderedDict()         
        d["author_firstname"] = first_name    
        d["author_lastname"] = last_name 
        j = json.dumps(d)
        return j

    if author is not None:
        return "Author already exist"
    

def get_book(book_id):
    books = session.query(Book).filter_by(id=book_id).one()
    return jsonify(books=books.serialize)

def updateBook(id, title, genre, author):
    updatedBook = session.query(Book).filter_by(id=id).one()
    if title:
        t = session.query(Book).filter_by(title=title).one()
        if t is None:
            updatedBook.title = title
        else:
            return "Book title already exist"
    if genre:
        updatedBook.genre = genre
    if author:
        first_name, _, last_name = author.partition(" ")
        author = (
            session.query(Author)
            .filter(
                and_(
                    Author.first_name == first_name, Author.last_name == last_name
                )
            )
            .one_or_none()
        )
        if author is None:
            return "Author name not exist in the table"
        else:         
            updatedBook.author = author
    
    session.add(updatedBook)
    session.commit()
    return 'Updated a Book with id %s' % id

def deleteBook(id):
    bookToDelete = session.query(Book).filter_by(id=id).one()
    session.delete(bookToDelete)
    session.commit()
    return 'Removed Book with id %s' % id


""" 
Routes 
"""       
@app.route('/')
@app.route('/booksApi', methods=['GET','POST'])
def booksFunction():
    if request.method =='GET':
        return get_books()
    if request.method =='POST':  
        title = request.args.get('title', '')
        genre = request.args.get('genre', '')
        author = request.args.get('author', '')
        return add_new_book(title, genre, author)

@app.route('/author', methods=['GET','POST'])
def authorFunction():
    if request.method =='GET':
        return get_author()
    if request.method =='POST':  
        author = request.args.get('author', '')
    return addAuthor(author)
    
@app.route('/booksApi/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def bookFunctionId(id):
    if request.method == 'GET':
        return get_book(id)

    elif request.method == 'PUT':
        title = request.args.get('title', '')
        genre = request.args.get('genre', '')
        author = request.args.get('author', '')
        return updateBook(id, title, genre, author)

    elif request.method == 'DELETE':
        return deleteBook(id)


if __name__ == '__main__':
    app.debug = True
    app.run(host="localhost", port=8000)