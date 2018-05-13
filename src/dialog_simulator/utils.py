import yaml

def import_yaml(file_path: str)->dict:
    try:
        file = yaml.safe_load(open(file_path))
        return file
    except ImportError:
        raise("Error: unable to import %s."%file_path)

