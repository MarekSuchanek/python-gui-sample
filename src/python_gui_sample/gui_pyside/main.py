import datetime
import pathlib
import sys
import uuid

from PySide6.QtCore import QFile, QItemSelection
from PySide6.QtWidgets import (QApplication, QWidget, QAbstractItemView,
                               QSpinBox, QDialog, QVBoxLayout, QLabel,
                               QLineEdit, QDialogButtonBox)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtUiTools import QUiLoader

from ..logic import TODOLogic

UI_DIR = pathlib.Path(__file__).parent / "ui"


class ListWindow:

    def __init__(self, parent: QWidget, logic: TODOLogic):
        self.parent = parent
        self.logic = logic
        self.list_id = None

        ui_file = QFile(UI_DIR / "list_window.ui")
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader(parent)
        self.window = loader.load(ui_file)
        ui_file.close()

    def _setup_table(self):
        # Set up table view: model, selection mode, etc.
        table = self.window.tableView
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def _setup_actions(self):
        self.window.actionNew.triggered.connect(self._on_new_item)
        self.window.actionEdit.triggered.connect(self._on_edit_item)
        self.window.actionDelete.triggered.connect(self._on_delete_item)
        self.window.actionEditList.triggered.connect(self._on_edit_list)
        self.window.actionClose.triggered.connect(self._on_close)

        # Initially disable these actions
        self.window.actionEdit.setEnabled(False)
        self.window.actionDelete.setEnabled(False)

    def open_list(self, list_id: uuid.UUID):
        self.list_id = list_id

        todo_list = self.logic.get_list(list_id)
        self.window.setWindowTitle(f"TODO Items: {todo_list.title}")
        self.window.labelTitle.setText(todo_list.title)
        self.window.labelDescription.setText(todo_list.description)
        self._refresh_table()
        self.window.show()

    def _refresh_table(self):
        table = self.window.tableView
        todo_list = self.logic.get_list(self.list_id)
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Title", "Priority", "Tags", "Due"])

        for item in todo_list.items:
            row = [
                QStandardItem(item.title),
                QStandardItem(str(item.priority)),
                QStandardItem(", ".join(item.tags)),
                QStandardItem(item.due_at.isoformat() if item.due_at else "")
            ]
            row[0].setData(str(item.identifier))  # store UUID
            model.appendRow(row)

        table.setModel(model)
        table.resizeColumnsToContents()
        table.selectionModel().selectionChanged.connect(self._on_selection_changed)

        # Disable item actions until a row is selected
        self._on_selection_changed(None, None)

    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        table = self.window.tableView
        has = table.selectionModel().hasSelection()
        self.window.actionEdit.setEnabled(has)
        self.window.actionDelete.setEnabled(has)

    def _on_new_item(self):
        dialog = QDialog(self.window)
        dialog.setWindowTitle("New TODO Item")

        layout = QVBoxLayout(dialog)

        title_input = QLineEdit()
        desc_input = QLineEdit()
        priority_input = QSpinBox()
        priority_input.setRange(0, 5)
        tags_input = QLineEdit()
        due_input = QLineEdit()
        due_input.setPlaceholderText("YYYY-MM-DD or leave empty")

        layout.addWidget(QLabel("Title:"))
        layout.addWidget(title_input)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(desc_input)
        layout.addWidget(QLabel("Priority:"))
        layout.addWidget(priority_input)
        layout.addWidget(QLabel("Tags (comma-separated):"))
        layout.addWidget(tags_input)
        layout.addWidget(QLabel("Due date (optional):"))
        layout.addWidget(due_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def accept():
            title = title_input.text().strip()
            if not title:
                dialog.reject()
                return
            description = desc_input.text().strip()
            priority = priority_input.value()
            tags = set(t.strip() for t in tags_input.text().split(",") if t.strip())
            due_str = due_input.text().strip()
            due_at = None
            if due_str:
                try:
                    due_at = datetime.datetime.fromisoformat(due_str)
                except ValueError:
                    due_at = None  # you could show an error message if desired

            self.logic.add_item(
                self.list_id,
                title=title,
                description=description,
                priority=priority,
                tags=tags,
                due_at=due_at
            )
            self._refresh_table()
            dialog.accept()

        buttons.accepted.connect(accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def _on_edit_item(self):
        table = self.window.tableView
        index = table.selectionModel().currentIndex()
        if not index.isValid():
            return

        row = index.row()
        uuid_str = table.model().item(row, 0).data()
        item_uuid = uuid.UUID(uuid_str)

        lst = self.logic.get_list(self.list_id)
        item = next((i for i in lst.items if i.identifier == item_uuid), None)
        if not item:
            return

        dialog = QDialog(self.window)
        dialog.setWindowTitle("Edit TODO Item")

        layout = QVBoxLayout(dialog)

        title_input = QLineEdit(item.title)
        desc_input = QLineEdit(item.description)
        priority_input = QSpinBox()
        priority_input.setRange(0, 5)
        priority_input.setValue(item.priority)
        tags_input = QLineEdit(", ".join(item.tags))
        due_input = QLineEdit(item.due_at.isoformat() if item.due_at else "")
        due_input.setPlaceholderText("YYYY-MM-DD or leave empty")

        layout.addWidget(QLabel("Title:"))
        layout.addWidget(title_input)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(desc_input)
        layout.addWidget(QLabel("Priority:"))
        layout.addWidget(priority_input)
        layout.addWidget(QLabel("Tags (comma-separated):"))
        layout.addWidget(tags_input)
        layout.addWidget(QLabel("Due date (optional):"))
        layout.addWidget(due_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def accept():
            new_title = title_input.text().strip()
            if not new_title:
                dialog.reject()
                return
            new_desc = desc_input.text().strip()
            new_priority = priority_input.value()
            new_tags = set(t.strip() for t in tags_input.text().split(",") if t.strip())
            new_due_str = due_input.text().strip()
            new_due_at = None
            if new_due_str:
                try:
                    new_due_at = datetime.datetime.fromisoformat(new_due_str)
                except ValueError:
                    new_due_at = None  # optionally show error

            self.logic.update_item(
                self.list_id,
                item_uuid,
                title=new_title,
                description=new_desc,
                priority=new_priority,
                tags=new_tags,
                due_at=new_due_at
            )
            self._refresh_table()
            dialog.accept()

        buttons.accepted.connect(accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def _on_delete_item(self):
        table = self.window.tableView
        index = table.selectionModel().currentIndex()
        if not index.isValid():
            return
        row = index.row()
        uuid_str = table.model().item(row, 0).data()
        self.logic.delete_item(self.list_id, uuid.UUID(uuid_str))
        self._refresh_table()

    def _on_edit_list(self):
        todo_list = self.logic.get_list(self.list_id)

        if todo_list is None:
            return

        # Create edit dialog
        dialog = QDialog(self.window)
        dialog.setWindowTitle("Edit TODO List")

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Title:"))
        title_input = QLineEdit(todo_list.title)
        layout.addWidget(title_input)

        layout.addWidget(QLabel("Description:"))
        desc_input = QLineEdit(todo_list.description)
        layout.addWidget(desc_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def accept():
            new_title = title_input.text().strip()
            new_desc = desc_input.text().strip()
            if new_title:
                self.logic.update_list(self.list_id, new_title, new_desc)
                self._refresh_table()
                dialog.accept()

        buttons.accepted.connect(accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def _on_close(self):
        self.window.hide()
        self.list_id = None
        self.window.labelTitle.setText("--")
        self.window.labelDescription.setText("--")
        self.window.tableView.setModel(QStandardItemModel())


class TODOPySideApp:

    def __init__(self):
        self.logic = TODOLogic()
        self.app = QApplication(sys.argv)

        ui_file = QFile(UI_DIR / "main_window.ui")
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader(self.app)
        self.window = loader.load(ui_file)
        ui_file.close()
        self.item_window = ListWindow(self.window, self.logic)

        self._setup_table()
        self._setup_actions()

    def _setup_table(self):
        # Set up table view: model, selection mode, etc.
        table = self.window.tableView
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def _setup_actions(self):
        self.window.actionNew.triggered.connect(self._on_new_list)
        self.window.actionEdit.triggered.connect(self._on_edit_list)
        self.window.actionDelete.triggered.connect(self._on_delete_list)
        self.window.actionOpen.triggered.connect(self._on_open_list)
        self.window.actionImport.triggered.connect(self._on_import)
        self.window.actionExport.triggered.connect(self._on_export)
        self.window.actionClear.triggered.connect(self._on_clear)

        # Initially disable these actions
        self.window.actionEdit.setEnabled(False)
        self.window.actionDelete.setEnabled(False)
        self.window.actionOpen.setEnabled(False)

    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        has_selection = self.window.tableView.selectionModel().hasSelection()
        self.window.actionEdit.setEnabled(has_selection)
        self.window.actionDelete.setEnabled(has_selection)
        self.window.actionOpen.setEnabled(has_selection)

    def _on_new_list(self):
        # alternatively the dialog could be created in .ui file
        dialog = QDialog(self.window)
        dialog.setWindowTitle("New TODO List")

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Title:"))
        title_input = QLineEdit()
        layout.addWidget(title_input)

        layout.addWidget(QLabel("Description:"))
        desc_input = QLineEdit()
        layout.addWidget(desc_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def accept():
            title = title_input.text().strip()
            description = desc_input.text().strip()
            if title:
                self.logic.create_list(title, description)
                self._refresh_table()
                dialog.accept()

        buttons.accepted.connect(accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def _on_edit_list(self):
        selected_index = self.window.tableView.selectionModel().currentIndex()
        if not selected_index.isValid():
            return

        model = self.window.tableView.model()
        row = selected_index.row()
        uuid_str = model.item(row, 0).data()
        list_uuid = uuid.UUID(uuid_str)
        todo_list = self.logic.get_list(list_uuid)

        if todo_list is None:
            return

        # Create edit dialog
        dialog = QDialog(self.window)
        dialog.setWindowTitle("Edit TODO List")

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Title:"))
        title_input = QLineEdit(todo_list.title)
        layout.addWidget(title_input)

        layout.addWidget(QLabel("Description:"))
        desc_input = QLineEdit(todo_list.description)
        layout.addWidget(desc_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def accept():
            new_title = title_input.text().strip()
            new_desc = desc_input.text().strip()
            if new_title:
                self.logic.update_list(list_uuid, new_title, new_desc)
                self._refresh_table()
                dialog.accept()

        buttons.accepted.connect(accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def _on_delete_list(self):
        model = self.window.tableView.model()
        selected = self.window.tableView.selectionModel().currentIndex()
        if selected.isValid():
            row = selected.row()
            identifier = model.item(row, 0).data()
            self.logic.delete_list(uuid.UUID(identifier))
            self._refresh_table()

    def _on_open_list(self):
        selection_model = self.window.tableView.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            return

        selected_index = selection_model.currentIndex()
        if not selected_index.isValid():
            return

        # Get UUID from first column's user data
        model = self.window.tableView.model()
        row = selected_index.row()
        uuid_str = model.item(row, 0).data()
        list_uuid = uuid.UUID(uuid_str)

        # Create or reuse ItemWindow
        if not hasattr(self, "item_window"):
            self.item_window = ItemWindow(self.window, self.logic)

        self.item_window.open_list(list_uuid)

    def _on_import(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self.window, "Import TODOs")
        if path:
            self.logic.import_lists(pathlib.Path(path))
            self._refresh_table()

    def _on_export(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self.window, "Export TODOs")
        if path:
            self.logic.export_lists(pathlib.Path(path))

    def _on_clear(self):
        self.logic.todo_lists.clear()
        self._refresh_table()

    def _refresh_table(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["UUID", "Title", "Description"])

        for tdl in self.logic.todo_lists.values():
            row = [
                QStandardItem(str(tdl.identifier)),
                QStandardItem(tdl.title),
                QStandardItem(tdl.description)
            ]
            row[0].setData(str(tdl.identifier))  # store UUID
            model.appendRow(row)

        self.window.tableView.setModel(model)
        self.window.tableView.resizeColumnsToContents()

        self.window.tableView.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self._on_selection_changed(None, None)

    def run(self):
        # Show the main window
        self.window.show()
        # Main event loop
        result = self.app.exec()
        # Clean up
        self.window.deleteLater()
        return result


def main():
    app = TODOPySideApp()
    return app.run()
