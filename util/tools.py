import qrcode
import io
import json
from docx import Document
from docx.shared import Inches
import os
from paddleocr import PaddleOCR
import networkx as nx
import requests


graph = nx.Graph()

# 创建二维码
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img

def insertqr_word(form_data, doc_path):
    json_data = json.dumps(form_data, ensure_ascii=False)
    img = generate_qr_code(json_data) # qr

    document = Document(doc_path) # doc object
    print('创建doc成功')
    qr_stream = io.BytesIO() # 以PNG格式保存到二进制数据流qr_stream中
    img.save(qr_stream, format='PNG')

    # 写入指针移动到流的起始位置（偏移量为0）从流中读取整个图像数据
    qr_stream.seek(0)
    document.add_picture(qr_stream, width=Inches(1), height=Inches(1))
    document.save(doc_path) # 覆盖


def save_pth(file, submitter, title, dir):
    file_extension = os.path.splitext(file.filename)[1]  # 扩展名
    filename = f"{submitter}_{title}{file_extension}"
    
    word_file_path= os.path.join(dir, filename)
    file.save(word_file_path) # 存储
    
    print('word img 保存到文件服务器', word_file_path)
    return word_file_path

def ocr_paddle(img_path):
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    result = ocr.ocr(img_path, cls=True)

    txts = []
    for line in result[0]:
        txts.append(line[1][0])
    txt= ''.join(txts)
    return txt

def find_shortest_path(graph, source, target):
    if '不办理货运营业' in graph.nodes[source]['situation']:
        
        print(f"起点 {source} 不办理货运营业，正在查找替代节点...")
        neo_source = find_nearest_station_with_service(graph, source)
        if neo_source is None:
            print("没有符合条件的替代起点")
            return
        print(f"新的起点为 {neo_source}")
    if '不办理货运营业' in graph.nodes[target]['situation']:
        print(f"终点 {target} 不办理货运营业，正在查找替代节点...")
        neo_target = find_nearest_station_with_service(graph, target)
        if neo_target is None:
            print("没有符合条件的替代终点")
            return
        print(f"新的终点为 {neo_target}")
    try:
        shortest_path = nx.shortest_path(
            graph, source=source, target=target, weight='weight')
        shortest_path_length = nx.shortest_path_length(
            graph, source=source, target=target, weight='weight')
        
        pth= ' -> '.join(shortest_path)
        print(f"最短路径: {pth}")
        print(f"最短路径长度: {shortest_path_length}")
        return shortest_path, shortest_path_length
    
    except nx.NetworkXNoPath:
        print(f"{source} 和 {target} 不连通.")
    
def find_nearest_station_with_service(graph, start_node, service="办理整车货物发到"):
    
    for node in nx.bfs_tree(graph, start_node):
        if service in graph.nodes[node]['situation']:
            return node
    return None 

def loc2geo(addr):
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "address": addr,
        "key": "bb61567129dd682e05fd73e0cd9f724b"
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = json.loads(response.text)
        if data["info"]=="ENGINE_RESPONSE_DATA_ERROR":
            return []
        geocode = data['geocodes'][0]
        location = geocode['location']
        longitude, latitude = location.split(',')
        print(addr, "经度:", longitude, '纬度:', latitude)
        return [float(longitude), float(latitude)]
    
    else:
        print("请求失败，状态码:", response.status_code)
        return

__all__ = ['generate_qr_code', 'insertqr_word', 'save_pth', 'ocr_paddle']