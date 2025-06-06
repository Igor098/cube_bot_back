from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.core import settings


DATABASE_URL = settings.get_database_url()

engine = create_async_engine(url=DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)