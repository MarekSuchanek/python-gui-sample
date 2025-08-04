import datetime
import json
import pathlib
import uuid

from .base import SerializerStrategy
from ..model import TODOList, TODOItem


class JSONSerializer(SerializerStrategy):
    def export_data(self, data: dict[uuid.UUID, TODOList], filepath: pathlib.Path) -> None:
        def default(o):
            if isinstance(o, uuid.UUID):
                return str(o)
            if isinstance(o, set):
                return list(o)
            if isinstance(o, datetime.datetime):
                return o.isoformat()
            if hasattr(o, '__dict__'):
                return o.__dict__
            return str(o)

        with open(filepath, 'w') as f:
            json.dump(list(data.values()), f, default=default, indent=2)

    def import_data(self, filepath: pathlib.Path) -> dict[uuid.UUID, TODOList]:
        with open(filepath, 'r') as f:
            raw = json.load(f)
            result = {}
            for lst in raw:
                items = [
                    TODOItem(
                        title=i['title'],
                        description=i['description'],
                        created_at=datetime.datetime.fromisoformat(i['created_at']),
                        completed_at=datetime.datetime.fromisoformat(i['completed_at']) if i['completed_at'] else None,
                        due_at=datetime.datetime.fromisoformat(i['due_at']) if i['due_at'] else None,
                        priority=i['priority'],
                        tags=set(i['tags']),
                        identifier=uuid.UUID(i['identifier'])
                    ) for i in lst['items']
                ]
                tdl = TODOList(
                    title=lst['title'],
                    description=lst['description'],
                    identifier=uuid.UUID(lst['identifier']),
                    items=items
                )
                result[tdl.identifier] = tdl
            return result
