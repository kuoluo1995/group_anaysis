# 数据库部分
## 环境
1. neo4j
## 导入数据
```bash
neo4j-admin load --from=./dataset/graph_cbdb2_1.dump --database=graph.db --force
neo4j-admin load --from=./dataset/graph_cbdb2_2.dump --database=graph.db --force
```
## 启动neo4j数据库
neo4j.bat console
## 连接账户密码
connect URL: bolt://localhost:7687
Username: neo4j
Password: 123456

# 后端部分
## 环境
推荐使用 anaconda 安装所需要的包
所需要的包全在requirement.txt
## 运行后台
```bash
python manage.py runserver 127.0.0.1:8001
```
