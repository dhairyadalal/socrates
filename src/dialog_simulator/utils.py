import yaml
import json


def import_yaml(file_path: str)->dict:
    try:
        file = yaml.safe_load(open(file_path, 'r'))
        return file
    except ImportError:
        raise("Error: unable to import %s."%file_path)


def import_json(file_path: str)->dict:
    try:
        with open(file_path, "r") as file:
            file = json.load(file)
        file.close()
        return file
    except ImportError:
        raise("Error: unable to import %s." % file_path)

