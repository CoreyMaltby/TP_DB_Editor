# staff_tab.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QFormLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from utils import DATA_DIR, TAB_FILES, read_json, write_json, ACCENT, TEXT


# mapping for nicer role names in the UI
ROLE_DISPLAY = {
    "technical_director": "Technical Director",
    "chief_designer": "Chief Designer",
    "head_of_dynamics": "Head of Dynamics",
    "chief_mechanic": "Chief Mechanic"
}

DISPLAY_ROLE_TO_JSON = {v: k for k, v in ROLE_DISPLAY.items()}



class StaffTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file = DATA_DIR / TAB_FILES["staff"]

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # Left: staff list + add button
        left_layout = QVBoxLayout()
        self.list = QListWidget()
        self.add_btn = QPushButton("Add Staff")
        left_layout.addWidget(self.list)
        left_layout.addWidget(self.add_btn)
        layout.addLayout(left_layout, 1)

        # Right: scrollable form
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        layout.addWidget(self.detail_area, 3)

        detail_widget = QWidget()
        self.form_layout = QFormLayout(detail_widget)
        self.detail_area.setWidget(detail_widget)

        self.fields = {}
        self.staff_data = []

        self.create_fields()
        self.load_data()

        # Connections
        self.list.currentRowChanged.connect(self.display_staff)
        self.add_btn.clicked.connect(self.add_staff)

    def create_fields(self):
        lbl = QLabel("Staff Details")
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

        self.fields["name"] = QLineEdit()
        self.fields["role"] = QComboBox()
        self.fields["role"].addItems(list(ROLE_DISPLAY.values()))
        self.fields["team"] = QLineEdit()
        self.fields["skill"] = QLineEdit()
        self.fields["age"] = QLineEdit()
        self.fields["contract_team"] = QLineEdit()
        self.fields["contract_length"] = QLineEdit()
        self.fields["contract_salary"] = QLineEdit()
        self.fields["contract_start"] = QLineEdit()

        for key, widget in self.fields.items():
            label = key.replace("_", " ").capitalize()
            self.form_layout.addRow(label, widget)

        self.save_btn = QPushButton("Save Changes")
        self.form_layout.addRow(self.save_btn)
        self.save_btn.clicked.connect(self.save_staff)

    def load_data(self):
        self.staff_data = read_json(self.file) or []
        self.list.clear()
        for s in self.staff_data:
            self.list.addItem(s.get("name", "Unnamed"))

    def display_staff(self, index):
        if index < 0 or index >= len(self.staff_data):
            return
        staff = self.staff_data[index]
        self.fields["name"].setText(staff.get("name", ""))
        self.fields["role"].setCurrentText(ROLE_DISPLAY.get(staff.get("role"), "Technical Director"))
        self.fields["team"].setText(staff.get("team") or "")
        self.fields["skill"].setText(str(staff.get("skill", 0)))
        self.fields["age"].setText(str(staff.get("age", 0)))

        contract = staff.get("contract") or {}
        self.fields["contract_team"].setText(contract.get("team") or "")
        self.fields["contract_length"].setText(str(contract.get("length_weeks", 0)))
        self.fields["contract_salary"].setText(str(contract.get("salary_m", 0)))
        self.fields["contract_start"].setText(str(contract.get("start_week", 0)))

    def save_staff(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        staff = self.staff_data[idx]

        staff["name"] = self.fields["name"].text()
        staff["role"] = DISPLAY_ROLE_TO_JSON[self.fields["role"].currentText()]
        staff["team"] = self.fields["team"].text() or None
        staff["skill"] = int(self.fields["skill"].text())
        staff["age"] = int(self.fields["age"].text())

        if staff["team"]:
            staff["contract"] = {
                "team": self.fields["contract_team"].text() or staff["team"],
                "length_weeks": int(self.fields["contract_length"].text()),
                "salary_m": float(self.fields["contract_salary"].text()),
                "start_week": int(self.fields["contract_start"].text())
            }
        else:
            staff["contract"] = None

        write_json(self.file, self.staff_data)
        QMessageBox.information(self, "Saved", f"Staff {staff['name']} updated!")
        self.load_data()
        self.list.setCurrentRow(idx)

    def add_staff(self):
        new_staff = {
            "name": "New Staff",
            "role": ROLES[0],
            "team": None,
            "skill": 10,
            "age": 30,
            "contract": None
        }
        self.staff_data.append(new_staff)
        write_json(self.file, self.staff_data)
        self.load_data()
        self.list.setCurrentRow(len(self.staff_data) - 1)
