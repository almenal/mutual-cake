import json
from turtle import back
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    id   = Column(Integer, primary_key = True)
    name = Column(String),
    allergies = relationship("Ingredient", back_populates = "Employee")

class Cake(Base):
    __tablename__ = "cakes"
    id   = Column(Integer, primary_key = True)
    name = Column(String),
    previewDescription = Column(String)
    ingredients = relationship("Ingredient", back_populates = "Cake")

class Ingredient(Base):
    __tablename__ = "ingredients"
    id   = Column(Integer, primary_key = True)
    name = Column(String)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key = True)
    fromId = relationship("Employee", back_populates = "Assignments")
    toId   = relationship("Employee", back_populates = "Assignments")
    cakeId = relationship("Cake",     back_populates = "Assignments")

