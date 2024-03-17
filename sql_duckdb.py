import duckdb
from duckdb import DuckDBPyConnection, ConnectionException
from pathlib import Path
from sqlalchemy import text
from pandas import DataFrame


def connect_db(database:str) -> DuckDBPyConnection:
    """ create a database connection to the duckDB database
    specified by the db_file
:param db_file: database file
:return: Connection object or None
"""
    conn = None
    if database.endswith(".db"):
        try:
            conn = duckdb.connect(database=database, read_only=False)
            return conn
        except Exception as e:
            return e

def create_table(conn: DuckDBPyConnection, table: str):
    """Cria a tabela se ela não existir
    Informar colunas com tipo de dado
    Ex: columns=["id INTEGER", "name VARCHAR"] """
    try:    
        conn.sql(f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM df")
        conn.sql(f"INSERT INTO {table} SELECT * FROM df")
    except Exception as e:
        return(e)
    # query=f"CREATE TABLE IF NOT EXISTS {table} {*columns,}".replace("'","") 
    # if conn:
    #     try:
    #         conn.sql(query)
    #         conn.table(f"{table}").show()
    #     except Exception as e:
    #         print(e)
    #         return e


def list_database() -> list:
    path=Path("./")
    db_list =[db.name for db in path.glob("*.db")]
    return db_list

def list_tables(conn: DuckDBPyConnection, database: str) -> list[str]:
    tables = [tb[0] for tb in  conn.sql("SHOW TABLES").fetchall()]
    return tables

# if __name__=="__main__":
# #     list_database()
#     conn = connect_db(database="duckdb.db")
#     print(list_tables(conn,"duckdb.db"))
    # create_table(conn=conn, table="rh", columns=["id INTEGER","name VARCHAR","wage FLOAT"])