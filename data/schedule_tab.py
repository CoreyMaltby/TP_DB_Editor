# schedule_tab.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from utils import DATA_DIR, TAB_FILES, read_json, write_json, ACCENT, TEXT


class ScheduleTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file = DATA_DIR / TAB_FILES["schedule"]

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Scrollable form
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        layout.addWidget(self.detail_area, 1)

        detail_widget = QWidget()
        self.form_layout = QFormLayout(detail_widget)
        self.detail_area.setWidget(detail_widget)

        self.fields = []
        self.schedule_data = []

        # Buttons
        self.save_btn = QPushButton("Save Schedule")
        self.reload_btn = QPushButton("Reload Schedule")
        layout.addWidget(self.save_btn)
        layout.addWidget(self.reload_btn)

        # Connections
        self.save_btn.clicked.connect(self.save_schedule)
        self.reload_btn.clicked.connect(self.load_data)

        self.load_data()

    def load_data(self):
        self.schedule_data = read_json(self.file) or [None] * 52

        # Clear old fields
        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)
        self.fields = []

        for week, race in enumerate(self.schedule_data, start=1):
            lbl = QLabel(f"Week {week}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            field = QLineEdit()
            field.setText("" if race is None else str(race))
            field.textChanged.connect(lambda text, f=field: self.validate_input(f, text))
            self.form_layout.addRow(lbl, field)
            self.fields.append(field)

    def validate_input(self, field: QLineEdit, text: str):
        text = text.strip().lower()

        if text in ("", "null"):
            field.setStyleSheet("color: gray;")
            return
        elif text == "test":
            field.setStyleSheet("color: green;")
            return
        elif len(text) == 3 and text.isalpha():
            field.setStyleSheet("color: green;")
            return
        else:
            field.setStyleSheet("color: red;")

        # force lowercase
        if text != field.text():
            field.setText(text)

    def save_schedule(self):
        new_schedule = []
        for field in self.fields:
            val = field.text().strip().lower()
            if val in ("", "null"):
                new_schedule.append(None)
            elif val == "test":
                new_schedule.append("test")
            elif len(val) == 3 and val.isalpha():
                new_schedule.append(val)
            else:
                QMessageBox.warning(self, "Invalid Input", f"Invalid entry: {val}")
                return

        write_json(self.file, new_schedule)
        QMessageBox.information(self, "Saved", "Schedule updated successfully!")

