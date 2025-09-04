from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QFormLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt
from pathlib import Path
import json
from utils import DATA_DIR, TAB_FILES, read_json, write_json, ACCENT, TEXT, BG

class DriversTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file = DATA_DIR / TAB_FILES["drivers"]
        self.teams_file = DATA_DIR / TAB_FILES["teams"]

        # --- Main Layout ---
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # --- Left: driver list + add button ---
        left_layout = QVBoxLayout()
        self.list = QListWidget()
        left_layout.addWidget(self.list)

        # Add Driver button at the bottom
        self.add_btn = QPushButton("Add Driver")
        left_layout.addWidget(self.add_btn)
        self.add_btn.clicked.connect(self.add_driver)

        layout.addLayout(left_layout, 1)

        # --- Right: scrollable detail form ---
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        layout.addWidget(self.detail_area, 3)

        detail_widget = QWidget()
        self.form_layout = QFormLayout(detail_widget)
        self.detail_area.setWidget(detail_widget)

        self.fields = {}

        def add_section_header(title):
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

        add_section_header("Driver Details")
        for field in ["name", "age", "talent", "train", "pay_driver_amount_m"]:
            self.fields[field] = QLineEdit()
            self.form_layout.addRow(QLabel(field.capitalize()), self.fields[field])

        add_section_header("Stats")
        for field in ["base_lap_time_sim", "number", "cornering", "braking", "consistency", "smoothness", "control"]:
            self.fields[field] = QLineEdit()
            self.form_layout.addRow(QLabel(field.capitalize()), self.fields[field])

        add_section_header("History")
        for field in ["seasons", "championships", "wins", "podiums", "poles"]:
            self.fields[field] = QLineEdit()
            self.form_layout.addRow(QLabel(field.capitalize()), self.fields[field])

        add_section_header("Contract")
        self.fields["contract_team"] = QComboBox()
        self.load_active_teams()
        self.form_layout.addRow(QLabel("Team"), self.fields["contract_team"])

        for field in ["length_weeks", "salary_m", "start_week"]:
            key = f"contract_{field}"
            self.fields[key] = QLineEdit()
            self.form_layout.addRow(QLabel(field.capitalize()), self.fields[key])

        self.save_btn = QPushButton("Save Changes")
        self.form_layout.addRow(self.save_btn)

        self.drivers = []
        self.load_data()

        self.list.currentRowChanged.connect(self.display_driver)
        self.save_btn.clicked.connect(self.save_data)
        self.fields["contract_team"].currentIndexChanged.connect(self.on_team_changed)

    def load_active_teams(self):
        self.fields["contract_team"].clear()
        teams = read_json(self.teams_file) or []
        active_teams = [t["name"] for t in teams if t.get("active", False)]
        self.fields["contract_team"].addItem("Null")
        self.fields["contract_team"].addItems(active_teams)

    def on_team_changed(self):
        team = self.fields["contract_team"].currentText()
        read_only = team == "Null"
        for key in ["contract_length_weeks", "contract_salary_m", "contract_start_week"]:
            self.fields[key].setReadOnly(read_only)
            if read_only:
                self.fields[key].setText("0")
            else:
                self.fields[key].setText(self.fields[key].text())

    def load_data(self):
        self.drivers = read_json(self.file) or []
        self.list.clear()
        for d in self.drivers:
            self.list.addItem(d.get("name", "Unnamed"))

    def display_driver(self, index):
        if index < 0 or index >= len(self.drivers):
            return
        driver = self.drivers[index]
        for key, widget in self.fields.items():
            if key.startswith("contract_"):
                contract_key = key.replace("contract_", "")
                if contract_key == "team":
                    idx = widget.findText(driver.get("contract", {}).get("team", "Null"))
                    widget.setCurrentIndex(idx if idx >= 0 else 0)
                else:
                    widget.setText(str(driver.get("contract", {}).get(contract_key, "")))
            else:
                widget.setText(str(driver.get(key, "")))
        self.on_team_changed()

    def save_data(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        driver = self.drivers[idx]
        for key, widget in self.fields.items():
            if key.startswith("contract_"):
                contract_key = key.replace("contract_", "")
                if contract_key == "team":
                    driver.setdefault("contract", {})[contract_key] = widget.currentText()
                else:
                    driver.setdefault("contract", {})[contract_key] = widget.text()
            else:
                driver[key] = widget.text()
        write_json(self.file, self.drivers)
        QMessageBox.information(self, "Saved", f"Driver {driver.get('name')} updated!")
        self.load_data()
        self.list.setCurrentRow(idx)

    def add_driver(self):
        """Add a new blank driver and select it."""
        new_driver = {
            "name": "New Driver",
            "age": "",
            "talent": "",
            "train": "",
            "pay_driver_amount_m": "",
            "base_lap_time_sim": "",
            "number": "",
            "cornering": "",
            "braking": "",
            "consistency": "",
            "smoothness": "",
            "control": "",
            "seasons": "",
            "championships": "",
            "wins": "",
            "podiums": "",
            "poles": "",
            "contract": {
                "team": "Null",
                "length_weeks": 0,
                "salary_m": 0,
                "start_week": 1
            }
        }
        self.drivers.append(new_driver)
        self.load_data()
        self.list.setCurrentRow(len(self.drivers) - 1)


