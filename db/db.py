import sqlite3
from models.models import Model_Type
from typing import List
from models.models import Strategy


def get_connection():
    return sqlite3.connect("db/v1.db")

def create_script() -> None:
    table_query = "CREATE TABLE IF NOT EXISTS objects (" \
                        "id TEXT PRIMARY KEY," \
                        "kind TEXT NOT NULL," \
                        "name TEXT NOT NULL," \
                        "json TEXT NOT NULL" \
                    ")"
    
    with get_connection() as conn:
        conn.execute(table_query)

def insert(obj: Model_Type) -> None:
    """Pass one of our models in and save as JSON in DB"""
    
    insert_query = "INSERT INTO objects (id, kind, name, json) VALUES (?, ?, ?, ?)"
    
    json = obj.model_dump_json()
    id = obj.id
    kind = obj.kind
    name = obj.name

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(insert_query, (str(id), kind, name, json))

def update(obj: Model_Type) -> None:
    """ Update an Objects Record in the DB"""
    update_query = "UPDATE objects " \
                   "SET kind = ?, json = ?, name = ?" \
                   "WHERE id = ?"
    
    kind = obj.kind
    json = obj.model_dump_json()
    id = obj.id
    name = obj.name

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(update_query, (kind, json, name, str(id)))


def get_strategy_names() -> List[str]:
    """ Return a list of all strategy names in the DB"""
    
    query = "SELECT name FROM objects WHERE kind = 'strategy'"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        stuff = cursor.fetchall()

    return stuff

def get_strategy(name: str) -> Strategy:
    """ Fetch a record from DB, Hydrate and return 
    Args:
        name: name of the strategy """
    query = "SELECT * from objects WHERE name = ?"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (name,))
        strategy = cursor.fetchone()
        return Strategy.model_validate_json(strategy[3])
