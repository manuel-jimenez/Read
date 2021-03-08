from api import app, db
from models import User, Address, Bot, BotHeartbeat, Parameter, BotJob, Task, TaskVersion
from api.config import Config

@app.shell_context_processor
def make_shell_context():
    return {
            'db': db, 'User': User, 'Bot': Bot, 'BotHeartbeat': BotHeartbeat,\
            'Parameter' : Parameter, 'BotJob':BotJob, 'Task': Task, \
            'TaskVersion':TaskVersion
    }