# engines_tab.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QFormLayout,
    QLabel, QLineEdit, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from utils import DATA_DIR, TAB_FILES, read_json, write_json, ACCENT, TEXT


class EnginesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file = DATA_DIR / TAB_FILES["engines"]

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # Left: engine list + add button
        left_layout = QVBoxLayout()
        self.list = QListWidget()
        self.add_btn = QPushButton("Add Engine")
        left_layout.addWidget(self.list)
        left_layout.addWidget(self.add_btn)
        layout.addLayout(left_layout, 1)

        # Right: engine detail form
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        layout.addWidget(self.detail_area, 3)

        detail_widget = QWidget()
        self.form_layout = QFormLayout(detail_widget)
        self.detail_area.setWidget(detail_widget)

        self.fields = {}

        self.create_form()
        self.load_data()

        # Connections
        self.list.currentRowChanged.connect(self.display_engine)
        self.add_btn.clicked.connect(self.add_engine)

    def create_form(self):
        self.fields["name"] = QLineEdit()
        self.fields["lap_time_delta"] = QLineEdit()
        self.fields["reliability_mult"] = QLineEdit()
        self.fields["cost_m"] = QLineEdit()

        for key, label in [("name", "Name"), ("lap_time_delta", "Lap Time Delta"),
                           ("reliability_mult", "Reliability Multiplier"), ("cost_m", "Cost (M)")]:
            self.form_layout.addRow(label, self.fields[key])

        # Save & Delete buttons
        self.save_btn = QPushButton("Save Engine")
        self.delete_btn = QPushButton("Delete Engine")
        self.form_layout.addRow(self.save_btn)
        self.form_layout.addRow(self.delete_btn)
        self.save_btn.clicked.connect(self.save_engine)
        self.delete_btn.clicked.connect(self.delete_engine)

    def load_data(self):
        data = read_json(self.file) or {}
        self.engines = data.get("engines", {})
        self.list.clear()
        for name in self.engines.keys():
            self.list.addItem(name)

    def display_engine(self, index):
        if index < 0 or index >= len(self.engines):
            for f in self.fields.values():
                f.clear()
            return

        engine_name = list(self.engines.keys())[index]
        engine = self.engines[engine_name]

        self.fields["name"].setText(engine_name)
        self.fields["lap_time_delta"].setText(str(engine.get("lap_time_delta", 0)))
        self.fields["reliability_mult"].setText(str(engine.get("reliability_mult", 1)))
        self.fields["cost_m"].setText(str(engine.get("cost_m", 0)))

    def save_engine(self):
        index = self.list.currentRow()
        if index < 0:
            return

        old_name = list(self.engines.keys())[index]
        new_name = self.fields["name"].text().strip()
        if not new_name:
            QMessageBox.warning(self, "Error", "Engine must have a name!")
            return

        engine_data = {
            "lap_time_delta": float(self.fields["lap_time_delta"].text()),
            "reliability_mult": float(self.fields["reliability_mult"].text()),
            "cost_m": float(self.fields["cost_m"].text())
        }

        # Remove old name if changed
        if old_name != new_name:
            self.engines.pop(old_name, None)
        self.engines[new_name] = engine_data

        write_json(self.file, {"engines": self.engines})
        QMessageBox.information(self, "Saved", f"Engine {new_name} saved!")
        self.load_data()
        self.list.setCurrentRow(list(self.engines.keys()).index(new_name))

    def add_engine(self):
        # Add a blank engine
        new_name = "New Engine"
        counter = 1
        while new_name in self.engines:
            new_name = f"New Engine {counter}"
            counter += 1
        self.engines[new_name] = {"lap_time_delta": 0, "reliability_mult": 1, "cost_m": 0}
        write_json(self.file, {"engines": self.engines})
        self.load_data()
        self.list.setCurrentRow(list(self.engines.keys()).index(new_name))

    def delete_engine(self):
        index = self.list.currentRow()
        if index < 0:
            return
        name = list(self.engines.keys())[index]
        reply = QMessageBox.question(self, "Delete Engine",
                                     f"Are you sure you want to delete {name}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.engines.pop(name, None)
            write_json(self.file, {"engines": self.engines})
            self.load_data()
