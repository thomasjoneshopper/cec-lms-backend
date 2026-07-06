import struct

from azure.identity import AzureCliCredential
import pyodbc

from cec_lms_backend.config import CONNECTION_STRING


def connect() -> pyodbc.Connection:
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


