# teams_tab.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QFormLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from utils import DATA_DIR, TAB_FILES, read_json, write_json, ACCENT, TEXT


class TeamsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file = DATA_DIR / TAB_FILES["teams"]
        self.tyre_suppliers_file = DATA_DIR / TAB_FILES["tyre_suppliers"]

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # --- Left: team list + add button ---
        left_layout = QVBoxLayout()
        self.list = QListWidget()
        left_layout.addWidget(self.list)

        self.add_btn = QPushButton("Add Team")
        left_layout.addWidget(self.add_btn)

        layout.addLayout(left_layout, 1)

        # --- Right: scrollable form ---
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        layout.addWidget(self.detail_area, 3)

        detail_widget = QWidget()
        self.form_layout = QFormLayout(detail_widget)
        self.detail_area.setWidget(detail_widget)

        self.fields = {}
        self.teams_data = []

        self.create_fields()
        self.load_data()

        # Connections
        self.list.currentRowChanged.connect(self.display_team)
        self.add_btn.clicked.connect(self.add_team)
        self.save_btn.clicked.connect(self.save_team)

    def add_section_header(self, title):
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

    def create_fields(self):
        # --- Details ---
        self.add_section_header("Team Details")
        for field in ["name", "short_name", "country", "budget_m"]:
            self.fields[field] = QLineEdit()
            self.form_layout.addRow(QLabel(field.replace("_", " ").capitalize()), self.fields[field])

        # --- Headquarters ---
        self.add_section_header("Headquarters")
        for field in ["wind_tunnel", "factory", "simulator", "test_track"]:
            self.fields[field] = QLineEdit()
            self.form_layout.addRow(QLabel(field.replace("_", " ").capitalize()), self.fields[field])

        # --- Tyre Contract ---
        self.add_section_header("Tyre Contract")
        self.fields["tyre_supplier"] = QComboBox()
        self.fields["tyre_type"] = QComboBox()
        self.fields["tyre_type"].addItems(["partner", "works", "customer"])
        self.form_layout.addRow(QLabel("Supplier"), self.fields["tyre_supplier"])
        self.form_layout.addRow(QLabel("Type"), self.fields["tyre_type"])

        # Save button
        self.save_btn = QPushButton("Save Changes")
        self.form_layout.addRow(self.save_btn)

    def load_data(self):
        # Load teams
        self.teams_data = read_json(self.file) or []
        self.list.clear()
        for t in self.teams_data:
            self.list.addItem(t.get("name", "Unnamed"))

        # Load tyre suppliers
        suppliers_data = read_json(self.tyre_suppliers_file) or {"suppliers": {}}
        supplier_names = list(suppliers_data.get("suppliers", {}).keys())

        self.fields["tyre_supplier"].clear()
        self.fields["tyre_supplier"].addItem("Null")
        self.fields["tyre_supplier"].addItems(supplier_names)

    def display_team(self, index):
        if index < 0 or index >= len(self.teams_data):
            return
        team = self.teams_data[index]

        self.fields["name"].setText(team.get("name", ""))
        self.fields["short_name"].setText(team.get("short_name", ""))
        self.fields["country"].setText(team.get("country", ""))
        self.fields["budget_m"].setText(str(team.get("budget_m", 0)))

        hq = team.get("headquarters", {})
        self.fields["wind_tunnel"].setText(str(hq.get("wind_tunnel", 0)))
        self.fields["factory"].setText(str(hq.get("factory", 0)))
        self.fields["simulator"].setText(str(hq.get("simulator", 0)))
        self.fields["test_track"].setText(str(hq.get("test_track", 0)))

        tyre = team.get("tyre_contract", {})
        supplier = tyre.get("supplier", "")
        idx = self.fields["tyre_supplier"].findText(supplier)
        self.fields["tyre_supplier"].setCurrentIndex(idx if idx >= 0 else 0)
        tyre_type = tyre.get("type", "partner")
        idx = self.fields["tyre_type"].findText(tyre_type)
        self.fields["tyre_type"].setCurrentIndex(idx if idx >= 0 else 0)

    def save_team(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        team = self.teams_data[idx]

        team["name"] = self.fields["name"].text()
        team["short_name"] = self.fields["short_name"].text()
        team["country"] = self.fields["country"].text()
        team["budget_m"] = float(self.fields["budget_m"].text() or 0)

        team["headquarters"] = {
            "wind_tunnel": int(self.fields["wind_tunnel"].text() or 0),
            "factory": int(self.fields["factory"].text() or 0),
            "simulator": int(self.fields["simulator"].text() or 0),
            "test_track": int(self.fields["test_track"].text() or 0),
        }

        team["tyre_contract"] = {
            "supplier": self.fields["tyre_supplier"].currentText(),
            "type": self.fields["tyre_type"].currentText()
        }

        write_json(self.file, self.teams_data)
        QMessageBox.information(self, "Saved", f"Team {team['name']} updated!")
        self.load_data()
        self.list.setCurrentRow(idx)

    def add_team(self):
        new_team = {
            "name": "New Team",
            "short_name": "",
            "country": "",
            "budget_m": 0,
            "headquarters": {
                "wind_tunnel": 0,
                "factory": 0,
                "simulator": 0,
                "test_track": 0
            },
            "tyre_contract": {
                "supplier": "",
                "type": "partner"
            }
        }
        self.teams_data.append(new_team)
        write_json(self.file, self.teams_data)
        self.load_data()
        self.list.setCurrentRow(len(self.teams_data) - 1)
