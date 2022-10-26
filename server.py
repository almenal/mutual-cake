from click import echo
from fastapi import FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column,String,Integer,Float
import dbase_ops
from dbase_ops import Employee, Cake, Ingredient, Assignment

# connect to database
engine = create_engine('sqlite:///data/db.sqlite3', echo=True)
dbase_ops.populate_dummy_data(engine)

app = FastAPI()

# region query items by item id -------------------------------------

@app.get("/employees/{employee_id}")
def fetch_employee_data(employee_id:int):
    ""
    with Session(engine) as sess:
        return sess.query(Employee).filter(Employee.id == employee_id).one()

@app.get("/cakes/{cake_id}")
def fetch_cake_data(cake_id:int):
    ""
    with Session(engine) as sess:
        return sess.query(Cake).filter(Cake.id == cake_id).one()

@app.get("/ingredients/{ingredient_id}")
def fetch_employee_data(ingredient_id:int):
    ""
    with Session(engine) as sess:
        return sess.query(Ingredient).filter(Ingredient.id == ingredient_id).one()

# endregion -------------------------------------