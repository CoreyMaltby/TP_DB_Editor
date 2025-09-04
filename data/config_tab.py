# config_tab.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QScrollArea,
    QFormLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from utils import DATA_DIR, TAB_FILES, read_json, write_json, TEXT, ACCENT


class ConfigTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file = DATA_DIR / TAB_FILES["config"]

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # Sidebar with categories
        self.sidebar = QListWidget()
        layout.addWidget(self.sidebar, 1)

        # Scrollable area for form
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        layout.addWidget(self.detail_area, 4)

        detail_widget = QWidget()
        self.form_layout = QFormLayout(detail_widget)
        self.detail_area.setWidget(detail_widget)

        self.fields = {}
        self.data = {}

        self.save_btn = QPushButton("Save Changes")
        self.form_layout.addRow(self.save_btn)
        self.save_btn.clicked.connect(self.save_config)

        self.load_data()
        self.sidebar.currentRowChanged.connect(self.display_category)

    def load_data(self):
        self.data = read_json(self.file) or {}
        self.sidebar.clear()
        for key in self.data.keys():
            self.sidebar.addItem(key.replace("_", " ").capitalize())

    def display_category(self, index):
        if index < 0:
            return
        self.fields.clear()
        # Clear old form widgets
        while self.form_layout.count() > 1:  # keep save button
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        category = list(self.data.keys())[index]
        cat_data = self.data[category]

        self._add_fields_recursive(cat_data, self.form_layout, parent_key=category)

    def _add_fields_recursive(self, data, form_layout, parent_key=""):
        if isinstance(data, dict):
            for k, v in data.items():
                full_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    self._add_header(k)
                    self._add_fields_recursive(v, form_layout, full_key)
                elif isinstance(v, list):
                    if all(isinstance(item, dict) for item in v):
                        for i, item in enumerate(v):
                            self._add_header(f"{k} [{i}]")
                            self._add_fields_recursive(item, form_layout, f"{full_key}[{i}]")
                    else:
                        for i, item in enumerate(v):
                            self._add_field_widget(f"{k}[{i}]", item, f"{full_key}[{i}]", form_layout)
                else:
                    self._add_field_widget(k, v, full_key, form_layout)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                full_key = f"{parent_key}[{i}]"
                if isinstance(item, dict):
                    self._add_header(f"{parent_key} [{i}]")
                    self._add_fields_recursive(item, form_layout, full_key)
                else:
                    self._add_field_widget(str(i), item, full_key, form_layout)

    def _add_header(self, text):
        lbl = QLabel(text.replace("_", " ").capitalize())
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

    def _add_field_widget(self, label, value, key, form_layout):
        if isinstance(value, bool):
            widget = QComboBox()
            widget.addItems(["True", "False"])
            widget.setCurrentText(str(value))
        else:
            widget = QLineEdit(str(value))
        self.fields[key] = widget
        form_layout.addRow(label.replace("_", " ").capitalize(), widget)

    def save_config(self):
        for category in self.data.keys():
            self.data[category] = self._update_dict_from_fields(self.data[category], category)

        write_json(self.file, self.data)
        QMessageBox.information(self, "Saved", "Config updated!")

    def _update_dict_from_fields(self, data, parent_key=""):
        if isinstance(data, dict):
            for k, v in data.items():
                full_key = f"{parent_key}.{k}" if parent_key else k
                data[k] = self._update_dict_from_fields(v, full_key)
            return data
        elif isinstance(data, list):
            for i, item in enumerate(data):
                full_key = f"{parent_key}[{i}]"
                if isinstance(item, dict):
                    data[i] = self._update_dict_from_fields(item, full_key)
                else:
                    widget = self.fields.get(full_key)
                    if widget:
                        text = widget.currentText() if isinstance(widget, QComboBox) else widget.text()
                        data[i] = self._parse_value(text, item)
            return data
        else:
            widget = self.fields.get(parent_key)
            if widget:
                text = widget.currentText() if isinstance(widget, QComboBox) else widget.text()
                return self._parse_value(text, data)
            return data

    def _parse_value(self, text, original):
        if isinstance(original, bool):
            return text == "True"
        elif isinstance(original, int):
            try:
                return int(text)
            except ValueError:
                return original
        elif isinstance(original, float):
            try:
                return float(text)
            except ValueError:
                return original
        return text
