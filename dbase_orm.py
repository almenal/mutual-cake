#!/usr/bin/env python3
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship

data_folder = Path("data")
data_folder.mkdir(parents=True, exist_ok=True)
engine = create_engine('sqlite:///data/db.sqlite3', echo=True)
Base = declarative_base()

employees_allergies_table = Table(
    "employees_allergies",
    Base.metadata,
    Column("user_id",     ForeignKey("employees.id")),
    Column("allergen_id", ForeignKey("ingredients.id")),
)

cake_ingredients_table = Table(
    "cake_ingredients",
    Base.metadata,
    Column("cake_id",       ForeignKey("cakes.id")),
    Column("ingredient_id", ForeignKey("ingredients.id")),
)

class Employee(Base):
    __tablename__ = "employees"
    id   = Column(Integer, primary_key = True)
    name = Column(String)
    birthday = Column(Date)
    allergies = relationship("Ingredient",
                             secondary=employees_allergies_table,
                             lazy = 'joined')
    
    def __repr__(self):
        return (f"Employee(id={self.id!r}, dob={self.birthday!s}, "
                f" name={self.name!r}, allergies={self.allergies!r})")

class Cake(Base):
    __tablename__ = "cakes"
    id   = Column(Integer, primary_key = True)
    name = Column(String)
    previewDescription = Column(String)
    ingredients = relationship("Ingredient",
                                secondary = cake_ingredients_table,
                                lazy = 'joined')

    def __repr__(self):
        return (f"Cake(id={self.id!r}, name={self.name!r}, " 
                f"ingredeints={self.ingredients!r})")

class Ingredient(Base):
    __tablename__ = "ingredients"
    id   = Column(Integer, primary_key = True)
    name = Column(String)

    def __repr__(self):
        return f"Ingredient(id={self.id!r}, name={self.name!r})"

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key = True)
    fromId = Column(ForeignKey("employees.id"))
    toId   = Column(ForeignKey("employees.id"))
    cakeId = Column(ForeignKey("cakes.id"))
    def __repr__(self):
        return (f"Assignment(Employee[{self.fromId!r}] bakes "
                f"Cake[{self.cakeId}] for Employee[{self.toId!r}])")

# NOTE: Make sure this does not delete dbase records
Base.metadata.create_all(engine)
