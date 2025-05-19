import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from nudge_bot.utils.logger import configure_logger

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, relationship # relationship will help with another table

engine = create_engine('sqlite:///nudge_bot/goals.db', echo=False)

Base = declarative_base()

logger = logging.getLogger(__name__)
configure_logger(logger)

class Goal(Base):
    """Represents a user created goal

    This model maps to the 'goals' table and stores metadata for desired target areas.

    Used in a Flask-SQLAlchemy application for user interaction and data-driven goal operations.
    """

    __tablename__ = "Goals"

    goal_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    target = Column(Integer, nullable=False)
    progress = Column(Integer, nullable=True, default=0)
    reminder = Column(String, nullable=True, default='N')

    def validate(self) -> None:
        """Validates the goal instance before committing to the database.

        Raises:
            ValueError: If any required fields are invalid.

        TODO:
            See about reminder being only a select few options.

        """
        logger.info(f"Validating goal.")
        if not self.title or not isinstance(self.title, str):
            logger.error(f"Title must be a non-empty string. Not {self.title}.")
            raise ValueError(f"Title must be a non-empty string. Not {self.title}.")
        if self.description and not isinstance(self.description, str):
            logger.error(f"Goal description must be a string. Not {self.description}.")
            raise ValueError(f"Goal description must be a string. Not {self.description}.")
        if self.target is None or not isinstance(self.target, int) or self.target <= 0:
            logger.error(f"Target an integer greater than 0. Not {self.target}.")
            raise ValueError(f"Target an integer greather than 0. Not {self.target}")
        if self.progress is None or not isinstance(self.progress, int) or self.progress < 0:
            logger.error(f"Progress an integer at least 0. Not {self.progress}.")
            raise ValueError(f"Progress an integer at least 0. Not {self.progress}")
        if not self.reminder or not isinstance(self.reminder, str):
            logger.error(f"Reminder must be a non-empty string. Not {self.reminder}.")
            raise ValueError(f"Reminder must be a non-empty string. Not {self.reminder}.")
        logger.info(f"Valid goal.")


    @classmethod
    def create_goal(cls, user_id : int, title : str, description : str, target : int, reminder: str) -> str:
        """Create a new goal and add it to the database.

        Args:
            user_id: The id of the user who made the request.
            target: Value the user is trying to reach with their goal.
            description: Description of the user's goal.
            title: Short title of the goal.
            reminder: Frequency of the reminders the user wants to receive.

        Raises:
            ValueError: If any field is invalid or if a goal with the same compound key already exists. 
            SQLAlchemyError: For any other database-related issues.

        TODO:
            * add a message to be sent when a duplicate goal is created

        """
        logger.info(f"Inserting goal: user_id - {user_id}, title - {title}, description - {description}, target - {target}, reminder - {reminder}")

        try:
            goal = Goal(
                user_id = user_id,
                title = title,
                description = description,
                target = target,
                progress = 0,
                reminder = reminder
            )
            goal.validate()
        except ValueError as e:
            logger.warning(f"Validation failed: {e}")
            raise

        try:
            title=title.strip()
            logger.info(f"Check for existing goal with same compound key (title, target): ({title}, {target})")
            existing = session.query(Goal).filter(Goal.title==title, Goal.target==target).first()
            logger.info(existing)
            if existing:
                logger.error(f"Goal {title} - {target} already exists.1")
                raise ValueError(f"Goal '{title}' - '{target}' already exists.1")
            
            session.add(goal)
            session.commit()
            logger.info(f"Goal '{title}' - '{target}' successfully added.")

        # Duplicate - do we need this one we might not? Try commenting this out when making unit tests
        except IntegrityError:
            logger.error(f"Goal {title} - {target} already exists.2")
            session.rollback()
            raise ValueError(f"Goal {title} - {target} already exists.2")

        except SQLAlchemyError as e:
            logger.error(f"Database error while creating goal: {e}")
            session.rollback()
            raise 
    
    
    @classmethod
    def delete_goal(cls, goal_id: int):
        """Deletes a goal from the database.

        Args:
            goal_id: ID of the goal to be deleted.

        Raises:
            ValueError: If the goal with the given ID does not exist.
            SQLAlchemyError: For any database-related issues.
    
        """
        logger.info(f"Deleting goal {goal_id}...")

        try:
            goal = session.query(Goal).filter(Goal.goal_id==goal_id)
            if not goal:
                logger.warning(f"Attempted to delete non-existent goal with ID {goal_id}")
                raise ValueError(f"Goal with ID {goal_id} not found")

            session.query(Goal).filter(Goal.goal_id==goal_id).delete()
            session.commit()

            logger.info(f"Successfully deleted goal with ID {goal_id}")

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting goal with ID {goal_id}: {e}")
            session.rollback()
            raise


    @classmethod
    def log_goal(cls, goal_id: int, entry: int) -> tuple[bool, str, str]:
        """Logs progress towards a goal in the database.

        Args:
            goal_id: ID of the goal to add progress to.
            entry: Amount to add to progress.

        Returns:
            True if goal has been completed, False if goal has not been completed.
            Title and description of goal.

        Raises:
            ValueError: If the goal with the given ID does not exist.
            SQLAlchemyError: For any database-related issues.
        
        """
        logger.info(f"Logging progress {entry} to goal {goal_id}...")

        try:
            goal = session.query(Goal).filter(Goal.goal_id==goal_id).first()
            logger.info(f"goal is: {goal}")
            if not goal:
                logger.warning(f"Attempted to update non-existent goal with ID {goal_id}")
                raise ValueError(f"Goal with ID {goal_id} not found")
            
            goal.progress += entry

            completed = goal.progress >= goal.target

            session.query(Goal).filter(Goal.goal_id==goal_id).update({'progress': goal.progress})
            session.commit()

        except SQLAlchemyError as e:
            logger.error(f"Database error while logging progress: {e}")
            session.rollback()
            raise 

        logger.info(f"Successfully logged progress towards goal {goal_id}")
        return (completed, goal.title, goal.description)
    

    @classmethod
    def check_progress(cls, goal_id: int) -> tuple[int, float, str]:
        """Check progress of a goal in the database.

        Args:
            goal_id: ID of goal to check progress.

        Returns:
            Progress and percent completed of goal. Current reminder setting (could change this for reminder cog). 
        
        Raises:
            ValueError: If the goal with the given ID does not exist.
            SQLAlchemyError: For any database-related issues.

        """
        logger.info(f"Checking progress of goal {goal_id}...")
        try:
            result = session.query(Goal).filter(Goal.goal_id==goal_id)
            if not result:
                logger.warning(f"Attempted to check progress of non-existent goal with ID {goal_id}")
                raise ValueError(f"Goal with ID {goal_id} not found")
            
            goal = result[0]

            # calculates percent based on progress/target
            percent = (goal.progress / goal.target) * 100

            logger.info(f"Successfully retreived progress of goal {goal_id}")
            return (goal.progress, percent, goal.reminder)

        except SQLAlchemyError as e:
            logger.error(f"Database error while checking progress of goal: {e}")
            session.rollback()
            raise        
    

    @classmethod
    def get_all_goals(cls, user_id: int) -> list[dict]:
        """Retrieve all goals in the database for a user.

        Args:
            user_id: ID of the user requesting all goals.

        Returns:
            List of dictionaries containing all goal info.
        
        Raises:
            ValueError: If the user with the given ID does not exist.
            SQLAlchemyError: For any database-related issues.

        """
        logger.info(f"Getting goals for user {user_id}...")
        try:
            result = session.query(Goal).filter(Goal.user_id==user_id).all()
            if not result:
                logger.warning(f"No goals associated with user ID {user_id}")
                raise ValueError(f"No goals associated with user ID {user_id}")
            
            goals: list[dict] = []

            for goal in result:
                goal_dict = {
                    "title": goal.title,
                    "description": goal.description,
                    "target": goal.target,
                    "progress": goal.progress,
                    "reminder": goal.reminder
                }
                goals.append(goal_dict)
                
            logger.info(f"Successfully retreived all goals")
            return goals

        except SQLAlchemyError as e:
            logger.error(f"Database error while checking progress of goal: {e}")
            session.rollback()
            raise 

        

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()