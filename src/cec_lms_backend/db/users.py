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


def exists(user_id: str):
    """
    Checks if user with specified `user_id` exists in `Users`

    should return role information later
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
        return cursor.fetchone() is not None
