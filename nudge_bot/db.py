from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('sqlite:///cogs/goals.db', echo=True)

Base = declarative_base()

class GoalTemp(Base):
    __tablename__ = 'goals'
    goal_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    target = Column(Integer, nullable=False)
    progress = Column(Integer, nullable=True, default=0)
    reminder = Column(String, nullable=True, default='N')

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
