from sqlmodel import create_engine, SQLModel, Session

DATABASE_URL = "sqlite:///./rechef.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    from .models import FoodItem

    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
