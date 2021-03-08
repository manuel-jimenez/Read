import hashlib
import secrets
import json
from collections import namedtuple
from constants import NOTEBOOK_SCRIPT_TEMPLATE, FORMATTED_EXTENSIONS

def encode(rawValue):
    """
    encodes `rawValue` to sha256.

    Parameters
    ----------
    rawValue: str
        the value as plain old as it is

    Returns
    -------
    str
        the hashed value in `sha256`
    """
    m = hashlib.sha256()
    m.update(rawValue.encode('utf-8'))
    return m.hexdigest()

def get_proper_file_content(file_content, extension):
    """gets the file content, depending on its extension

    Parameters
    ----------
    file_content: bytes the file content bytes
    extension: file's extension 
    """
    if file_content:
        if extension in FORMATTED_EXTENSIONS:
            fileContent = str(file_content)
            if fileContent != None and fileContent != '':
                fileContent = fileContent[2:-1] #to get ride of b' at the beginning and ' at the end
                                                #but keeps all scaping characters
            if fileContent != None and "{" != fileContent[:1]:
                fileContent = fileContent.replace('"','\\"').replace("\\'","'") #to avoid problems with JSON content
                fileContent = f"{NOTEBOOK_SCRIPT_TEMPLATE}" % fileContent
            return fileContent
        else:
            return file_content.decode('utf-8')

    return None

def get_extension(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower()

def get_secret_random():
    return secrets.token_hex()

def _json_as_object_hook(data):
    """Converts data to Python object, represented as named tuple.
    
    Parameters
    ----------
    data: obj
        the data as str or obj
    
    Returns
    -------
    obj
        the python object serialized from `data`
    """
    return namedtuple('X', data.keys())(*data.values())

def json_2_object(data):
    """Converts data to Python object, verifies that data has value

    Parameters
    ----------
    data: obj
        the data as str or obj
    
    Returns
    -------
    obj
        the python object serialized from `data`
    """
    if data != None:
        data = json.dumps(data)
        return json.loads(data,object_hook=_json_as_object_hook)
    return None