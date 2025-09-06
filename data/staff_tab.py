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
        self.add_section_header("Staff Details")

        self.fields["name"] = QLineEdit()
        self.fields["role"] = QComboBox()
        self.fields["role"].addItems(list(ROLE_DISPLAY.values()))
        self.fields["team"] = QLineEdit()
        self.fields["skill"] = QLineEdit()
        self.fields["age"] = QLineEdit()

        for key in ["name", "role", "team", "skill", "age"]:
            label = key.replace("_", " ").capitalize()
            self.form_layout.addRow(label, self.fields[key])

        self.add_section_header("Contract")

        self.fields["contract_team"] = QLineEdit()
        self.fields["contract_length"] = QLineEdit()
        self.fields["contract_salary"] = QLineEdit()
        self.fields["contract_start"] = QLineEdit()

        for key in ["contract_team", "contract_length", "contract_salary", "contract_start"]:
            label = key.replace("_", " ").capitalize()
            self.form_layout.addRow(label, self.fields[key])

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
        self.fields["role"].setCurrentText(
            ROLE_DISPLAY.get(staff.get("role"), "Technical Director")
        )
        self.fields["team"].setText(staff.get("team") or "")
        self.fields["skill"].setText(str(staff.get("skill", "")))
        self.fields["age"].setText(str(staff.get("age", "")))

        contract = staff.get("contract") or {}
        self.fields["contract_team"].setText(contract.get("team", "") or "")
        self.fields["contract_length"].setText(str(contract.get("length_weeks", "")))
        self.fields["contract_salary"].setText(str(contract.get("salary_m", "")))
        self.fields["contract_start"].setText(str(contract.get("start_week", "")))

    def save_staff(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        staff = self.staff_data[idx]

        staff["name"] = self.fields["name"].text()
        staff["role"] = DISPLAY_ROLE_TO_JSON.get(
            self.fields["role"].currentText(), "technical_director"
        )
        staff["team"] = self.fields["team"].text() or None

        # safely cast numbers
        def safe_int(widget):
            try:
                return int(widget.text())
            except ValueError:
                return 0

        def safe_float(widget):
            try:
                return float(widget.text())
            except ValueError:
                return 0.0

        staff["skill"] = safe_int(self.fields["skill"])
        staff["age"] = safe_int(self.fields["age"])

        staff["contract"] = {
            "team": self.fields["contract_team"].text() or None,
            "length_weeks": safe_int(self.fields["contract_length"]),
            "salary_m": safe_float(self.fields["contract_salary"]),
            "start_week": safe_int(self.fields["contract_start"]),
        }

        write_json(self.file, self.staff_data)
        QMessageBox.information(self, "Saved", f"Staff {staff['name']} updated!")
        self.load_data()
        self.list.setCurrentRow(idx)

    def add_staff(self):
        new_staff = {
            "name": "New Staff",
            "role": "technical_director",  # default to TD
            "team": None,
            "skill": 10,
            "age": 30,
            "contract": {
                "team": None,
                "length_weeks": 0,
                "salary_m": 0.0,
                "start_week": 1,
            },
        }
        self.staff_data.append(new_staff)
        write_json(self.file, self.staff_data)
        self.load_data()
        self.list.setCurrentRow(len(self.staff_data) - 1)
