import struct
import time

from azure.identity import AzureCliCredential
import pyodbc

from cec_lms_backend.config import CONNECTION_STRING

SQL_COPT_SS_ACCESS_TOKEN = 1256
credential = AzureCliCredential()
token = bytes()
token_expiration = 0
def get_token():
    global token
    global token_expiration
    if token_expiration < int(time.time()) + 60:
        access_token = credential.get_token("https://database.windows.net/.default")
        token_expiration = access_token.expires_on
        b = access_token.token.encode("utf-16-le")
        token = struct.pack(f"<I{len(b)}s", len(b), b)
    return token

def connect() -> pyodbc.Connection:
    return pyodbc.connect(
        CONNECTION_STRING,
        timeout=30,
        attrs_before={SQL_COPT_SS_ACCESS_TOKEN: get_token()}
    )

def ping() -> bool:
    try:
        with connect() as connection:
            return bool(connection.execute("SELECT 1").fetchval())
    except Exception as e:
        print(f"ping failed with error:\n{e}")
        return False