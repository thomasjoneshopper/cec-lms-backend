from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from os import environ
import pyodbc
import struct

load_dotenv()

def db_connect() -> pyodbc.Connection:
    CONNECTION_STRING = environ["CONNECTION_STRING"]
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    
    token = (
        AzureCliCredential()
        .get_token("https://database.windows.net/.default")
        .token.encode("utf-16-le")
    )
    exptoken = struct.pack(f"<I{len(token)}s", len(token), token)

    connection = pyodbc.connect(
        CONNECTION_STRING,
        timeout=30,
        attrs_before={SQL_COPT_SS_ACCESS_TOKEN: exptoken}
    )

    return connection

if __name__ == "__main__":
    with db_connect() as connection:
        print(connection.execute("SELECT * FROM dbo.Courses").fetchall())