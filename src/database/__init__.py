from sqlmodel import create_engine, SQLModel
from .models.users import User
from .models.groups import Group
from .models.transactions import Transaction
from .models.link_model import UserGroupLink, Journal
from sqlmodel.sql.expression import Select, SelectOfScalar

# Silencing some SQL Alchemy warning about inherit_cache performance
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

postgres_url = "postgresql://postgres:postgres@localhost:5438"
database = create_engine(postgres_url, echo=False)

def create_tables():
    SQLModel.metadata.create_all(database)