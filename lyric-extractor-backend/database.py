from sqlmodel import SQLModel, create_engine, Session

sqlite_file_name = "lyrics.db"
sqlite_url = f"sqlite:///./{sqlite_file_name}"

# required for SQLite and FastAPI
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def init_db():
    # Creates the database and tables if they don't exist
    SQLModel.metadata.create_all(engine)

def get_session():
    # Provides a temporary session for database operations
    with Session(engine) as session:
        yield session