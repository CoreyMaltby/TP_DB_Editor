# teams_tab.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QFormLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QMessageBox,
    QCheckBox, QColorDialog, QComboBox, QFrame
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

from utils import DATA_DIR, TAB_FILES, read_json, write_json, ACCENT, TEXT


class TeamsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file = DATA_DIR / TAB_FILES["teams"]
        self.engines_file = DATA_DIR / TAB_FILES["engines"]

        # Main layout
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # Left: team list + add team button
        left_layout = QVBoxLayout()
        self.list = QListWidget()
        self.add_btn = QPushButton("Add Team")
        left_layout.addWidget(self.list)
        left_layout.addWidget(self.add_btn)
        layout.addLayout(left_layout, 1)

        # Right: scrollable detail form
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        layout.addWidget(self.detail_area, 3)

        detail_widget = QWidget()
        self.form_layout = QFormLayout(detail_widget)
        self.detail_area.setWidget(detail_widget)

        self.fields = {}
        self.team_data = []

        self.create_sections()
        self.load_engines()
        self.load_data()

        # Connections
        self.list.currentRowChanged.connect(self.display_team)
        self.add_btn.clicked.connect(self.add_team)

    def create_sections(self):
        """Create sections and fields in the form"""

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

        # Details
        add_section_header("Details")
        self.fields["name"] = QLineEdit()
        self.fields["active"] = QCheckBox("Active")
        self.fields["color_rgb"] = QPushButton("Select Color")
        self.fields["color_display"] = QFrame()
        self.fields["color_display"].setFixedSize(50, 20)
        self.fields["color_display"].setStyleSheet("background-color: #FFFFFF; border: 1px solid #000;")
        self.fields["prestige_base"] = QLineEdit()
        self.fields["negotiation_points"] = QLineEdit()

        self.form_layout.addRow("Name", self.fields["name"])
        self.form_layout.addRow("Active", self.fields["active"])
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.fields["color_rgb"])
        color_layout.addWidget(self.fields["color_display"])
        self.form_layout.addRow("Color", color_layout)
        self.form_layout.addRow("Prestige", self.fields["prestige_base"])
        self.form_layout.addRow("Negotiation Points", self.fields["negotiation_points"])
        self.fields["color_rgb"].clicked.connect(self.select_color)

        # Performance
        add_section_header("Performance")
        for key in ["team_pace_slow", "team_pace_med", "team_pace_high",
                    "attr_slow", "attr_med", "attr_high", "attr_straight",
                    "tyre_management", "dirty_air_sensitivity"]:
            self.fields[key] = QLineEdit()
            self.form_layout.addRow(key.replace("_", " ").capitalize(), self.fields[key])

        # Upgrades
        add_section_header("Upgrades")
        for key in ["front_wing", "underfloor", "rear_wing", "drag", "chassis"]:
            self.fields[key] = QLineEdit()
            self.form_layout.addRow(key.replace("_", " ").capitalize(), self.fields[key])

        # Engine
        add_section_header("Engine")
        self.fields["engine"] = QComboBox()
        self.fields["engine_contract_seasons"] = QLineEdit()
        self.form_layout.addRow("Engine", self.fields["engine"])
        self.form_layout.addRow("Engine Contract Seasons", self.fields["engine_contract_seasons"])

        # History
        add_section_header("History")
        for key in ["seasons", "championships", "wins", "podiums", "poles"]:
            self.fields[key] = QLineEdit()
            self.form_layout.addRow(key.capitalize(), self.fields[key])

        # Headquarters
        add_section_header("Headquarters")
        for key in ["hospitality_pr_center", "wind_tunnel", "engine_plant"]:
            self.fields[key] = QLineEdit()
            self.form_layout.addRow(key.replace("_", " ").capitalize(), self.fields[key])

        # Save button
        self.save_btn = QPushButton("Save Changes")
        self.form_layout.addRow(self.save_btn)
        self.save_btn.clicked.connect(self.save_team)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.fields["color_display"].setStyleSheet(f"background-color: {color.name()}; border: 1px solid #000;")
            self.fields["color_rgb"].setProperty("color", color)

    def load_engines(self):
        self.fields["engine"].clear()
        engines_data = read_json(self.engines_file) or {}
        engines_dict = engines_data.get("engines", {})  # Extract the dict under "engines"
        self.fields["engine"].addItem("Null")
        for engine_name in engines_dict.keys():
            self.fields["engine"].addItem(engine_name)

    def load_data(self):
        self.team_data = read_json(self.file) or []
        self.list.clear()
        for t in self.team_data:
            self.list.addItem(t.get("name", "Unnamed"))

    def display_team(self, index):
        # Guard against invalid index
        if index < 0 or index >= len(self.team_data):
            # Clear all fields
            for key, field in self.fields.items():
                if isinstance(field, QLineEdit):
                    field.clear()
                elif isinstance(field, QCheckBox):
                    field.setChecked(False)
                elif isinstance(field, QComboBox):
                    field.setCurrentIndex(0)
                elif isinstance(field, QFrame):
                    field.setStyleSheet("background-color: #FFFFFF; border: 1px solid #000;")
            return

        self.reload_engines()
        team = self.team_data[index]

        # Block signals to avoid recursive updates
        for field in self.fields.values():
            try:
                field.blockSignals(True)
            except Exception:
                pass

        # Details
        self.fields["name"].setText(team.get("name", ""))
        self.fields["active"].setChecked(team.get("active", True))
        rgb = team.get("color_rgb", [255, 255, 255])
        color_hex = "#{:02x}{:02x}{:02x}".format(*rgb)
        self.fields["color_display"].setStyleSheet(f"background-color: {color_hex}; border: 1px solid #000;")
        self.fields["prestige_base"].setText(str(team.get("prestige_base", 0)))
        self.fields["negotiation_points"].setText(str(team.get("negotiation_points", 0)))

        # Performance
        pace = team.get("team_pace", {})
        if isinstance(pace, dict):
            self.fields["team_pace_slow"].setText(str(pace.get("slow", 0)))
            self.fields["team_pace_med"].setText(str(pace.get("med", 0)))
            self.fields["team_pace_high"].setText(str(pace.get("high", 0)))
        attr = team.get("attr", {})
        if isinstance(attr, dict):
            self.fields["attr_slow"].setText(str(attr.get("slow", 0)))
            self.fields["attr_med"].setText(str(attr.get("med", 0)))
            self.fields["attr_high"].setText(str(attr.get("high", 0)))
            self.fields["attr_straight"].setText(str(attr.get("straight", 0)))
        self.fields["tyre_management"].setText(str(team.get("tyre_management", 0)))
        self.fields["dirty_air_sensitivity"].setText(str(team.get("dirty_air_sensitivity", 0)))

        # Upgrades
        upgrades = team.get("upgrades", {})
        for key in ["front_wing", "underfloor", "rear_wing", "drag", "chassis"]:
            self.fields[key].setText(str(upgrades.get(key, 0)))

        # Engine
        engine_name = team.get("engine", "Null") or "Null"
        idx = self.fields["engine"].findText(engine_name)
        self.fields["engine"].setCurrentIndex(idx if idx >= 0 else 0)
        self.fields["engine_contract_seasons"].setText(str(team.get("engine_contract_seasons", 0)))

        # History
        history = team.get("history", {})
        if isinstance(history, dict):
            for key in ["seasons", "championships", "wins", "podiums", "poles"]:
                self.fields[key].setText(str(history.get(key, 0)))
        else:
            # Fallback if history is malformed
            for key in ["seasons", "championships", "wins", "podiums", "poles"]:
                self.fields[key].setText("0")

        # Headquarters
        hq = team.get("headquarters", {})
        if isinstance(hq, dict):
            for key in ["hospitality_pr_center", "wind_tunnel", "engine_plant"]:
                self.fields[key].setText(str(hq.get(key, 0)))
        else:
            for key in ["hospitality_pr_center", "wind_tunnel", "engine_plant"]:
                self.fields[key].setText("0")

        # Unblock signals
        for field in self.fields.values():
            try:
                field.blockSignals(False)
            except Exception:
                pass

    def save_team(self):
        idx = self.list.currentRow()
        if idx < 0:
            return
        team = self.team_data[idx]

        # Details
        team["name"] = self.fields["name"].text()
        team["active"] = self.fields["active"].isChecked()
        color_style = self.fields["color_display"].styleSheet()
        color_hex = color_style.split("background-color:")[1].split(";")[0].strip()
        color_rgb = [int(color_hex[i:i + 2], 16) for i in (1, 3, 5)]
        team["color_rgb"] = color_rgb
        team["prestige_base"] = float(self.fields["prestige_base"].text())
        team["negotiation_points"] = int(self.fields["negotiation_points"].text())

        # Performance
        team["team_pace"] = {
            "slow": float(self.fields["team_pace_slow"].text()),
            "med": float(self.fields["team_pace_med"].text()),
            "high": float(self.fields["team_pace_high"].text())
        }
        team["attr"] = {
            "slow": float(self.fields["attr_slow"].text()),
            "med": float(self.fields["attr_med"].text()),
            "high": float(self.fields["attr_high"].text()),
            "straight": float(self.fields["attr_straight"].text())
        }
        team["tyre_management"] = float(self.fields["tyre_management"].text())
        team["dirty_air_sensitivity"] = float(self.fields["dirty_air_sensitivity"].text())

        # Upgrades
        team["upgrades"] = {key: float(self.fields[key].text()) for key in
                            ["front_wing", "underfloor", "rear_wing", "drag", "chassis"]}

        # Engine
        engine = self.fields["engine"].currentText()
        team["engine"] = None if engine == "Null" else engine
        team["engine_contract_seasons"] = int(self.fields["engine_contract_seasons"].text())

        # History
        team["history"] = {key: int(self.fields[key].text()) for key in
                           ["seasons", "championships", "wins", "podiums", "poles"]}

        # Headquarters
        team["headquarters"] = {key: int(self.fields[key].text()) for key in
                                ["hospitality_pr_center", "wind_tunnel", "engine_plant"]}

        write_json(self.file, self.team_data)
        QMessageBox.information(self, "Saved", f"Team {team['name']} updated!")
        self.load_data()
        self.list.setCurrentRow(idx)

    def reload_engines(self):
        """Reload the engine dropdown from engines.json"""
        current_engine = self.fields["engine"].currentText()
        self.load_engines()
        # Try to restore previously selected engine
        idx = self.fields["engine"].findText(current_engine)
        self.fields["engine"].setCurrentIndex(idx if idx >= 0 else 0)

    def add_team(self):
        """Add a new blank team"""
        new_team = {
            "name": "New Team",
            "active": True,
            "color_rgb": [255, 255, 255],
            "prestige_base": 50,
            "negotiation_points": 0,
            "team_pace": {"slow": 0, "med": 0, "high": 0},
            "attr": {"slow": 0, "med": 0, "high": 0, "straight": 0},
            "tyre_management": 1.0,
            "dirty_air_sensitivity": 1.0,
            "upgrades": {"front_wing": 0, "underfloor": 0, "rear_wing": 0, "drag": 0, "chassis": 0},
            "engine": None,
            "engine_contract_seasons": 0,
            "history": {"seasons": 0, "championships": 0, "wins": 0, "podiums": 0, "poles": 0},
            "headquarters": {"hospitality_pr_center": 0, "wind_tunnel": 0, "engine_plant": 0}
        }
        self.team_data.append(new_team)
        write_json(self.file, self.team_data)
        self.load_data()
        self.list.setCurrentRow(len(self.team_data) - 1)
