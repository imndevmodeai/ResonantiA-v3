import json
from datetime import datetime

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def dumps(obj, **kwargs):
    kwargs.setdefault('cls', CustomEncoder)
    return json.dumps(obj, **kwargs)

def loads(s, **kwargs):
    return json.loads(s, **kwargs) 