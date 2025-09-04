# events_tab.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QFormLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from utils import DATA_DIR, TAB_FILES, read_json, write_json, ACCENT, TEXT

# nicer display names for event types
EVENT_DISPLAY = {
    "team_join": "Team Join",
    "reg_change_aero": "Reg Change Aero",
    "reg_change_aero_minor": "Reg Change Aero Minor",
    "reg_change_engine": "Reg Change Engine",
    "reg_change_chassis_minor": "Reg Change Chassis Minor",
    "reg_change_chassis_major": "Reg Change Chassis Major",
    "team_package_aced": "Team Package Aced",
    "team_package_struggle": "Team Package Struggle"
}

DISPLAY_EVENT_TO_JSON = {v: k for k, v in EVENT_DISPLAY.items()}

TEAM_RELATED_EVENTS = ["team_join"]  # events that can have a team


class EventsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file = DATA_DIR / TAB_FILES["events"]
        self.teams_file = DATA_DIR / TAB_FILES["teams"]

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # Left: list of events + add & delete buttons
        left_layout = QVBoxLayout()
        self.list = QListWidget()
        self.add_btn = QPushButton("Add Event")
        self.delete_btn = QPushButton("Delete Event")
        left_layout.addWidget(self.list)
        left_layout.addWidget(self.add_btn)
        left_layout.addWidget(self.delete_btn)
        layout.addLayout(left_layout, 1)

        # Right: scrollable form
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        layout.addWidget(self.detail_area, 3)

        detail_widget = QWidget()
        self.form_layout = QFormLayout(detail_widget)
        self.detail_area.setWidget(detail_widget)

        self.fields = {}
        self.events_data = []
        self.teams_data = []

        self.load_teams()
        self.create_fields()
        self.load_data()

        # Connections
        self.list.currentRowChanged.connect(self.display_event)
        self.add_btn.clicked.connect(self.add_event_dialog)
        self.delete_btn.clicked.connect(self.delete_event)
        self.fields["type"].currentTextChanged.connect(self.update_team_field)

    def load_teams(self):
        self.teams_data = read_json(self.teams_file) or []
        self.team_names = [t.get("name") for t in self.teams_data]

    def create_fields(self):
        lbl = QLabel("Event Details")
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

        self.fields["type"] = QComboBox()
        self.fields["type"].addItems(list(EVENT_DISPLAY.values()))

        self.fields["team"] = QComboBox()  # dropdown for team
        self.fields["team"].addItems(self.team_names)

        self.fields["chance"] = QLineEdit()

        for key, widget in self.fields.items():
            label = key.replace("_", " ").capitalize()
            self.form_layout.addRow(label, widget)

        self.save_btn = QPushButton("Save Changes")
        self.form_layout.addRow(self.save_btn)
        self.save_btn.clicked.connect(self.save_event)

        # Initially update team field visibility
        self.update_team_field()

    def load_data(self):
        try:
            self.events_data = read_json(self.file) or []
        except FileNotFoundError:
            self.events_data = []
            write_json(self.file, self.events_data)

        self.list.clear()
        for e in self.events_data:
            event_type = EVENT_DISPLAY.get(e.get('type'), e.get('type', 'Unknown'))
            team = e.get('team')
            display_name = f"{event_type} – {team}" if team else event_type
            self.list.addItem(display_name)

    def display_event(self, index):
        if index < 0 or index >= len(self.events_data):
            return
        event = self.events_data[index]
        self.fields["type"].setCurrentText(EVENT_DISPLAY.get(event.get("type"), "Team Join"))

        # Update team field visibility
        self.update_team_field()

        if event.get("type") in TEAM_RELATED_EVENTS:
            self.fields["team"].setCurrentText(event.get("team") or "")
        self.fields["chance"].setText(str(event.get("chance", 0)))

    def save_event(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        event = self.events_data[idx]

        event["type"] = DISPLAY_EVENT_TO_JSON[self.fields["type"].currentText()]
        if event["type"] in TEAM_RELATED_EVENTS:
            event["team"] = self.fields["team"].currentText()
        else:
            event["team"] = None
        event["chance"] = float(self.fields["chance"].text())

        write_json(self.file, self.events_data)
        QMessageBox.information(self, "Saved", f"Event updated!")
        self.load_data()
        self.list.setCurrentRow(idx)

    def add_event_dialog(self):
        # Ask for event type
        type_dialog = QComboBox()
        type_dialog.addItems(list(EVENT_DISPLAY.values()))
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Select Event Type")
        msg_box.setText("Choose the type of event to add:")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg_box.layout().addWidget(type_dialog, 1, 1)
        ret = msg_box.exec()

        if ret == QMessageBox.StandardButton.Ok:
            chosen_type = DISPLAY_EVENT_TO_JSON[type_dialog.currentText()]
            self.add_event(chosen_type)

    def add_event(self, event_type="team_join"):
        new_event = {
            "type": event_type,
            "team": self.team_names[0] if event_type in TEAM_RELATED_EVENTS else None,
            "chance": 0.05
        }
        self.events_data.append(new_event)
        write_json(self.file, self.events_data)
        self.load_data()
        self.list.setCurrentRow(len(self.events_data) - 1)

    def delete_event(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        event = self.events_data[idx]

        confirm = QMessageBox.question(
            self, "Delete Event",
            f"Are you sure you want to delete '{self.list.item(idx).text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.events_data.pop(idx)
            write_json(self.file, self.events_data)
            self.load_data()
            self.list.setCurrentRow(min(idx, len(self.events_data) - 1))

    def update_team_field(self):
        current_type = DISPLAY_EVENT_TO_JSON.get(self.fields["type"].currentText())
        if current_type in TEAM_RELATED_EVENTS:
            self.fields["team"].setEnabled(True)
            self.fields["team"].show()
        else:
            self.fields["team"].setEnabled(False)
            self.fields["team"].hide()
