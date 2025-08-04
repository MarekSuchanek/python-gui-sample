import pathlib
import uuid

from .model import TODOList, TODOItem
from .serializers import CSVSerializer, JSONSerializer

# This file contains the logic for managing lists and items.
# The TODOLogic class is responsible for handling operations and acts as a facade
# to the underlying model classes. It provides methods to add, remove, and retrieve
# lists and items, as well as to mark items as completed or incomplete. It is
# agnostic to the GUI framework and can be used with any GUI toolkit (or even with
# other types of interfaces, such as a command line interface).

class TODOLogic:

    def __init__(self):
        self.todo_lists: dict[uuid.UUID, TODOList] = {}

    def create_list(self, title, description):
        new_list = TODOList(title=title, description=description)
        self.todo_lists[new_list.identifier] = new_list
        return new_list

    def delete_list(self, identifier: uuid.UUID):
        del self.todo_lists[identifier]

    def update_list(self, identifier: uuid.UUID, title: str, description: str):
        if identifier in self.todo_lists:
            lst = self.todo_lists[identifier]
            lst.title = title
            lst.description = description

    def get_list(self, identifier: uuid.UUID) -> TODOList | None:
        return self.todo_lists.get(identifier)

    def add_item(self, list_identifier, **item_kwargs):
        if list_identifier in self.todo_lists:
            item = TODOItem(**item_kwargs)
            self.todo_lists[list_identifier].items.append(item)

    def delete_item(self, list_identifier: uuid.UUID, item_identifier: uuid.UUID):
        if list_identifier in self.todo_lists:
            lst = self.todo_lists[list_identifier]
            item = next((it for it in lst.items if it.identifier == item_identifier), None)
            if item:
                lst.items.remove(item)

    def update_item(self, list_identifier: uuid.UUID, item_identifier: uuid.UUID, **kwargs):
        if list_identifier in self.todo_lists:
            lst = self.todo_lists[list_identifier]
            item = next((it for it in lst.items if it.identifier == item_identifier), None)
            if item:
                for key, value in kwargs.items():
                    setattr(item, key, value)

    def export_lists(self, filepath: pathlib.Path):
        if filepath:
            if filepath.name.endswith(".csv"):
                CSVSerializer().export_data(self.todo_lists, filepath)
            else:
                JSONSerializer().export_data(self.todo_lists, filepath)

    def import_lists(self, filepath: pathlib.Path):
        if filepath:
            if filepath.name.endswith(".csv"):
                self.todo_lists = CSVSerializer().import_data(filepath)
            else:
                self.todo_lists = JSONSerializer().import_data(filepath)
