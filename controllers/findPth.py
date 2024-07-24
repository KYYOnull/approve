

from flask import Blueprint, request, jsonify, render_template
from util.tools import find_shortest_path, loc2geo
import networkx as nx
import mysql.connector

findpth_bp = Blueprint("findpth", __name__)

# MySQL 配置
db_config = {
    "user": "root",
    "password": "741953",
    "host": "127.0.0.1",
    "database": "railway_lines",
}
graph = nx.Graph() # 一次构建

@findpth_bp.route("/show")
def show_path():
    return render_template("route.html")

@findpth_bp.route("/create-graph", methods=["GET"])
def create_graph():
    conn = mysql.connector.connect(**db_config)
    print("成功连接到数据库!")
    cursor= conn.cursor()

    query_tables = "SHOW TABLES"
    cursor.execute(query_tables)
    tables = cursor.fetchall()
    
    for table in tables: # 一条线
        table_name = table[0] # 万南线 [('万盛站', 0, '客运：办理旅客;;'), ('万盛北站', 3, '货运：办理整车路'), ..
        query_data = f"SELECT 站名, 里程, 客货运情况 FROM {table_name}"
        cursor.execute(query_data)
        results = cursor.fetchall() # 所有站点
            
        for i in range(len(results)): # i ('万盛站', 0, '客运：办理旅客;') 一个站点
            station = results[i][0]
            mileage = results[i][1]
            passe_cargo_situation = results[i][2]
            graph.add_node(station, situation= passe_cargo_situation)  # 添加节点
            
            if i > 0: # 前一个站
                station_pre = results[i - 1][0]
                mileage_pre = results[i - 1][1]
                distance = abs(mileage_pre - mileage)
                graph.add_edge(station, station_pre, weight=distance)  # 添加边 和 权重
                
    return jsonify(graph.number_of_nodes(), graph.number_of_edges())

@findpth_bp.route('/nodes')
def nodes_num():
    return jsonify(graph.number_of_nodes())

@findpth_bp.route("/findpth", methods=["GET"])
def findpth():
    start = request.args.get("start")
    end = request.args.get("end")
    print(start, end)
    
    shortest_path, shortest_path_length= find_shortest_path(graph, start, end)
    
    loc= []
    for sta in shortest_path:
        loc.append(loc2geo(sta)) # 维护路线上所有站点坐标
        
    loc = [coord for coord in loc if len(coord) == 2]
    
    filtered_loc = [loc[0]] # 只维护合法坐标 即 经纬度相邻站变化不超过1度的站点坐标

    for i in range(1, len(loc)):
        print(len(filtered_loc), i+1)
        prev_coord = filtered_loc[-1]
        current_coord = loc[i]
        if abs(prev_coord[0] - current_coord[0]) <= 2 and abs(prev_coord[1] - current_coord[1]) <= 1:
            filtered_loc.append(current_coord)
            
    
    return jsonify(filtered_loc)