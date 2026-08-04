from cec_lms_backend.db.connection import connect
from cec_lms_backend.db.utils import fetch_dict

def get_id(employee_number: str, full_name: str) -> int:
    """
    Returns `user_id`, updating `Users` if entry does not exist.

    `employee_number` is used for matching; `full_name` only needed if insert
    """

    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT user_id FROM dbo.Users 
            WHERE employee_number = ?
            """, employee_number
        )

        user_id = cursor.fetchval()
        if not user_id:
            cursor.execute(
                """
                INSERT INTO Users (employee_number, full_name) 
                OUTPUT INSERTED.user_id
                VALUES (?, ?)
                """, employee_number, full_name
            )
            user_id = cursor.fetchval()
            connection.commit()
    
    return user_id

def get_role(user_id: int) -> str | None:
    """
    Returns the role of user with specified `user_id` if exists
    """

    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT role_title
            FROM dbo.Users
            WHERE user_id = ?;
            """, user_id
        )
        return cursor.fetchval()
    
def get_entry(user_id: int) -> dict | None:
    """
    Returns dict of fields for user with specified `user_id` if exists
    """

    with connect() as connection:
        cursor = connection.execute(
            """
            SELECT employee_number, full_name, role_title
            FROM dbo.Users
            WHERE user_id = ?;
            """, user_id
        )
        
        return fetch_dict(cursor)
        
