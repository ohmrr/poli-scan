from server.app.db.connection import engine
from server.app.db.models import Base


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created (or already exist).")


if __name__ == "__main__":
    init_db()
