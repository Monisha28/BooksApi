import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()

class Author(Base): 
    __tablename__ = 'author'
    author_id = Column(Integer, primary_key=True)
    first_name = Column(String(250), nullable = False)
    last_name = Column(String(250), nullable = False)
    books = relationship("Book", backref=backref("author"))
 
    @property
    def serialize(self):
        return {
            'author_id':self.author_id,
            'fist_name': self.first_name,
            'last_name': self.last_name,
        }

class Book(Base):
    __tablename__ = 'book'
   
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False, unique= True)
    genre = Column(String(250),nullable=False)
    author_id = Column(Integer, ForeignKey("author.author_id"))
   
    @property
    def serialize(self):
        return {
            'title': self.title,
            'genre': self.genre,
            'author_id':self.author_id,
            'id': self.id,
        }

engine = create_engine('sqlite:///books-collection.db')

Base.metadata.create_all(engine)