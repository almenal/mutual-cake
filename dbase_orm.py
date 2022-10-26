from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

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
    allergies = relationship("Ingredient", secondary = employees_allergies_table)

class Cake(Base):
    __tablename__ = "cakes"
    id   = Column(Integer, primary_key = True)
    name = Column(String)
    previewDescription = Column(String)
    ingredients = relationship("Ingredient", secondary = cake_ingredients_table)

class Ingredient(Base):
    __tablename__ = "ingredients"
    id   = Column(Integer, primary_key = True)
    name = Column(String)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key = True)
    fromId = Column(ForeignKey("employees.id"))
    toId   = Column(ForeignKey("employees.id"))
    cakeId = Column(ForeignKey("cakes.id"))
