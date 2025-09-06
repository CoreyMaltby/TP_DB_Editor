from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QFormLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from utils import DATA_DIR, TAB_FILES, read_json, write_json, ACCENT, TEXT

TRAITS_LIST = [
    "hotlapper", "tyer_whisperer", "pay driver", "overtake_artist",
    "mechanic", "clean_air_merchant", "bottlejob", "crash_happy",
    "nervous", "tyre_abuser"
]

class DriversTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file = DATA_DIR / TAB_FILES["drivers"]
        self.teams_file = DATA_DIR / TAB_FILES["teams"]

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # --- Left: search, driver list, buttons ---
        left_layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search driver...")
        left_layout.addWidget(self.search_input)

        self.list = QListWidget()
        left_layout.addWidget(self.list)

        self.add_btn = QPushButton("Add Driver")
        left_layout.addWidget(self.add_btn)
        self.add_btn.clicked.connect(self.add_driver)

        self.sort_btn = QPushButton("Sort Alphabetically")
        left_layout.addWidget(self.sort_btn)
        self.sort_btn.clicked.connect(self.sort_drivers)

        layout.addLayout(left_layout, 1)

        # --- Right: scrollable form ---
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        layout.addWidget(self.detail_area, 3)

        detail_widget = QWidget()
        self.form_layout = QFormLayout(detail_widget)
        self.detail_area.setWidget(detail_widget)

        self.fields = {}

        # Helper for colored headers
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

        # Driver Details
        add_section_header("Driver Details")
        for field in ["name", "age", "talent", "train"]:
            self.fields[field] = QLineEdit()
            self.form_layout.addRow(QLabel(field.capitalize()), self.fields[field])

        # Pay driver amount field
        self.fields["pay_driver_amount_m"] = QLineEdit()
        self.form_layout.addRow(QLabel("Pay Driver Amount (M)"), self.fields["pay_driver_amount_m"])

        # Stats
        add_section_header("Stats")
        for field in ["base_lap_time_sim", "number", "cornering", "braking",
                      "consistency", "smoothness", "control"]:
            self.fields[field] = QLineEdit()
            self.form_layout.addRow(QLabel(field.capitalize()), self.fields[field])

        # History
        add_section_header("History")
        for field in ["seasons", "championships", "wins", "podiums", "poles"]:
            self.fields[field] = QLineEdit()
            self.form_layout.addRow(QLabel(field.capitalize()), self.fields[field])

        # Contract
        add_section_header("Contract")
        self.fields["contract_team"] = QComboBox()
        self.fields["contract_role"] = QComboBox()
        self.fields["contract_role"].addItems(["null", "main", "reserve"])
        self.load_active_teams()
        self.form_layout.addRow(QLabel("Team"), self.fields["contract_team"])
        self.form_layout.addRow(QLabel("Role"), self.fields["contract_role"])

        for field in ["length_weeks", "salary_m", "start_week"]:
            key = f"contract_{field}"
            self.fields[key] = QLineEdit()
            self.form_layout.addRow(QLabel(field.capitalize()), self.fields[key])

        # Traits
        add_section_header("Traits")
        self.fields["traits"] = QComboBox()
        self.fields["traits"].setEditable(True)
        self.fields["traits"].lineEdit().setReadOnly(True)
        self.fields["traits"].lineEdit().setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.form_layout.addRow(QLabel("Traits"), self.fields["traits"])
        self.setup_traits_combo()

        # Save button
        self.save_btn = QPushButton("Save Changes")
        self.form_layout.addRow(self.save_btn)

        self.drivers = []
        self.load_data()

        # Connections
        self.list.currentRowChanged.connect(self.display_driver)
        self.save_btn.clicked.connect(self.save_data)
        self.fields["contract_team"].currentIndexChanged.connect(self.on_team_changed)
        self.search_input.textChanged.connect(self.update_driver_list)

    def setup_traits_combo(self):
        combo = self.fields["traits"]
        combo.clear()
        model = QStandardItemModel()
        for trait in TRAITS_LIST:
            item = QStandardItem(trait)
            item.setCheckable(True)
            item.setSelectable(False)
            model.appendRow(item)
        combo.setModel(model)
        model.dataChanged.connect(lambda topLeft, bottomRight, roles: self.update_traits_display())

    def update_traits_display(self):
        combo = self.fields["traits"]
        model = combo.model()
        selected = []
        for i in range(model.rowCount()):
            item = model.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        combo.setCurrentText(", ".join(selected))
        self.fields["pay_driver_amount_m"].setVisible("pay driver" in selected)

    def load_active_teams(self):
        self.fields["contract_team"].clear()
        teams = read_json(self.teams_file) or []
        active_teams = [t["name"] for t in teams if t.get("active", False)]
        self.fields["contract_team"].addItem("Null")
        self.fields["contract_team"].addItems(active_teams)

    def on_team_changed(self):
        team = self.fields["contract_team"].currentText()
        read_only = team.lower() == "null"
        for key in ["contract_length_weeks", "contract_salary_m", "contract_start_week"]:
            self.fields[key].setReadOnly(read_only)
            if read_only:
                self.fields[key].setText("0")

    def load_data(self):
        self.drivers = read_json(self.file) or []
        self.update_driver_list()

    def update_driver_list(self):
        search_text = self.search_input.text().lower().strip()
        self.list.clear()
        for d in sorted(self.drivers, key=lambda x: x.get("name", "").lower()):
            if search_text in d.get("name", "").lower():
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
                elif contract_key == "role":
                    idx = widget.findText(driver.get("contract", {}).get("role", "null"))
                    widget.setCurrentIndex(idx if idx >= 0 else 0)
                else:
                    widget.setText(str(driver.get("contract", {}).get(contract_key, "")))
            elif key == "traits":
                self.set_traits_checkboxes(driver.get("traits", []))
            else:
                widget.setText(str(driver.get(key, "")))
        self.update_traits_display()
        self.on_team_changed()

    def set_traits_checkboxes(self, traits):
        model = self.fields["traits"].model()
        for i in range(model.rowCount()):
            item = model.item(i)
            item.setCheckState(Qt.CheckState.Checked if item.text() in traits else Qt.CheckState.Unchecked)

    def save_data(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        driver = self.drivers[idx]
        for key, widget in self.fields.items():
            if key.startswith("contract_"):
                contract_key = key.replace("contract_", "")
                driver.setdefault("contract", {})[contract_key] = widget.currentText() if contract_key in ["team","role"] else widget.text()
            elif key == "traits":
                driver["traits"] = [t.strip() for t in widget.currentText().split(",") if t.strip()]
            else:
                driver[key] = widget.text()
        write_json(self.file, self.drivers)
        QMessageBox.information(self, "Saved", f"Driver {driver.get('name')} updated!")
        self.load_data()
        self.list.setCurrentRow(idx)

    def add_driver(self):
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
            "traits": [],
            "contract": {
                "team": "Null",
                "role": "null",
                "length_weeks": 0,
                "salary_m": 0,
                "start_week": 1
            }
        }
        self.drivers.append(new_driver)
        self.load_data()
        self.list.setCurrentRow(len(self.drivers) - 1)

    def sort_drivers(self):
        self.drivers.sort(key=lambda x: x.get("name", "").lower())
        self.load_data()
