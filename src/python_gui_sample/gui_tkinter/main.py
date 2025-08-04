import pathlib
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from uuid import UUID

from ..logic import TODOLogic


class TODOTkinterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TODO Manager")
        self.geometry("600x400")
        self.logic = TODOLogic()
        self.selected_list_id: UUID | None = None
        self.create_widgets()

    def create_widgets(self):
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        toolbar = tk.Frame(self)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="Add List", command=self.add_list).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Edit", command=self.edit_list).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Delete", command=self.delete_list).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Open", command=self.open_list).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Export", command=self.export_lists).pack(side=tk.RIGHT)
        tk.Button(toolbar, text="Import", command=self.import_lists).pack(side=tk.RIGHT)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for lst in self.logic.todo_lists.values():
            self.listbox.insert(tk.END, f"{lst.title} - {lst.description}")

    def on_select(self, event):
        sel = self.listbox.curselection()
        if sel:
            all_uuids = list(self.logic.todo_lists.keys())
            self.selected_list_id = all_uuids[sel[0]]

    def add_list(self):
        title = simpledialog.askstring("Title", "Enter title:")
        desc = simpledialog.askstring("Description", "Enter description:")
        if title:
            self.logic.create_list(title, desc)
            self.refresh()

    def edit_list(self):
        if not self.selected_list_id:
            return
        lst = self.logic.get_list(self.selected_list_id)
        title = simpledialog.askstring("Edit Title", "Enter new title:", initialvalue=lst.title)
        desc = simpledialog.askstring("Edit Description", "Enter new desc:", initialvalue=lst.description)
        self.logic.update_list(self.selected_list_id, title, desc)
        self.refresh()

    def delete_list(self):
        if not self.selected_list_id:
            return
        self.logic.delete_list(self.selected_list_id)
        self.selected_list_id = None
        self.refresh()

    def open_list(self):
        if not self.selected_list_id:
            return
        ItemWindow(self, self.logic, self.selected_list_id)

    def export_lists(self):
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if path:
            self.logic.export_lists(pathlib.Path(path))
            messagebox.showinfo("Export", "Lists exported successfully.")

    def import_lists(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            self.logic.import_lists(pathlib.Path(path))
            self.refresh()
            messagebox.showinfo("Import", "Lists imported successfully.")


class ItemWindow(tk.Toplevel):
    def __init__(self, parent, logic, list_id: UUID):
        super().__init__(parent)
        selected_list = logic.get_list(list_id)
        self.logic = logic
        self.list_id = list_id
        self.title(f"TODO Items: {selected_list.title}")
        self.geometry("500x300")
        self.itembox = tk.Listbox(self)
        self.itembox.pack(fill=tk.BOTH, expand=True)
        self.toolbar = tk.Frame(self)
        self.toolbar.pack(fill=tk.X)
        tk.Button(self.toolbar, text="Add Item", command=self.add_item).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Delete Item", command=self.delete_item).pack(side=tk.LEFT)
        self.refresh()

    def refresh(self):
        self.itembox.delete(0, tk.END)
        lst = self.logic.get_list(self.list_id)
        for item in lst.items:
            self.itembox.insert(tk.END, f"[{item.priority}] {item.title} - {', '.join(item.tags)} "
                                        f"(Due: {item.due_at.strftime('%Y-%m-%d') if item.due_at else 'N/A'})")

    def add_item(self):
        title = simpledialog.askstring("Title", "Enter item title:")
        desc = simpledialog.askstring("Desc", "Enter item description:")
        tags = simpledialog.askstring("Tags", "Comma-separated tags:")
        priority = simpledialog.askinteger("Priority", "Enter priority (0-5):")
        due_at = simpledialog.askstring("Due Date", "Enter due date (YYYY-MM-DD):")
        if due_at:
            try:
                from datetime import datetime
                due_at = datetime.strptime(due_at, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
                return
        self.logic.add_item(
            self.list_id,
            title=title,
            description=desc,
            tags=set(tags.split(',')) if tags else set(),
            priority=priority or 0,
            due_at=due_at if due_at else None,
        )
        self.refresh()

    def delete_item(self):
        sel = self.itembox.curselection()
        if sel:
            lst = self.logic.get_list(self.list_id)
            item = lst.items[sel[0]]
            self.logic.delete_item(self.list_id, item.identifier)
            self.refresh()


def main():
    app = TODOTkinterApp()
    app.mainloop()
