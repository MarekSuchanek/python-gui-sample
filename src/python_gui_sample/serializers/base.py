import abc
import pathlib

from ..model import TODOList


class SerializerStrategy(abc.ABC):
    @abc.abstractmethod
    def export_data(self, data: list[TODOList], filepath: pathlib.Path) -> None:
        pass

    @abc.abstractmethod
    def import_data(self, filepath: pathlib.Path) -> list[TODOList]:
        pass
