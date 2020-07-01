import glob
import json
import os


def save_json(data, name):
    # 将算法的结果保存成json串，用于提供给前端快速测试
    input_file = 'temp/{}.json'.format(name)  # 输入的json
    with open(input_file, 'w') as file_obj:
        json.dump(data, file_obj)


def load_json(name):
    input_file = 'temp/{}.json'.format(name)  # 输入的json
    with open(input_file, 'r') as file_obj:
        return json.load(file_obj)


def exist_json(name):
    input_file = 'temp/{}.json'.format(name)  # 输入的json
    if os.path.exists(input_file):
        return True
    else:
        return False


def get_size(name):
    input_file = 'temp/{}.json'.format(name)  # 输入的json
    return os.path.getsize(input_file)


def delete_json(name):
    os.remove('temp/{}.json'.format(name))


def delete_all_temps():
    folder = os.path.exists('temp/')
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs('temp/')  # make dirs 创建文件时如果路径不存在会创建这个路径
    temps = glob.glob('temp/temp_*.json')
    for temp in temps:
        os.remove(temp)
