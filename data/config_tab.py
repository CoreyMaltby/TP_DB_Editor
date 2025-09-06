# config_tab.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QFormLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt
from utils import DATA_DIR, TAB_FILES, read_json, write_json, ACCENT, TEXT


class ConfigTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file = DATA_DIR / TAB_FILES["config"]

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # Sidebar list
        left_layout = QVBoxLayout()
        self.list = QListWidget()
        left_layout.addWidget(self.list)
        layout.addLayout(left_layout, 1)

        # Scrollable detail panel
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        layout.addWidget(self.detail_area, 3)

        detail_widget = QWidget()
        self.form_layout = QFormLayout(detail_widget)
        self.detail_area.setWidget(detail_widget)

        self.fields = {}
        self.config_data = {}

        self.load_data()

        # Connections
        self.list.currentRowChanged.connect(self.display_section)

    def add_section_header(self, title: str):
        """Add styled header like drivers tab"""
        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"""
            font-weight: bold;
            border: 1px solid {ACCENT};
            padding: 4px;
            margin-top: 8px;
            margin-bottom: 4px;
            border-radius: 4px;
            background-color: #2f3436;
            color: {TEXT};
        """)
        self.form_layout.addRow(lbl)

    def load_data(self):
        self.config_data = read_json(self.file) or {}
        self.list.clear()
        for key in self.config_data.keys():
            self.list.addItem(key.replace("_", " ").capitalize())

    def display_section(self, index):
        # Clear form
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)
        self.fields.clear()

        if index < 0:
            return

        section_key = list(self.config_data.keys())[index]
        section_data = self.config_data[section_key]

        # Add header
        self.add_section_header(section_key.replace("_", " ").capitalize())

        # Populate fields depending on section
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                self.add_field(section_key, key, value)
        elif isinstance(section_data, list):
            self.fields[section_key] = QLineEdit(str(section_data))
            self.form_layout.addRow(section_key.capitalize(), self.fields[section_key])
        else:
            self.fields[section_key] = QLineEdit(str(section_data))
            self.form_layout.addRow(section_key.capitalize(), self.fields[section_key])

        # Save button
        save_btn = QPushButton("Save Changes")
        self.form_layout.addRow(save_btn)
        save_btn.clicked.connect(lambda: self.save_section(section_key))

    def add_field(self, section_key, key, value):
        label = key.replace("_", " ").capitalize()
        if isinstance(value, bool):
            field = QComboBox()
            field.addItems(["True", "False"])
            field.setCurrentText("True" if value else "False")
        elif isinstance(value, dict):
            # Nested dicts (like tyre compounds, start probabilities)
            self.add_section_header(label)
            for subkey, subval in value.items():
                self.add_field(section_key, f"{key}.{subkey}", subval)
            return
        else:
            field = QLineEdit(str(value))

        self.fields[f"{section_key}.{key}"] = field
        self.form_layout.addRow(label, field)

    def save_section(self, section_key):
        section_data = self.config_data[section_key]

        if isinstance(section_data, dict):
            for fullkey, widget in self.fields.items():
                if not fullkey.startswith(section_key + "."):
                    continue
                path = fullkey.split(".")[1:]
                self.set_nested_value(section_data, path, widget)
        else:
            widget = self.fields[section_key]
            self.config_data[section_key] = self.parse_value(widget.text())

        write_json(self.file, self.config_data)
        QMessageBox.information(self, "Saved", f"Config section '{section_key}' updated!")

    def set_nested_value(self, data, path, widget):
        key = path[0]
        if len(path) == 1:
            if isinstance(widget, QComboBox):
                data[key] = True if widget.currentText() == "True" else False
            else:
                data[key] = self.parse_value(widget.text())
        else:
            if key not in data or not isinstance(data[key], dict):
                data[key] = {}
            self.set_nested_value(data[key], path[1:], widget)

    def parse_value(self, text: str):
        try:
            if "." in text:
                return float(text)
            return int(text)
        except ValueError:
            if text.lower() == "true":
                return True
            if text.lower() == "false":
                return False
            # Try list or dict from JSON string
            try:
                import json
                return json.loads(text)
            except Exception:
                return text
