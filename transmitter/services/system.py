import json
from typing import Dict


class JsonWrapper:
    @staticmethod
    def json_loads(data: str) -> Dict:
        # print()
        # print(f'input data: {json.loads(data)}')
        return json.loads(data)

    @staticmethod
    def json_dumps(data: Dict) -> str:
        # print()
        # print(f'output data: {data}')
        return json.dumps(data)
