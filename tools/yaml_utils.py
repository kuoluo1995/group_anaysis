import yaml
from pathlib import Path


def read(path):
    with Path(path).open('r', encoding='UTF-8') as file:
        params = yaml.load(file, Loader=yaml.SafeLoader)
    return params


def write(path, data):
    with Path(path).open('w') as file:
        yaml.dump(data, file)

# def _dict2object(_dict):
#     for key, value in _dict.items():
#         if isinstance(value, dict):
#             _dict[key] = Option(value)
#         else:
#             _dict[key] = value
#     return _dict
#
#
# class Option(dict):
#     def __init__(self, *args, **kwargs):
#         super(Option, self).__init__(*args, **kwargs)
#         self.__dict__ = _dict2object(self)
