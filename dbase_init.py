#!/usr/bin/env python3
from datetime import datetime, date
import dbase_orm
from dbase_orm import (
    Employee, Ingredient, Cake, Assignment,
    employees_allergies_table, cake_ingredients_table
    )
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect

# Base = declarative_base()
# Base.metadata.create_all(engine)

def populate_dummy_data(engine):
    dbase_has_tables = inspect(engine).get_table_names() != []
    if dbase_has_tables:
        with Session(engine) as session:
            first_row = session.execute(select(Employee)).unique().first()
        if first_row is not None:
            return
    # Base.metadata.create_all(engine)
    with Session(engine) as session:
        # Create all ingredients (fixed vocabulary)
        milk        = Ingredient(name = "milk")
        nuts        = Ingredient(name = "nuts")
        eggs        = Ingredient(name = "eggs")
        chocolate   = Ingredient(name = "chocolate")
        cheese      = Ingredient(name = "cheese")
        cookies     = Ingredient(name = "cookies")
        wheat       = Ingredient(name = "wheat")
        strawberry  = Ingredient(name = "strawberry")
        raspberry   = Ingredient(name = "raspberry")
        cream       = Ingredient(name = "cream")
        margarine   = Ingredient(name = "margarine")
        carrot      = Ingredient(name = "carrot")
        cinammon    = Ingredient(name = "cinammon")
        oat         = Ingredient(name = "oat")
        flour       = Ingredient(name = "flour")
        bicarbonate = Ingredient(name = "bicarbonate")

        # Add employees
        michael = Employee(
            name = "Michael Scott",
            birthday = date(2022, 10, 10),
            allergies = [milk, nuts]
        )
        dwight = Employee(
            name = "Dwight Schrutte",
            birthday = date(2022, 10, 10),
            allergies = [milk, eggs]
        )
        jim = Employee(
            name = "Jim Halpert",
            birthday = date(2022, 10, 10),
            allergies = [chocolate]
        )
        pam = Employee(name = "Pam Beesly")
        session.add_all([michael, dwight, jim, pam])
        session.flush() # ensure employees have id assigned
        
        # Add cakes
        lemon = Cake(
            name =  "Lemon cheesecake - strawberry",
            previewDescription = "A cheesecake made of lemon",
            ingredients = [
                cheese, eggs, 
                flour, cookies, 
                wheat, strawberry
                ]
            )
        victoria = Cake(
            name =  "Victoria sponge",
            previewDescription = "Sponge with jam",
            ingredients = [
                raspberry, cream, 
                eggs, flour, 
                margarine
                ]
            )
        carrot = Cake(
            name =  "Carrot cake",
            previewDescription = "Bugs bunnys favourite",
            ingredients = [
                carrot, eggs, 
                flour, cinammon, 
                nuts
                ]
            )
        vegan = Cake(
            name =  "Vegan sponge cake",
            previewDescription = "For that one friend",
            ingredients = [
                oat, flour, 
                bicarbonate, strawberry,
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
