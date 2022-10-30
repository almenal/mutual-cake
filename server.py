#!/usr/bin/env python3
import datetime
import logging
from typing import List
from fastapi import FastAPI
from sqlalchemy.orm import Session, aliased
from sqlalchemy import create_engine, select, update
from dbase_init import populate_dummy_data
from dbase_orm import Employee, Cake, Ingredient, Assignment, engine
from pydantic import BaseModel

# connect to database
populate_dummy_data(engine)
logging.basicConfig(
    format = "[{asctime}][{name:^10}][{levelname:^7}] {msg}",
    style = "{",
    force = True,
    level = logging.INFO
)
logger = logging.getLogger('my-server')
app = FastAPI()

# region pydantic models -------------------------------------

class UserInfo(BaseModel):
    id: int = None
    name: str = None
    birthday: datetime.date = None
    allergies: List[str] = None

class CakeInfo(BaseModel):
    id: int = None
    name: str = None
    previewDescription: str = None
    ingredients: List[str] = None

# endregion -------------------------------------


# region List all entries of one table  ------------------

@app.get("/ingredients/all")
def list_all_allergens():
    with Session(engine) as sess:
        res = sorted(set([
            ingredient.capitalize() for ingredient in \
            sess.scalars(select(Ingredient.name)).unique().all()
        ]))
        return res

@app.get("/employees/all")
def list_all_employees():
    with Session(engine) as sess:
        all_employees = sess.scalars(select(Employee)).unique().all()
        res = sorted(all_employees, key=lambda emp: emp.name)
        return res

@app.get("/cakes/all")
def list_all_cakes():
    with Session(engine) as sess:
        all_cakes = sess.scalars(select(Cake)).unique().all()
        res = sorted(all_cakes, key=lambda cake: cake.name)
        return res

# endregion -------------------------------------


# region Query items by item id -------------------------------------

@app.get("/employees/{employee_id}")
def fetch_employee_data(employee_id:int):
    ""
    with Session(engine) as sess:
        return (
            sess.scalars(
                select(Employee)
                .where(Employee.id == employee_id)
            ).unique().one_or_none()
        )

@app.get("/employees/name/{employee_name}")
def fetch_employee_data_by_name(employee_name: str):
    ""
    with Session(engine) as sess:
        return (
            sess.scalars(
                select(Employee)
                .where(Employee.name == employee_name)
            ).unique().one_or_none()
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
    with Session(engine) as sess:
        return (
            sess.scalars(
                select(Cake)
                .select_from(Assignment)
                .join(Cake, Cake.id == Assignment.cakeId)
                .where(Assignment.fromId == employee_id)
            ).unique().one_or_none()
        )

# endregion -------------------------------------


# region Ingest data from POST ------------------

@app.post("/employees/")
def sign_up_user(new_user: UserInfo):
    with Session(engine) as sess:
        sess.add(
            Employee(
                name = new_user.name,
                birthday = new_user.birthday,
                allergies = [
                    Ingredient(name = ingr) for ingr in new_user.allergies
                ]
            )
        )
        sess.commit()

@app.post("/cakes/")
def submit_cake(new_cake: CakeInfo):
    with Session(engine) as sess:
        ingredients_lower = [ingr.lower() for ingr in new_cake.ingredients]
        ingredients = sess.scalars(
            select(Ingredient)
            .where(Ingredient.name.in_(ingredients_lower))
        ).unique().all()
        new_cake = Cake(
            name               = new_cake.name,
            previewDescription = new_cake.previewDescription,
            ingredients        = ingredients
            )
        sess.add(new_cake)
        sess.commit()

# endregion -------------------------------------


# region Ammend data via PUT ------------------

@app.put("/employees/{employee_id}/update")
def ammend_user_details(employee_id:int, new_details: UserInfo):
    """The assumption for the allergens is that the ingredients is a finite
    vocabulary with no option to add new items (for now)"""
    logger.info(f"new_details.dict(): '{new_details.dict()}'")
    new_details_ = {
        k:v for k,v in new_details.dict().items() 
        if v is not None and k != 'allergies'
    }
    logger.info(f"new_details_: '{new_details_}'")
    
    with Session(engine) as sess:
        # Update name, dob -----------
        if new_details_ != {}:
            sess.execute(
                update(Employee)
                .where(Employee.id == employee_id)
                .values(**new_details_)
            )
            sess.flush()
        # Update allergies -----------
        user = sess.scalars(
            select(Employee).where(Employee.id == employee_id)
        ).unique().one()
        if new_details.allergies is not None:
            new_allergies = [x.lower() for x in new_details.allergies]
            new_allergies_records = sess.scalars(
                select(Ingredient)
                .where(Ingredient.name.in_(new_allergies))
            ).unique().all()
            user.allergies = new_allergies_records
        
        sess.commit()

@app.put("/employees/{employee_id}/new_patner/{partner_id}")
def choose_new_partner(employee_id:int, partner_id:int):
    with Session(engine) as sess:
        existing_assignment = sess.scalars(
            select(Assignment)
            .where(Assignment.fromId == employee_id)
        ).one_or_none()
        
        if existing_assignment is not None:
            existing_assignment.toId = partner_id
        else:
            sess.add(
                Assignment(
                    fromId = employee_id,
                    toId = partner_id,
                    cakeId = None #FIXME
                )
            )
        sess.commit()

@app.put("/employees/{employee_id}/new_cake/{cake_id}")
def choose_new_cake(employee_id:int, cake_id:int):
    with Session(engine) as sess:
        existing_assignment = sess.scalars(
            select(Assignment)
            .where(Assignment.fromId == employee_id)
        ).one_or_none()
        
        if existing_assignment is not None:
            existing_assignment.cakeId = cake_id
        else:
            sess.add(
                Assignment(
                    fromId = employee_id,
                    toId = None, 
                    cakeId = cake_id
                )
            )
        sess.commit()

# endregion -------------------------------------


# region DELETE data ------------------

@app.delete("/employees/{employee_id}")
def delete_user(employee_id: int):
    with Session(engine) as sess:
        user = sess.scalars(
                select(Employee).where(Employee.id == employee_id)
        ).unique().one()
        sess.delete(user)
        sess.commit()

# endregion -------------------------------------
