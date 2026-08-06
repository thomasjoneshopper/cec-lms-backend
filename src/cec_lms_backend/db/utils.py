from pyodbc import Cursor

def fetch_dict(cursor: Cursor):
    row = cursor.fetchone()
    if row is None: return None
    columns = (column[0] for column in cursor.description)
    return dict(zip(columns, row))