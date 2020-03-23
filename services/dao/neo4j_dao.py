from py2neo import Graph


class Neo4jDAO:
    def __init__(self, ip, username, password):
        self.neo_graph = Graph(ip, username=username, password=password)

    def query(self, sql):
        rows = self.neo_graph.run(sql).data()
        results = [cols['id(n)'] for cols in rows]
        return results
