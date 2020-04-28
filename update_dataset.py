import sqlite3
import yaml
from pathlib import Path


def update_node_en_name(db_path):
    with Path('name2en_name.yaml').open('r', encoding='UTF-8') as file:
        name2en_name = yaml.load(file, Loader=yaml.SafeLoader)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for name, en_name in name2en_name.items():
        rows = c.execute("SELECT en_name, name FROM node2data WHERE  name = ?", (name,))
        rows = [(cols[1], cols[0]) for cols in rows]
    for name, en_name in name2en_name.items():
        c.execute("UPDATE node2data SET en_name = ? WHERE name = ?", (en_name, name,))
    conn.commit()


if __name__ == '__main__':
    sql_dataset = Path('./dataset/graph.db')
    update_node_en_name(str(sql_dataset))
