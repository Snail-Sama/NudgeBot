import pytest

from nudge_bot.cogs.goal import Goal
from pytest_mock import MockerFixture

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from unittest import TestCase

Session = sessionmaker()

engine = create_engine("mysql+mysqldb://username:password@5000:5000/goals.db")

# --- Fixtures ---
class TestGoal(TestCase):
    def setUp(self):
        # connect to the database
        self.connection = engine.connect()

        # begin a non-ORM transaction
        self.trans = self.connection.begin()

        # bind an individual Session to the connection, selecting
        # "create_savepoint" join_transaction_mode
        self.session = Session(
            bind=self.connection, join_transaction_mode="create_savepoint"
        )


    @pytest.fixture
    def goal_biceps(self): 
        """Fixture for a biceps goal."""
        goal = Goal(
            user_id = 1,
            title = "Bicep Curls",
            description = "Do 35lbs bicep curls",
            target = 35,
            reminder = "W"
        )
        self.session.add(goal)
        self.session.commit()
        return goal

    @pytest.fixture
    def goal_pecs(self):
        """Fixture for a pecs goal."""
        goal = Goal(
            user_id = 2,
            title = "Bench Press",
            description = "Do a 225lbs bench press",
            target = 225,
            reminder = "N"
        )

        self.session.add(goal)
        self.session.commit()
        return goal

    # --- Create Goal ---

    def test_create_goal(self):
        """Test creating a new goal."""
        Goal.create_goal(
            user_id = 1,
            title = "Bicep Curls",
            description = "Do 35lbs bicep curls",
            target = 35,
            reminder = "W"
        )
        goal = self.session.query(Goal).filter_by(title="Bicep Curls").first()
        assert goal is not None
        assert goal.goal_id == 1
        assert goal.user_id == 1
        assert goal.title == "Bicep Curls"
        assert goal.description == "Do 35lbs bicep curls"
        assert goal.target == 35
        assert goal.goal_progress == 0
        assert goal.reminder == 'W'

    def test_create_goal_duplicate(self):
        """Test creating a duplicate goal."""
        with pytest.raises(ValueError, match=f"Goal 'Bicep Curls' - '35' already exists."):
            Goal.create_goal(user_id=1, title="Bicep Curls", description="Do 35lbs bicep curls", target=35, reminder="W")


    @pytest.mark.parametrize("title, description, target, reminder", [
        ("", "empty title", 10, "N"),
        ("Non-string description", 0, 15, "W"),
        ("Target", "Incorrect target type", "twenty reps", "D"),
        ("Reminder", "Incorrect reminder type", 50, 25),
    ])

    def test_create_goal_invalid_data(self, title, description, target, reminder):
        """Test validation errors during goal creation."""
        with pytest.raises(ValueError):
            Goal.create_goal(user_id=1, title=title, description=description, target=target, reminder=reminder)

    def test_delete_goal(self):
        ...

    def test_delete_goal_error(self):
        ...

    def test_log_goal(self):
        ...

    def test_log_goal_error(self):
        ...

    def test_check_progress(self):
        ...

    def test_check_progress_error(self):
        ...
        
    # # --- Get Goal ---

    # def test_get_goal_by_id(goal_biceps):
    #     """Test fetching a goal by ID."""
    #     fetched = Goals.get_goal_by_id(goal_biceps.id)
    #     assert fetched.target == "biceps"

    # def test_get_goal_by_id_not_found(app, session):
    #     """Test error when fetching nonexistent goal by ID."""
    #     with pytest.raises(ValueError, match="not found"):
    #         Goals.get_goal_by_id(999)

    # def test_get_goal_target(goal_biceps):
    #     """Test target field value of a goal."""
    #     fetched = Goals.get_goal_by_id(goal_biceps.id)
    #     assert fetched.target == "biceps"

    # def test_get_goal_by_target_not_found(app, session):
    #     """Test error when fetching nonexistent goal by target."""
    #     with pytest.raises(ValueError, match="No goals found with target 'nonexistent_target'"):
    #         Goals.get_goals_by_target("nonexistent_target")

    # def test_get_goal_value(goal_biceps):
    #     """Test goal_value field of a goal."""
    #     fetched = Goals.get_goal_by_id(goal_biceps.id)
    #     assert isinstance(fetched.goal_value, int)
    #     assert fetched.goal_value == goal_biceps.goal_value

    # def test_get_goal_by_goal_value_not_found(app, session):
    #     """Test error when fetching nonexistent goal by goal_value."""
    #     with pytest.raises(ValueError, match="No goals found with goal value '9999'"):
    #         Goals.get_goals_by_goal_value(9999)

    # def test_get_goal_completed(goal_biceps):
    #     """Test completed field of a goal."""
    #     fetched = Goals.get_goal_by_id(goal_biceps.id)
    #     assert isinstance(fetched.completed, bool)
    #     assert fetched.completed == goal_biceps.completed


    # # --- Delete Goal ---

    # def test_delete_goal_by_id(session, goal_pecs):
    #     """Test deleting a goal by ID."""
    #     Goals.delete_goal(goal_pecs.id)
    #     assert session.query(Goals).get(goal_pecs.id) is None

    # def test_delete_goal_not_found(app, session):
    #     """Test deleting a non-existent goal by ID."""
    #     with pytest.raises(ValueError, match="not found"):
    #         Goals.delete_goal(999)

    # def test_delete_goal_by_target(session, goal_biceps):
    #     """Test deleting a goal by target."""
    #     Goals.delete_goal_by_target(goal_biceps.target)
    #     deleted = session.query(Goals).filter_by(target=goal_biceps.target).first()
    #     assert deleted is None

    # def test_delete_goal_by_goal_value(session, goal_biceps):
    #     """Test deleting a goal by goal_value."""
    #     Goals.delete_goal_by_goal_value(goal_biceps.goal_value)
    #     deleted = session.query(Goals).filter_by(goal_value=goal_biceps.goal_value).first()
    #     assert deleted is None

    # def test_delete_goal_by_completed(session, goal_biceps):
    #     """Test deleting a goal by completed status."""
    #     Goals.delete_goal_by_completed(goal_biceps.completed)
    #     deleted = session.query(Goals).filter_by(completed=goal_biceps.completed).first()
    #     assert deleted is None



    # # --- Update ---
    # def test_update_goal(session, goal_biceps):
    #     """Test updating an existing goal."""
    #     updated = Goals.update_goal(goal_biceps.id, goal_value=20, completed=True)
    #     assert updated.goal_value == 20
    #     assert updated.completed is True


    # # --- Log Progress ---
    # def test_log_progress_updated(session, goal_biceps):
    #     """Test logging progress toward a goal."""
    #     result = goal_biceps.log_progress(5.0)
    #     assert "Progress updated" in result
    #     session.refresh(goal_biceps)
    #     assert goal_biceps.goal_progress == 7.0


    # def test_log_progress_completed(session, goal_biceps):
    #     """Test logging progress toward a goal."""
    #     result = goal_biceps.log_progress(8.0)
    #     assert "Goal completed" in result
    #     session.refresh(goal_biceps)
    #     assert goal_biceps.goal_progress == 10.0

    # # --- Progress Notes ---

    # def test_add_progress_note(session, goal_biceps):
    #     """Test adding a progress note."""
    #     note = "Curls with dumbbells"
    #     goal_biceps.add_progress_note(note)
    #     session.commit()
    #     notes = goal_biceps.get_progress_notes()
    #     assert note in notes


    # # --- Recommendations ---

    # def test_get_exercise_recommendations(session, goal_biceps, mocker):
    #     """Test getting exercise recommendations for a goal."""
    #     mock_response = [
    #         {"name": "bicep curl", "equipment": "dumbbell"},
    #         {"name": "hammer curl", "equipment": "dumbbell"}
    #     ]

    #     mock_fetch = mocker.patch("coach_peter.models.goal_model.fetch_recommendation", return_value=mock_response)

    #     result = Goals.get_exercise_recommendations(goal_biceps.id)

    #     mock_fetch.assert_called_once_with("biceps")
    #     assert isinstance(result, list)
    #     assert result[0]["name"] == "bicep curl"


    # # --- Get All Goals ---

    # def test_get_all_goals(session, goal_biceps, goal_pecs):
    #     """Test retrieving all goals."""
    #     goals = Goals.get_all_goals()
    #     assert isinstance(goals, list)
    #     expected = [
    #         {
    #             "id": goal_biceps.id,
    #             "target": goal_biceps.target,
    #             "goal_value": goal_biceps.goal_value,
    #             "goal_progress": goal_biceps.goal_progress,
    #             "completed": goal_biceps.completed,
    #             "progress_notes": goal_biceps.progress_notes
    #         },
    #         {
    #             "id": goal_pecs.id,
    #             "target": goal_pecs.target,
    #             "goal_value": goal_pecs.goal_value,
    #             "goal_progress": goal_pecs.goal_progress,
    #             "completed": goal_pecs.completed,
    #             "progress_notes": goal_pecs.progress_notes
    #         }
    #     ]
    #     assert goals == expected

    def tearDown(self):
        self.session.close()

        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        self.trans.rollback()

        # return connection to the Engine
        self.connection.close()


