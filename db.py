from tabulate import tabulate
import sqlite3

def get_db() -> sqlite3.Connection:
    connection = sqlite3.connect("temp.db")
    connection.execute()
    return 

def init():
    with get_db() as connection: 
        cursor = connection.cursor()
        cursor.executescript(open("schema.sql").read())
        connection.commit()


# cursor.execute(
#     """
#     INSERT INTO UserParagraphCompletion (user_id, module_id, paragraph_number)

#     """
# )


# def upsert_user(employee_number, name):
#     cursor.

def sprint_table(table):
    print(f"{table}:\n")
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        headers = [description[0] for description in cursor.description]
        return tabulate(rows, headers=headers)


def main():
    init()

    for table in ("Users", "Modules", "UserParagraphCompletion"):
        print(f"{sprint_table(table)}\n\n")

if __name__ == "__main__":
    main()