import dataclasses
import datetime
import uuid

# Alternatively, a more complex model library could be used, such as Pydantic or Marshmallow,
# but for simplicity, we will use dataclasses here.

@dataclasses.dataclass
class TODOItem:
    """
    A class to represent a single item in a TO-DO list.
    """
    title: str = ""
    description: str = ""
    created_at: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)
    completed_at: datetime.datetime | None = None
    due_at: datetime.datetime | None = None
    priority: int = 0  # Lower number means higher priority
    tags: set[str] = dataclasses.field(default_factory=set)
    identifier: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)

    def mark_completed(self):
        """Mark the item as completed."""
        self.completed_at = datetime.datetime.now()

    def mark_incomplete(self):
        """Mark the item as incomplete."""
        self.completed_at = None

    @property
    def is_completed(self) -> bool:
        """Check if the item is completed."""
        return self.completed_at is not None

    def __eq__(self, other):
        """Check equality based on identifier."""
        if isinstance(other, TODOItem):
            return self.identifier == other.identifier
        return False


@dataclasses.dataclass
class TODOList:
    """
    A class to represent a TO-DO list.
    """
    title: str
    description: str = ""
    items: list[TODOItem] = dataclasses.field(default_factory=list)
    identifier: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)

    def add_item(self, item: TODOItem):
        """Add an item to the list."""
        self.items.append(item)

    def remove_item(self, item: TODOItem):
        """Remove an item from the list."""
        if item in self.items:
            self.items.remove(item)
