import json


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'toJson'):
            return obj.toJson()
        else:
            return json.JSONEncoder.default(self, obj)

