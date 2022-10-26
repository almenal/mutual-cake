from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.inspection import inspect

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
    #TODO
    # fromId = Column(ForeignKey("employees.id"))
    # toId   = Column(ForeignKey("employees.id"))
    # cakeId = Column(ForeignKey("cakes.id"))

def populate_dummy_data(engine):
    dbase_has_tables = inspect(engine).get_table_names() != []
    if dbase_has_tables:
        return
    Base.metadata.create_all(engine)
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
                    Ingredient(name = "flour"), Ingredient(name = "cookies"), 
                    Ingredient(name = "wheat"), Ingredient(name = "strawberry")
                    ]
                ),
            Cake(
                name =  "Victoria sponge",
                previewDescription = "Sponge with jam",
                ingredients = [
                    Ingredient(name = "raspberry"), Ingredient(name = "cream"), 
                    Ingredient(name = "eggs"), Ingredient(name = "flour"), 
                    Ingredient(name = "margarine")
                    ]
                ),
            Cake(
                name =  "Carrot cake",
                previewDescription = "Bugs bunnys favourite",
                ingredients = [
                    Ingredient(name = "carrot"), Ingredient(name = "eggs"), 
                    Ingredient(name = "flour"), Ingredient(name = "cinammon"), 
                    Ingredient(name = "nuts")
                    ]
                ),
            Cake(
                name =  "Vegan sponge cake",
                previewDescription = "For that one friend",
                ingredients = [
                    Ingredient(name = "oat"), Ingredient(name = "flour"), 
                    Ingredient(name = "bicarbonate"), Ingredient(name = "strawberry"),
                    ]
                ),
        ]
        session.add_all(employees)
        session.add_all(cakes)
        session.commit()
