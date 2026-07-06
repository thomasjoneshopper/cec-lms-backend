from .connection import connect

def get_id(employee_number: str, name: str) -> int:
    """
    Returns `user_id`, updating `Users` if entry does not exist.

    `employee_number` is used for matching; `name` only needed if insert
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
                INSERT INTO Users (employee_number, name) 
                OUTPUT INSERTED.user_id
                VALUES (?, ?)
                """, employee_number, name
            )
            user_id = cursor.fetchval()
            connection.commit()
    
    return user_id

def get_role(user_id: int) -> bool:
    """
    Returns the role of user with specified `user_id` if exists

    TODO: set up role field
    """

    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT 1 
            FROM Users
            WHERE user_id = ?
            """, user_id
        )
        row = cursor.fetchone()
        if row is None: return False
        return True
    
def get_entry(user_id: int) -> dict | None:
    """
    Returns dict of fields for user with specified `user_id` if exists
    """
    FIELDS = ("employee_number", "name")

    with connect() as connection:
        cursor = connection.cursor()
        
        cursor.execute(
            f"""
            SELECT {", ".join(FIELDS)} 
            FROM Users
            WHERE user_id = ?
            """, user_id
        )
        row = cursor.fetchone()
        if row is None: return None
        return {field: getattr(row, field, None) for field in FIELDS}
