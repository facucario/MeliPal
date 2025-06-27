from sqlalchemy import Column, Integer, String, Text, UniqueConstraint, create_engine, text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, future=True)
with engine.connect() as conn:
    conn.execute(text("PRAGMA journal_mode=WAL"))

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()

class Watchlist(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, index=True)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    __table_args__ = (UniqueConstraint("chat_id", "url", name="uq_chat_url"),)

class SeenAd(Base):
    __tablename__ = "seen_ads"
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, index=True)
    url = Column(Text, nullable=False)
    ad_link = Column(Text, nullable=False)
    __table_args__ = (UniqueConstraint("chat_id", "url", "ad_link", name="uq_chat_url_adlink"),)

class BotState(Base):
    __tablename__ = "bot_state"
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, index=True)
    is_running = Column(Boolean, default=True)  # True = running, False = stopped

Base.metadata.create_all(engine)