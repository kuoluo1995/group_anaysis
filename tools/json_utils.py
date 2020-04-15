import glob
import json
import os
from pathlib import Path


def save_json(data, name):
    # 将算法的结果保存成json串，用于提供给前端快速测试
    input_file = 'temp/{}.json'.format(name)  # 输入的json
    with open(input_file, 'w') as file_obj:
        json.dump(data, file_obj)


def load_json(name):
    input_file = 'temp/{}.json'.format(name)  # 输入的json
    with open(input_file, 'r') as file_obj:
        return json.load(file_obj)


def delete_json(name):
    os.remove('temp/{}.json'.format(name))


def delete_all_temps():
    Path('temp/').mkdir(parents=True, exist_ok=True)
    temps = glob.glob('temp/temp_*.json')
    for temp in temps:
        os.remove(temp)
