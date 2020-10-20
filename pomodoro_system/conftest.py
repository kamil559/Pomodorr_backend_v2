import pytest
from pony.orm import BindingError

from models import db


@pytest.fixture(scope='class')
def setup_teardown_tables() -> None:
    try:
        db.bind(provider='sqlite', filename=':memory:', create_db=True)
    except BindingError:
        pass
    else:
        db.generate_mapping(create_tables=True)
        yield
        db.drop_all_tables(with_all_data=True)
        db.disconnect()
        db.provider = db.schema = None
