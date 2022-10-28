#!/usr/bin/env python3
import datetime
from typing import List
from fastapi import FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, update
from dbase_init import populate_dummy_data
from dbase_orm import Employee, Cake, Ingredient, Assignment
from pydantic import BaseModel

# connect to database
engine = create_engine('sqlite:///data/db.sqlite3', echo=True)
populate_dummy_data(engine)

app = FastAPI()

# region Get joined info  ------------------

@app.get("/ingredients/all")
def list_all_allergens():
    with Session(engine) as sess:
        res = list(set([
            ingredient.capitalize() for ingredient in \
            sess.scalars(select(Ingredient.name)).unique().all()
        ]))
        return res

# endregion -------------------------------------

# region Query items by item id -------------------------------------

@app.get("/employees/{employee_id}")
def fetch_employee_data(employee_id:int):
    ""
    with Session(engine) as sess:
        return  (
            sess.query(Employee)
            .filter(Employee.id == employee_id)
            .one_or_none()
        )

@app.get("/cakes/{cake_id}")
def fetch_cake_data(cake_id:int):
    ""
    with Session(engine) as sess:
        return  (
            sess.query(Cake)
            .filter(Cake.id == cake_id)
            .one_or_none()
        )

@app.get("/ingredients/{ingredient_id}")
def fetch_ingredient_data(ingredient_id:int):
    ""
    with Session(engine) as sess:
        return (
            sess.query(Ingredient)
            .filter(Ingredient.id == ingredient_id)
            .one_or_none()
        )

@app.get("/assignments/{assignment_id}")
def fetch_assignment_data(assignment_id:int):
    ""
    with Session(engine) as sess:
        return (
            sess.query(Assignment)
            .filter(Assignment.id == assignment_id)
            .one_or_none()
        )

# endregion -------------------------------------

# region Get joined info  ------------------

@app.get("/employees/{employee_id}/assignments/employee")
def fetch_assigned_employee(employee_id:int):
    ""
    with Session(engine) as sess:
        return (
            sess.scalars(
                select(Employee.name)
                .select_from(Assignment)
                .join(Employee, Employee.id == Assignment.toId)
                .where(Assignment.fromId == employee_id)
            ).one_or_none()
        )

@app.get("/employees/{employee_id}/assignments/cake")
def fetch_assigned_cake(employee_id:int):
    "Return just cake name as opposed to full description"
    with Session(engine) as sess:
        return (
            sess.scalars(
                select(Cake.name)
                .select_from(Assignment)
                .join(Cake, Cake.id == Assignment.cakeId)
                .where(Assignment.fromId == employee_id)
            ).one_or_none()
        )

@app.get("/employees/{employee_id}/assignments/cake/details")
def fetch_assigned_cake_details(employee_id:int):
    "Return full description as opposed to just cake name"
    #TODO Include ingredients
    with Session(engine) as sess:
        return (
            sess.scalars(
                select(Cake)
                .select_from(Assignment)
                .join(Cake, Cake.id == Assignment.cakeId)
                .where(Assignment.fromId == employee_id)
            ).one_or_none()
        )

# endregion -------------------------------------

# region Ingest data from POST ------------------

class UserInfo(BaseModel):
    id: int = None
    name: str
    birthday: datetime.date
    allergies: List[str]

@app.post("/employees/")
def sign_up_user(new_user: UserInfo):
    with Session(engine) as sess:
        sess.add(
            Employee(
                name = new_user.name,
                # birthday = datetime.datetime.strptime(new_user.dob, "%Y-%m-%d"),
                allergies = [
                    Ingredient(name = ingr) for ingr in new_user.allergies
                ]
            )
        )
        sess.commit()
    # TODO get users without assignment and assign missing ones

# endregion -------------------------------------

# region Ammend data via PUT ------------------

@app.put("/employees/{employee_id}")
def ammend_user_details(employee_id:int, new_details: UserInfo):
    with Session(engine) as sess:
        sess.execute(
            update(Employee)
            .where(Employee.id == employee_id)
            .values(**new_details.dict())
        )
        sess.commit()

# endregion -------------------------------------
