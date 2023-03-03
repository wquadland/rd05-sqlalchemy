# Use this file for notes and running examples...
# As expected, run it with `python3 -m notes`

from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import MetaData
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[str | None]
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id = mapped_column(ForeignKey("user_account.id"))
    user: Mapped[User] = relationship(back_populates="addresses")
    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"

metadata_obj = MetaData()
engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)

user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30)),
    Column("fullname", String),
)

address_table = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("user_account.id"), nullable=False),
    Column("email_address", String, nullable=False),
)

metadata_obj.create_all(engine)

print('Creating tables from Base metadata')
Base.metadata.create_all(engine)

squidward = User(name="squidward", fullname="Squidward Tentacles")
krabs = User(name="ehkrabs", fullname="Eugene H. Krabs")

session = Session(engine)
session.add(squidward)
session.add(krabs)

session.add(User(name="spongebob", fullname="Spongebob Squarepants"))
session.add(User(name="sandy", fullname="Sandy Cheeks"))
session.add(User(name="patrick", fullname="Patrick Star"))

sandy = session.execute(select(User).filter_by(name="sandy")).scalar_one()
sandy.fullname = "Sandy Squirrel"

stmt = select(user_table).where(user_table.c.name == "spongebob")
print(stmt)

# with engine.connect() as conn:
#     for row in conn.execute(stmt):
#         print(row)

stmt = select(User).where(User.name == "spongebob")
with Session(engine) as session:
    for row in session.execute(stmt):
        print(row)

session.flush()

session.commit()




# region

# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

# with engine.connect() as conn:
#     conn.execute(text("CREATE TABLE some_table (x int, y int)"))
#     conn.execute(
#         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
#         [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
#     )
#     conn.commit()

# with engine.begin() as conn:
#     conn.execute(
#         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
#         [{"x": 6, "y": 8}, {"x": 9, "y": 10}],
#     )

# with engine.connect() as conn:
#     result = conn.execute(text("select x, y from some_table"))
#     for x, y in result:
#         print(f"x: {x}  y: {y}")

# with engine.connect() as conn:
#     result = conn.execute(text("SELECT x, y FROM some_table WHERE y > :y"), {"y": 4})
#     for row in result:
#         print(f"x: {row.x}  y: {row.y}")

# with engine.connect() as conn:
#     conn.execute(
#         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
#         [{"x": 11, "y": 12}, {"x": 13, "y": 14}],
#     )
#     conn.commit()

# stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")
# with Session(engine) as session:
#     result = session.execute(stmt, {"y": 6})
#     for row in result:
#         print(f"x: {row.x}  y: {row.y}")

# with Session(engine) as session:
#     result = session.execute(
#         text("UPDATE some_table SET y=:y WHERE x=:x"),
#         [{"x": 9, "y": 11}, {"x": 13, "y": 15}],
#     )
#     session.commit()

# endregion
