from flask import Flask, request, jsonify
import logging

# 改为在ddoinstance内实现
# 导入已定义的类
from .core import DigitalObjectRepository, DigitalObject, IdentifierResolutionService

app = Flask(__name__)

# 初始化仓库和标识解析服务
repository = DigitalObjectRepository(url="sqlite:///your_database_url.db")
irs = IdentifierResolutionService(repository)

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

@app.route('/hello', methods=['GET'])
def handle_hello():
    return jsonify({"message": "Hello, this is Digital Object Repository!"})

@app.route('/create', methods=['POST'])
def handle_create():
    data = request.json.get('data')
    metadata = request.json.get('metadata')
    doid = irs.generate(data)  # 生成唯一标识符
    do = DigitalObject(data=data, metadata=metadata, doid=doid)
    if repository.save(do):
        return jsonify({"message": "Digital Object created", "doid": doid}), 201
    else:
        return jsonify({"error": "Failed to create Digital Object"}), 500

@app.route('/retrieve/<doid>', methods=['GET'])
def handle_retrieve(doid):
    digital_object = repository.retrieve(doid)
    if digital_object:
        return jsonify({
            "data": digital_object.data,
            "metadata": digital_object.metadata,
            "doid": digital_object.doid
        })
    else:
        return jsonify({"error": "Digital Object not found"}), 404

@app.route('/update', methods=['PUT'])
def handle_update():
    doid = request.json.get('doid')
    data = request.json.get('data')
    metadata = request.json.get('metadata')
    new_do = DigitalObject(data=data, metadata=metadata, doid=doid)
    if repository.update(doid, new_do):
        return jsonify({"message": "Digital Object updated"})
    else:
        return jsonify({"error": "Failed to update Digital Object"}), 500

@app.route('/delete/<doid>', methods=['DELETE'])
def handle_delete(doid):
    if repository.delete(doid):
        return jsonify({"message": "Digital Object deleted"})
    else:
        return jsonify({"error": "Failed to delete Digital Object"}), 404

@app.route('/listops', methods=['GET'])
def handle_list_ops():
    ops = ["create", "retrieve", "update", "delete", "hello", "listops"]
    return jsonify({"operations": ops})

if __name__ == '__main__':
    app.run(debug=True)
