import json
from constants import *


def create_table(path):
    try:
        file = open(path, "w+", encoding='utf-8')
    except CANT_READ_FILE_EXCEPTIONS as e:
        raise
    file.write("{}")
    file.close()
    return True


def load_table(path):
    try:
        file = open(path, "r", encoding='utf-8')
    except CANT_READ_FILE_EXCEPTIONS as e:
        create_table(path)
        file = open(path, "r", encoding='utf-8')
    data = file.read()
    file.close()
    data_json_format = json.loads(data)
    return data_json_format


def save_table(data, path):
    js = json.dumps(data)
    try:
        file = open(path, "w+", encoding='utf-8')
    except CANT_READ_FILE_EXCEPTIONS as e:
        return False
    file.write(js)
    file.close()
    return True
