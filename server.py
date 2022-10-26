from fastapi import FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column,String,Integer,Float
import dbase_ops

# connect to database
engine = create_engine('sqlite:///data/db.sqlite3')
dbase_ops.populate_dummy_data(engine)

app = FastAPI()

@app.get("/employees/{employee_id}")
def fetch_employee_data(employee_id:int):
    """#TODO Use SQLAlchemy to retrieve employee data"""
    pass