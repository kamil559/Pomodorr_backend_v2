import pytest
from pony.orm import sql_debug, BindingError

from models import db


def setup_database() -> None:
    sql_debug(True)
    try:
        db.bind('sqlite', ':memory:')
    except BindingError:
        pass
    else:
        db.generate_mapping(check_tables=False)
    db.create_tables()


@pytest.fixture()
def setup_teardown_tables() -> None:
    setup_database()
    try:
        yield
    finally:
        db.drop_all_tables(with_all_data=True)
        db.disconnect()
