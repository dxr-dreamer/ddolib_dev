from .dos import DataDigitalObject
from .core import DigitalObjectRepository,IdentifierResolutionService
from flask import Flask, jsonify, request, abort
import logging

class DDOInstance:
    def __init__(self, repo=None, IRS=None, repo_url=None):  
        if repo_url:  
            self.repo = DigitalObjectRepository(repo_url)    
            if IRS is None:  
                self.IRS = IdentifierResolutionService(self.repo) 
            else:  
                self.IRS = IRS  
        elif repo:    
            self.repo = repo  
            if IRS is None:  
                self.IRS = IdentifierResolutionService(self.repo)
            else:  
                self.IRS = IRS  
        else:   
            raise ValueError("Either 'repo' or 'repo_url' must be provided.")
        
    def start_server(self, host='127.0.0.1', port=5000,protocol='http',environment='development'):
        if protocol == 'http':
            # 待办：使用gunicorn实现生产环境
            app = Flask(__name__)

            @app.route('/hello', methods=['GET'])
            def handle_hello():
                return jsonify({"message": "Hello from Digital Object Repository!"})

            @app.route('/create', methods=['POST'])
            def handle_create():
                try:
                    data = request.json['data']
                    metadata = request.json['metadata']
                    do = DataDigitalObject(data=data, metadata=metadata, IRS=self.IRS)
                    if self.repo.save(do):
                        return jsonify({"message": "Digital Object created", "doid": do.doid}), 201
                    else:
                        return jsonify({"error": "Failed to create Digital Object"}), 500
                except KeyError:
                    abort(400, description="Missing data or metadata in request")

            @app.route('/retrieve/<doid>', methods=['GET'])
            def handle_retrieve(doid):
                digital_object = self.repo.retrieve(doid)
                if digital_object:
                    return jsonify({
                        "data": digital_object.data,
                        "metadata": digital_object.metadata,
                        "doid": digital_object.doid
                    }), 200
                else:
                    return jsonify({"error": "Digital Object not found"}), 404

            @app.route('/update/<doid>', methods=['PUT'])
            def handle_update(doid):
                try:
                    data = request.json['data']
                    metadata = request.json['metadata']
                    new_do = DataDigitalObject(data=data, metadata=metadata, doid=doid)
                    if self.repo.update(doid, new_do):
                        return jsonify({"message": "Digital Object updated"}), 200
                    else:
                        return jsonify({"error": "Failed to update Digital Object"}), 500
                except KeyError:
                    abort(400, description="Missing data or metadata in request")

            @app.route('/delete/<doid>', methods=['DELETE'])
            def handle_delete(doid):
                if self.repo.delete(doid):
                    return jsonify({"message": "Digital Object deleted"}), 200
                else:
                    return jsonify({"error": "Digital Object not found"}), 404

            @app.route('/listops', methods=['GET'])
            def handle_list_ops():
                ops = ["Create", "Retrieve", "Update", "Delete", "Hello", "ListOps"]
                return jsonify({"operations": ops}), 200

            app.run(host=host, port=port)
        else:
            logging.error(f'Invalid protocol.')
            return False
  
    def DDO(self, metadata, doid=None):  
        """  
        Returns a decorator that creates DataDigitalObjects using the IRS and repo instances  
        of the DDOManager.  
  
        Parameters:  
        metadata (dict): Metadata to attach to the data object.  
        doid (str, optional): Digital Object Identifier.  
  
        Returns:  
        function: The wrapped function that returns a DataDigitalObject.  
        """  
        def decorator(func):  
            def wrapper(*args, **kwargs):  
                data = func(*args, **kwargs)  
                ddo = DataDigitalObject(data, metadata, self.IRS, doid)  
                self.repo.save(ddo)  
                return ddo  
            return wrapper  
        return decorator