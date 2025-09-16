# tyre_suppliers_tab.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QListWidget,
    QPushButton, QLineEdit, QTabWidget, QFormLayout, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from utils import DATA_DIR, TAB_FILES, read_json, write_json


class TyreSuppliersTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file = DATA_DIR / TAB_FILES["tyre_suppliers"]

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # --- Left: supplier list + add ---
        left_layout = QVBoxLayout()
        self.list = QListWidget()
        self.add_btn = QPushButton("Add Supplier")
        left_layout.addWidget(self.list)
        left_layout.addWidget(self.add_btn)
        layout.addLayout(left_layout, 1)

        # --- Right: scrollable form with tabs ---
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        layout.addWidget(self.detail_area, 3)

        detail_widget = QWidget()
        self.tabs = QTabWidget(detail_widget)
        main_layout = QVBoxLayout(detail_widget)
        main_layout.addWidget(self.tabs)
        self.detail_area.setWidget(detail_widget)

        self.fields = {}
        self.suppliers = []

        # Build tabs
        self.create_tabs()

        # Save button
        self.save_btn = QPushButton("Save Changes")
        main_layout.addWidget(self.save_btn)

        # Connections
        self.add_btn.clicked.connect(self.add_supplier)
        self.list.currentRowChanged.connect(self.display_supplier)
        self.save_btn.clicked.connect(self.save_supplier)

        self.load_data()

    def create_tabs(self):
        # Tyres tab with sub-tabs
        tyres_tab = QTabWidget()
        self.tabs.addTab(tyres_tab, "Tyres")

        for compound in ["soft", "medium", "hard"]:
            form = QFormLayout()
            page = QWidget()
            page.setLayout(form)
            self.fields[f"pace_{compound}"] = QLineEdit()
            self.fields[f"durability_{compound}"] = QLineEdit()
            form.addRow("Pace (-1 to 1)", self.fields[f"pace_{compound}"])
            form.addRow("Durability (-1 to 1)", self.fields[f"durability_{compound}"])
            tyres_tab.addTab(page, compound.capitalize())

        # Trend tab
        trend_form = QFormLayout()
        trend_page = QWidget()
        trend_page.setLayout(trend_form)
        for attr in ["pace", "durability"]:
            self.fields[f"trend_{attr}"] = QLineEdit()
            trend_form.addRow(attr.capitalize(), self.fields[f"trend_{attr}"])
        self.tabs.addTab(trend_page, "Trend")

        # Variance tab
        var_form = QFormLayout()
        var_page = QWidget()
        var_page.setLayout(var_form)
        for attr in ["pace", "durability"]:
            self.fields[f"variance_{attr}"] = QLineEdit()
            var_form.addRow(attr.capitalize(), self.fields[f"variance_{attr}"])
        self.tabs.addTab(var_page, "Variance")

        # Prices tab
        price_form = QFormLayout()
        price_page = QWidget()
        price_page.setLayout(price_form)
        for t in ["works", "partner", "customer"]:
            self.fields[f"price_{t}"] = QLineEdit()
            price_form.addRow(t.capitalize(), self.fields[f"price_{t}"])
        self.tabs.addTab(price_page, "Prices")

    def load_data(self):
        data = read_json(self.file) or {"suppliers": {}}
        self.suppliers = []
        self.list.clear()
        for name, info in data.get("suppliers", {}).items():
            supplier = {"name": name}
            supplier.update(info)
            self.suppliers.append(supplier)
            self.list.addItem(name)

    def display_supplier(self, index):
        if index < 0 or index >= len(self.suppliers):
            for field in self.fields.values():
                field.clear()
            return

        supplier = self.suppliers[index]

        # Fill tyre compound data
        for compound in ["soft", "medium", "hard"]:
            self.fields[f"pace_{compound}"].setText(str(supplier.get("pace", {}).get(compound, 0)))
            self.fields[f"durability_{compound}"].setText(str(supplier.get("durability", {}).get(compound, 0)))

        # Fill trend + variance
        for attr in ["pace", "durability"]:
            self.fields[f"trend_{attr}"].setText(str(supplier.get("trend", {}).get(attr, 0)))
            self.fields[f"variance_{attr}"].setText(str(supplier.get("variance", {}).get(attr, 0)))

        # Fill prices
        for t in ["works", "partner", "customer"]:
            self.fields[f"price_{t}"].setText(str(supplier.get("prices", {}).get(t, 0)))

    def save_supplier(self):
        idx = self.list.currentRow()
        if idx < 0:
            return

        supplier = {
            "pace": {c: float(self.fields[f"pace_{c}"].text() or 0) for c in ["soft", "medium", "hard"]},
            "durability": {c: float(self.fields[f"durability_{c}"].text() or 0) for c in ["soft", "medium", "hard"]},
            "prices": {t: float(self.fields[f"price_{t}"].text() or 0) for t in ["works", "partner", "customer"]},
            "trend": {a: float(self.fields[f"trend_{a}"].text() or 0) for a in ["pace", "durability"]},
            "variance": {a: float(self.fields[f"variance_{a}"].text() or 0) for a in ["pace", "durability"]}
        }

        # Update supplier
        name = self.list.item(idx).text()
        self.suppliers[idx] = {"name": name, **supplier}

        # Save JSON
        data = {"suppliers": {s["name"]: {
            "pace": s["pace"], "durability": s["durability"],
            "prices": s["prices"], "trend": s["trend"], "variance": s["variance"]
        } for s in self.suppliers}}
        write_json(self.file, data)
        QMessageBox.information(self, "Saved", f"Supplier {name} updated!")

    def add_supplier(self):
        new_name = "New Supplier"
        new_supplier = {
            "name": new_name,
            "pace": {"soft": 0, "medium": 0, "hard": 0},
            "durability": {"soft": 0, "medium": 0, "hard": 0},
            "prices": {"works": 0, "partner": 0, "customer": 0},
            "trend": {"pace": 0, "durability": 0},
            "variance": {"pace": 0, "durability": 0}
        }
        self.suppliers.append(new_supplier)

        # Save and reload
        data = {"suppliers": {s["name"]: {
            "pace": s["pace"], "durability": s["durability"],
            "prices": s["prices"], "trend": s["trend"], "variance": s["variance"]
        } for s in self.suppliers}}
        write_json(self.file, data)
        self.load_data()
        self.list.setCurrentRow(len(self.suppliers) - 1)
