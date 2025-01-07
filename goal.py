import discord

class Goal:
    nextID = 0

    def __init__(self, USER_ID, target, description):
        self.USER_ID = USER_ID
        self.target = target
        self.description = description
        self.GOAL_ID = Goal.next_ID()

    def next_ID(USER_ID):
        ID = Goal.nextID
        Goal.nextID += 1
        return ID
