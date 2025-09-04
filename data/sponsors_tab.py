# sponsors_tab.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QFormLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from utils import DATA_DIR, TAB_FILES, read_json, write_json, ACCENT, TEXT


class SponsorsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file = DATA_DIR / TAB_FILES["sponsors"]

        # Main layout
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # Left: sponsor list + add button
        left_layout = QVBoxLayout()
        self.list = QListWidget()
        self.add_btn = QPushButton("Add Sponsor")
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
        self.sponsor_data = []

        self.create_fields()
        self.load_data()

        # Connections
        self.list.currentRowChanged.connect(self.display_sponsor)
        self.add_btn.clicked.connect(self.add_sponsor)

    def create_fields(self):
        lbl = QLabel("Sponsor Details")
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
        self.fields["rating"] = QLineEdit()
        self.fields["amount_m"] = QLineEdit()

        self.form_layout.addRow("Name", self.fields["name"])
        self.form_layout.addRow("Rating (1-10)", self.fields["rating"])
        self.form_layout.addRow("Amount (M)", self.fields["amount_m"])

        self.save_btn = QPushButton("Save Changes")
        self.form_layout.addRow(self.save_btn)
        self.save_btn.clicked.connect(self.save_sponsor)

    def load_data(self):
        self.sponsor_data = read_json(self.file) or []
        self.list.clear()
        for s in self.sponsor_data:
            self.list.addItem(s.get("name", "Unnamed"))

    def display_sponsor(self, index):
        if index < 0 or index >= len(self.sponsor_data):
            return
        sponsor = self.sponsor_data[index]
        self.fields["name"].setText(sponsor.get("name", ""))
        self.fields["rating"].setText(str(sponsor.get("rating", 1)))
        self.fields["amount_m"].setText(str(sponsor.get("amount_m", 0)))

    def save_sponsor(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        sponsor = self.sponsor_data[idx]

        sponsor["name"] = self.fields["name"].text()
        sponsor["rating"] = int(self.fields["rating"].text())
        sponsor["amount_m"] = float(self.fields["amount_m"].text())

        write_json(self.file, self.sponsor_data)
        QMessageBox.information(self, "Saved", f"Sponsor {sponsor['name']} updated!")
        self.load_data()
        self.list.setCurrentRow(idx)

    def add_sponsor(self):
        new_sponsor = {
            "name": "New Sponsor",
            "rating": 1,
            "amount_m": 10
        }
        self.sponsor_data.append(new_sponsor)
        write_json(self.file, self.sponsor_data)
        self.load_data()
        self.list.setCurrentRow(len(self.sponsor_data) - 1)
