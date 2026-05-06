from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./polandrent.db"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(engine,expire_on_commit=False)
