# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget

from utils import TAB_FILES, DATA_DIR, ACCENT, TEXT, BG, read_json, write_json
from drivers_tab import DriversTab
from teams_tab import TeamsTab
from table_tab import TableTab
from engines_tab import EnginesTab
from sponsors_tab import SponsorsTab
from staff_tab import  StaffTab
from events_tab import  EventsTab
from config_tab import ConfigTab
from schedule_tab import ScheduleTab

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Team Principal Manager — Editor")
        self.resize(1000, 650)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.vlayout = QVBoxLayout()
        self.central.setLayout(self.vlayout)

        # Tabs
        self.tabs = QTabWidget()
        self.tab_objs = {}

        for name in TAB_FILES.keys():
            if name == "drivers":
                tab = DriversTab()
            elif name == "teams":
                tab = TeamsTab()
            elif name == "engines":
                tab = EnginesTab()
            elif name == "sponsors":
                tab = SponsorsTab()
            elif name == "staff":
                tab = StaffTab()
            elif name == "events":
                tab = EventsTab()
            elif name == "config":
                tab = ConfigTab()
            elif name == "schedule":
                tab = ScheduleTab()
            else:
                tab = TableTab(name)
            self.tab_objs[name] = tab
            self.tabs.addTab(tab, name.capitalize())

        self.vlayout.addWidget(self.tabs)
        self.apply_styles()

    def apply_styles(self):
        style = f"""
        QMainWindow, QWidget {{
            background-color: {BG};
            color: {TEXT};
            font-family: Arial, Helvetica, sans-serif;
        }}
        QLabel, QPushButton, QTableWidget {{
            color: {TEXT};
        }}
        QPushButton {{
            background-color: transparent;
            border: 1px solid {TEXT};
            padding: 6px;
            border-radius: 6px;
        }}
        QPushButton:hover {{
            border-color: {ACCENT};
            color: {ACCENT};
        }}
        QTabBar::tab {{
            background: #2f3436;
            color: {TEXT};
            padding: 8px;
            margin: 2px;
            border-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background: {ACCENT};
            color: white;
        }}
        QTableWidget {{
            background-color: #2e3132;
            gridline-color: #444;
        }}
        QHeaderView::section {{
            background-color: #2b2f30;
            color: {TEXT};
            padding: 4px;
        }}
        """
        self.setStyleSheet(style)

# --- Ensure default JSON files ---
def ensure_default_files():
    for name, filename in TAB_FILES.items():
        p = DATA_DIR / filename
        if not p.exists():
            if name == "config":
                default = {"game_name": "Team Principal Manager", "version": "0.1"}
            elif name == "drivers":
                default = [
                    {
                        "name": "John Doe",
                        "team": "Team A",
                        "age": 25,
                        "talent": 80,
                        "train": 5,
                        "pay_driver_amount_m": 1.2,
                        "base_lap_time_sim": 90.5,
                        "number": 7,
                        "cornering": 75,
                        "braking": 70,
                        "consistency": 85,
                        "smoothness": 80,
                        "control": 78,
                        "seasons": 3,
                        "championships": 1,
                        "wins": 5,
                        "podiums": 10,
                        "poles": 2,
                        "contract": {
                            "team": "Team A",
                            "length_weeks": 52,
                            "salary_m": 2.5,
                            "start_week": 1
                        }
                    }
                ]
            elif name == "teams":
                default = []
            else:
                default = []
            write_json(p, default)

# --- Main entry ---
def main():
    ensure_default_files()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
