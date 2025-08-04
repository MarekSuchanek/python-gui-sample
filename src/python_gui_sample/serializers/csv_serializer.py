import csv
import datetime
import pathlib
import uuid

from .base import SerializerStrategy
from ..model import TODOList, TODOItem


class CSVSerializer(SerializerStrategy):
    def export_data(self, data: dict[uuid.UUID, TODOList], filepath: pathlib.Path) -> None:
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "list_uuid", "list_title", "list_description",
                "item_uuid", "title", "description", "created_at",
                "completed_at", "due_at", "priority", "tags"
            ])
            for list_uuid, tdl in data.items():
                for item in tdl.items:
                    writer.writerow([
                        str(tdl.identifier), tdl.title, tdl.description,
                        str(item.identifier), item.title, item.description,
                        item.created_at.isoformat(),
                        item.completed_at.isoformat() if item.completed_at else "",
                        item.due_at.isoformat() if item.due_at else "",
                        item.priority, ";".join(item.tags)
                    ])

    def import_data(self, filepath: pathlib.Path) -> dict[uuid.UUID, TODOList]:
        result: dict[uuid.UUID, TODOList] = {}
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                list_uuid = uuid.UUID(row["list_uuid"])
                if list_uuid not in result:
                    result[list_uuid] = TODOList(
                        title=row["list_title"],
                        description=row["list_description"],
                        identifier=list_uuid,
                        items=[]
                    )
                item = TODOItem(
                    title=row["title"],
                    description=row["description"],
                    created_at=datetime.datetime.fromisoformat(row["created_at"]),
                    completed_at=datetime.datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
                    due_at=datetime.datetime.fromisoformat(row["due_at"]) if row["due_at"] else None,
                    priority=int(row["priority"]),
                    tags=set(row["tags"].split(";")) if row["tags"] else set(),
                    identifier=uuid.UUID(row["item_uuid"])
                )
                result[list_uuid].items.append(item)
        return result
