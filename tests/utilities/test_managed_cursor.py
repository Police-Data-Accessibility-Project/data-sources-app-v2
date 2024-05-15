from utilities.managed_cursor import managed_cursor
import uuid

SQL_TEST = """
    INSERT INTO test_table (name) VALUES (%s)
"""

class TestException(Exception):

def test_managed_cursor_rollback(test_db_connection):
    """
    When an exception occurs,
    the managed_cursor will rollback any changes made
    and close the cursor
    """
    name = str(uuid.uuid4())
    try:
        with managed_cursor(test_db_connection) as cursor:
            cursor.execute(SQL_TEST, name)
            raise TestException
    except TestException:
        pass
    assert cursor.closed == 1, "Cursor should be closed after exiting context manager"
    cursor = test_db_connection.cursor()
    cursor.execute("SELECT * FROM test_table WHERE name = '%s'", name)
    result = cursor.fetchall()
    cursor.close()
    assert (len(result) == 0,
           "Any transactions should be rolled back when an "
           "exception is raised in the context of the managed cursor")

def test_managed_cursors_happy_path(test_db_connection):
    """
    When no exception occurs,
    the changes will be committed and the cursor will be closed
    """
    name = str(uuid.uuid4())
    with managed_cursor(test_db_connection) as cursor:
        cursor.execute(SQL_TEST, name)
    assert cursor.closed == 1, "Cursor should be closed after exiting context manager"
    cursor = test_db_connection.cursor()
    cursor.execute("SELECT * FROM test_table WHERE name = '%s'", name)
    result = cursor.fetchall()
    cursor.close()
    assert (len(result) == 1,
           "Any transactions should persist in the absence of an exception "
           "raised in the context of the managed cursor")