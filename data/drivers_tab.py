# drivers_tab.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QFormLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from utils import DATA_DIR, TAB_FILES, read_json, write_json, ACCENT, TEXT

TRAITS_LIST = [
    "hotlapper", "tyre_whisperer", "pay_driver", "overtake_artist",
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

        # --- Left: search box, driver list + add button ---
        left_layout = QVBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search drivers...")
        self.search_box.textChanged.connect(self.filter_drivers)
        left_layout.addWidget(self.search_box)

        self.list = QListWidget()
        left_layout.addWidget(self.list)

        self.add_btn = QPushButton("Add Driver")
        left_layout.addWidget(self.add_btn)
        self.add_btn.clicked.connect(self.add_driver)

        self.reload_btn = QPushButton("Reload Drivers")
        left_layout.addWidget(self.reload_btn)
        self.reload_btn.clicked.connect(self.load_data)

        layout.addLayout(left_layout, 1)

        # --- Right: scrollable form ---
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

        # Driver Details
        add_section_header("Driver Details")
        for field in ["name", "age", "talent", "train"]:
            self.fields[field] = QLineEdit()
            self.form_layout.addRow(QLabel(field.capitalize()), self.fields[field])

        # Pay driver field
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
        self.load_active_teams()
        self.form_layout.addRow(QLabel("Team"), self.fields["contract_team"])

        for field in ["length_weeks", "salary_m", "start_week", "role"]:
            key = f"contract_{field}"
            if field == "role":
                self.fields[key] = QComboBox()
                self.fields[key].addItems(["Null", "main", "reserve"])
            else:
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

        # Save + Delete buttons
        self.save_btn = QPushButton("Save Changes")
        self.form_layout.addRow(self.save_btn)
        self.delete_btn = QPushButton("Delete Driver")   ### DELETE DRIVER
        self.form_layout.addRow(self.delete_btn)

        # Data containers
        self.drivers = []
        self.filtered_drivers = []

        self.load_data()

        # Connections
        self.list.currentRowChanged.connect(self.display_driver)
        self.save_btn.clicked.connect(self.save_data)
        self.delete_btn.clicked.connect(self.delete_driver)   ### DELETE DRIVER
        self.add_btn.clicked.connect(self.add_driver)
        self.fields["contract_team"].currentIndexChanged.connect(self.on_team_changed)

    # --------------------
    # Traits combo helpers
    # --------------------
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
        model.dataChanged.connect(lambda *_: self.update_traits_display())

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

    # --------------------
    # Teams / contract UI
    # --------------------
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
        self.fields["contract_role"].setCurrentText("Null" if read_only else "main")

    # --------------------
    # Loading / filtering
    # --------------------
    def load_data(self):
        self.drivers = read_json(self.file) or []
        self.filtered_drivers = list(self.drivers)
        self.refresh_list()

    def refresh_list(self):
        self.list.clear()
        for d in self.filtered_drivers:
            self.list.addItem(d.get("name", "Unnamed"))

    def filter_drivers(self, text):
        text = (text or "").strip().lower()
        if not text:
            self.filtered_drivers = list(self.drivers)
        else:
            self.filtered_drivers = [d for d in self.drivers if text in d.get("name", "").lower()]
        self.refresh_list()

    # --------------------
    # Display / edit
    # --------------------
    def display_driver(self, index):
        if index < 0 or index >= len(self.filtered_drivers):
            for key, widget in self.fields.items():
                if isinstance(widget, QLineEdit):
                    widget.clear()
                elif isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)
            return

        driver = self.filtered_drivers[index]
        contract = driver.get("contract") or {}
        traits = driver.get("traits") or []

        for key, widget in self.fields.items():
            if key.startswith("contract_"):
                contract_key = key.replace("contract_", "")
                if contract_key == "team":
                    idx = widget.findText(contract.get("team", "Null"))
                    widget.setCurrentIndex(idx if idx >= 0 else 0)
                elif contract_key == "role":
                    idx = widget.findText(contract.get("role", "Null"))
                    widget.setCurrentIndex(idx if idx >= 0 else 0)
                else:
                    widget.setText(str(contract.get(contract_key, "")))
            elif key == "traits":
                self.set_traits_checkboxes(traits)
            else:
                widget.setText(str(driver.get(key, "")))

        self.update_traits_display()
        self.on_team_changed()

    def set_traits_checkboxes(self, traits):
        model = self.fields["traits"].model()
        for i in range(model.rowCount()):
            item = model.item(i)
            item.setCheckState(Qt.CheckState.Checked if item.text() in traits else Qt.CheckState.Unchecked)

    # --------------------
    # Save
    # --------------------
    def save_data(self):
        idx = self.list.currentRow()
        if idx < 0 or idx >= len(self.filtered_drivers):
            return
        driver = self.filtered_drivers[idx]
        try:
            original_idx = next(i for i, d in enumerate(self.drivers) if d is driver or d.get("name") == driver.get("name"))
        except StopIteration:
            original_idx = None

        driver_contract = driver.setdefault("contract", {})

        for key, widget in self.fields.items():
            if key.startswith("contract_"):
                contract_key = key.replace("contract_", "")
                if contract_key in ("team", "role"):
                    driver_contract[contract_key] = widget.currentText()
                else:
                    driver_contract[contract_key] = widget.text() or "0"
            elif key == "traits":
                driver["traits"] = [t.strip() for t in widget.currentText().split(",") if t.strip()]
            else:
                driver[key] = widget.text()

        if driver.get("contract", {}).get("team") in ("Null", None, ""):
            driver["contract"]["team"] = None
            driver["contract"]["length_weeks"] = 0
            driver["contract"]["salary_m"] = 0
            driver["contract"]["start_week"] = 1
            driver["contract"]["role"] = None

        if original_idx is not None:
            self.drivers[original_idx] = driver
        else:
            self.drivers.append(driver)

        write_json(self.file, self.drivers)
        QMessageBox.information(self, "Saved", f"Driver {driver.get('name')} updated!")
        self.load_data()
        name = driver.get("name")
        sel_index = next((i for i, d in enumerate(self.filtered_drivers) if d.get("name") == name), 0)
        self.list.setCurrentRow(sel_index)

    # --------------------
    # Add / Delete
    # --------------------
    def add_driver(self):
        new_driver = {
            "name": "New Driver",
            "age": "",
            "talent": "",
            "train": "",
            "pay_driver_amount_m": "0",
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
                "team": None,
                "length_weeks": 0,
                "salary_m": 0,
                "start_week": 1,
                "role": None
            }
        }
        self.drivers.append(new_driver)
        write_json(self.file, self.drivers)
        self.search_box.clear()
        self.load_data()
        sel_index = len(self.filtered_drivers) - 1
        self.list.setCurrentRow(sel_index)

    def delete_driver(self):   ### DELETE DRIVER
        idx = self.list.currentRow()
        if idx < 0 or idx >= len(self.filtered_drivers):
            return
        driver = self.filtered_drivers[idx]
        name = driver.get("name", "Unnamed")

        confirm = QMessageBox.question(
            self, "Delete Driver",
            f"Are you sure you want to delete driver '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.drivers.remove(driver)
            write_json(self.file, self.drivers)
            QMessageBox.information(self, "Deleted", f"Driver '{name}' removed.")
            self.load_data()
            self.list.setCurrentRow(-1)
