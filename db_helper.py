import os
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy.engine import URL
from langchain.globals import set_verbose

set_verbose(True)
load_dotenv()
username=os.environ["DB_USERNAME"]
password=os.environ["DB_PASSWORD"]
host=os.environ["DB_HOST"]
database=os.environ["DB_NAME"]


def get_db_connection_string():

    params = f"Driver={{ODBC Driver 18 for SQL Server}};Server={host};Database={database};Uid={username};Pwd={password};"
    conn_str = URL.create("mssql+pyodbc",query={"odbc_connect": params})
    return conn_str

def get_db():
    conn_str = get_db_connection_string()
    uri = conn_str.__to_string__(hide_password=False)
    # ONLY if you have custom schema like 'SalesLT', otherwise dont pass ** at all.
    db = SQLDatabase.from_uri(uri, **{'schema': 'SalesLT'})
    return db

  
