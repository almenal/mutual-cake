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

def populate_dummy_data(engine):
    with Session(engine) as session:
        employees = [
            Employee(name = "Michael Scott", 
                    allergies = [Ingredient(name = "milk"), Ingredient(name = "nuts")]),
            Employee(name = "Dwight Schrutte", 
                    allergies = [Ingredient(name = "milk"), Ingredient(name = "eggs")]),
            Employee(name = "Jim Halpert", 
                    allergies = [Ingredient(name = "chocolate")]),
            Employee(name = "Pam Beesly")
        ]
        cakes = [
            
            Cake(
                name =  "Lemon cheesecake - strawberry",
                previewDescription = "A cheesecake made of lemon",
                ingredients = [
                    Ingredient(name = "cheese"), Ingredient(name = "eggs"), 
                    Ingredient(name = "flour"), Ingredient("cookies"), 
                    Ingredient("wheat"), Ingredient("strawberry")
                    ]
                ),
            Cake(
                name =  "Victoria sponge",
                previewDescription = "Sponge with jam",
                ingredients = [
                    Ingredient(name = "raspberry"), Ingredient(name = "cream"), 
                    Ingredient(name = "eggs"), Ingredient("flour"), 
                    Ingredient("margarine")
                    ]
                ),
            Cake(
                name =  "Carrot cake",
                previewDescription = "Bugs bunnys favourite",
                ingredients = [
                    Ingredient(name = "carrot"), Ingredient(name = "eggs"), 
                    Ingredient(name = "flour"), Ingredient("cinammon"), 
                    Ingredient("nuts")
                    ]
                ),
            Cake(
                name =  "Vegan sponge cake",
                previewDescription = "For that one friend",
                ingredients = [
                    Ingredient(name = "oat"), Ingredient(name = "flour"), 
                    Ingredient(name = "bicarbonate"), Ingredient("strawberry"),
                    ]
                ),
        ]
        session.add_all(employees)
        session.add_all(cakes)
        session.commit()
