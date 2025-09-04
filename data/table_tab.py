from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from utils import TAB_FILES, DATA_DIR
import json

class TableTab(QWidget):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.name = name
        self.file = DATA_DIR / TAB_FILES[name]
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- Controls ---
        controls = QHBoxLayout()
        self.load_btn = QPushButton("Load")
        self.save_btn = QPushButton("Save")
        self.add_btn = QPushButton("Add Row")
        self.remove_btn = QPushButton("Remove Selected")
        controls.addWidget(QLabel(f"<b>{name.capitalize()}</b>"))
        controls.addStretch()
        controls.addWidget(self.load_btn)
        controls.addWidget(self.save_btn)
        controls.addWidget(self.add_btn)
        controls.addWidget(self.remove_btn)
        self.layout.addLayout(controls)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Key / Field", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

        # --- Connections ---
        self.load_btn.clicked.connect(self.load_from_file)
        self.save_btn.clicked.connect(self.save_to_file)
        self.add_btn.clicked.connect(self.add_row)
        self.remove_btn.clicked.connect(self.remove_selected)

        self.load_from_file()

    def add_row(self):
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(""))
        self.table.setItem(r, 1, QTableWidgetItem(""))

    def remove_selected(self):
        rows = sorted(set(idx.row() for idx in self.table.selectedIndexes()), reverse=True)
        for r in rows:
            self.table.removeRow(r)

    def load_from_file(self):
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read {self.file.name}: {e}")
            return

        self.table.clearContents()
        self.table.setRowCount(0)

        if isinstance(data, dict):
            for k, v in data.items():
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(str(k)))
                self.table.setItem(r, 1, QTableWidgetItem(json.dumps(v) if not isinstance(v, (str, int, float, bool, type(None))) else str(v)))
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(str(idx)))
                self.table.setItem(r, 1, QTableWidgetItem(json.dumps(item) if isinstance(item, dict) else str(item)))
        else:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem("value"))
            self.table.setItem(r, 1, QTableWidgetItem(str(data)))

    def save_to_file(self):
        rows = []
        for r in range(self.table.rowCount()):
            key_item = self.table.item(r, 0)
            val_item = self.table.item(r, 1)
            key = key_item.text() if key_item else ""
            val = val_item.text() if val_item else ""
            rows.append((key, val))

        is_indexed = all(k.isdigit() for k, _ in rows if k != "")
        output = []
        if is_indexed:
            output = [self._try_parse_json_scalar(v) for _, v in rows]
        else:
            output = {k: self._try_parse_json_scalar(v) for k, v in rows if k != ""}

        try:
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Saved", f"Saved to {self.file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save {self.file}: {e}")

    @staticmethod
    def _try_parse_json_scalar(s: str):
        s = s.strip()
        if s == "":
            return ""
        try:
            return json.loads(s)
        except Exception:
            return s
