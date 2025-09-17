from sqlalchemy import create_engine, Column, Integer, Text, DateTime, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date


DATABASE_URL = "sqlite:///bot_knowledge.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class UserQuery(Base):
    __tablename__ = "user_queries"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    question = Column(Text)
    answer = Column(Text)
    section = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserStat(Base):
    __tablename__ = "user_stats"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    total_queries = Column(Integer, default=0)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class DailyStat(Base):
    __tablename__ = "daily_stats"
    id = Column(Integer, primary_key=True)
    stat_date = Column(Date, default=date.today, unique=True)
    total_queries = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    most_popular_section = Column(String(50), nullable=True)


# Создаем все таблицы
Base.metadata.create_all(bind=engine)
