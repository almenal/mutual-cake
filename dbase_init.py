#!/usr/bin/env python3
from datetime import datetime, date
import dbase_orm
from dbase_orm import (
    Employee, Ingredient, Cake, Assignment,
    employees_allergies_table, cake_ingredients_table
    )
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect

# Base = declarative_base()
# Base.metadata.create_all(engine)

def populate_dummy_data(engine):
    # dbase_has_tables = inspect(engine).get_table_names() != []
    # if dbase_has_tables:
    #     return
    # Base.metadata.create_all(engine)
    with Session(engine) as session:
        # Add employees
        michael = Employee(
            name = "Michael Scott",
            birthday = date(2022, 10, 10),
            allergies = [Ingredient(name = "milk"), Ingredient(name = "nuts")]
        )
        dwight = Employee(
            name = "Dwight Schrutte",
            birthday = date(2022, 10, 10),
            allergies = [Ingredient(name = "milk"), Ingredient(name = "eggs")]
        )
        jim = Employee(
            name = "Jim Halpert",
            birthday = date(2022, 10, 10),
            allergies = [Ingredient(name = "chocolate")]
        )
        pam = Employee(name = "Pam Beesly")
        session.add_all([michael, dwight, jim, pam])
        session.flush() # ensure employees have id assigned
        
        # Add cakes
        lemon = Cake(
            name =  "Lemon cheesecake - strawberry",
            previewDescription = "A cheesecake made of lemon",
            ingredients = [
                Ingredient(name = "cheese"), Ingredient(name = "eggs"), 
                Ingredient(name = "flour"), Ingredient(name = "cookies"), 
                Ingredient(name = "wheat"), Ingredient(name = "strawberry")
                ]
            )
        victoria = Cake(
            name =  "Victoria sponge",
            previewDescription = "Sponge with jam",
            ingredients = [
                Ingredient(name = "raspberry"), Ingredient(name = "cream"), 
                Ingredient(name = "eggs"), Ingredient(name = "flour"), 
                Ingredient(name = "margarine")
                ]
            )
        carrot = Cake(
            name =  "Carrot cake",
            previewDescription = "Bugs bunnys favourite",
            ingredients = [
                Ingredient(name = "carrot"), Ingredient(name = "eggs"), 
                Ingredient(name = "flour"), Ingredient(name = "cinammon"), 
                Ingredient(name = "nuts")
                ]
            )
        vegan = Cake(
            name =  "Vegan sponge cake",
            previewDescription = "For that one friend",
            ingredients = [
                Ingredient(name = "oat"), Ingredient(name = "flour"), 
                Ingredient(name = "bicarbonate"), Ingredient(name = "strawberry"),
                ]
            )
        cakes = [lemon, victoria, carrot, vegan]
        session.add_all(cakes)
        session.flush() # ensure cakes have id assigned

        # Now that both employees and cakes have ids, create assignments
        assignments = [
            Assignment(fromId = michael.id, toId =  dwight.id, cakeId = vegan.id),
            Assignment(fromId = dwight.id, toId = pam.id, cakeId = lemon.id)
        ]
        session.add_all(assignments)

        # Commit all
        session.commit()
