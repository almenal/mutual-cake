from click import echo
from fastapi import FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column,String,Integer,Float
import dbase_ops
from dbase_ops import Employee

# connect to database
engine = create_engine('sqlite:///data/db.sqlite3', echo=True)
dbase_ops.populate_dummy_data(engine)

app = FastAPI()

@app.get("/employees/{employee_id}")
def fetch_employee_data(employee_id:int):
    """#TODO Use SQLAlchemy to retrieve employee data"""
    with Session(engine) as sess:
        return sess.query(Employee).filter(Employee.id == employee_id).one()
