from app import create_app, db, migrate, cli
from models import User, Address, Bot, BotHeartbeat, Parameter, BotJob, Task, TaskVersion, BotTask, BotScheduledJob
from app import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {
            'db': db, 'User': User, 'Address': Address, 'Bot': Bot \
            , 'BotHeartbeat': BotHeartbeat, 'Parameter' : Parameter, \
            'BotJob':BotJob, 'Task': Task, 'TaskVersion':TaskVersion, \
            'BotTask': BotTask, 'BotScheduledJob': BotScheduledJob
            }