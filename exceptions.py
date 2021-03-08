class Error(Exception):
    """Base class for errors"""
    pass

class InvalidLoginError(Error):
    """Invalid login error"""
    pass

class BotNotExistsError(Error):
    """Bot does not exist"""
    pass

class BotNotConfiguredError(Error):
    """the bot was not configured due an error"""
    pass

class HeartBeatNotRecordedError(Error):
    """the heartbeat for bot was not recorded in the database"""
    pass

class ParameterNotFoundError(Error):
    """the specified parameter does not exist"""
    pass

class ScriptNotFoundError(Error):
    """the specified script does not exist"""
    pass

class RegisterUserError(Error):
    """error registering the user"""
    pass

class ScriptNotSavedError(Error):
    """error saving the script"""
    pass

class InvalidFileTypeError(Error):
    """error that indicates an ivalid file type"""
    pass