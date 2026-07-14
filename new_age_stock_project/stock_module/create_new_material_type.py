import sys
import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QLineEdit, QComboBox, QMessageBox, QApplication, QMainWindow)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)
DATA_FILE = os.path.join(project_root, "kategoriler.json")

class UrunTuruOlusturmaPaneli(QWidget):
    def __init__(self, ana_pencere=None):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel("🏗️ Malzeme Türü Seçin:"))
        self.cb_material = QComboBox()
        layout.addWidget(self.cb_material)

        layout.addWidget(QLabel("📂 Grup Türü Seçin:"))
        self.cb_group = QComboBox()
        layout.addWidget(self.cb_group)

        layout.addWidget(QLabel("📦 Yeni Ürün Türü Adı (Örn: Süt, Deterjan):"))
        self.input_urun_ad = QLineEdit()
        layout.addWidget(self.input_urun_ad)

        layout.addWidget(QLabel("⚖️ Birim (Örn: Adet, KG, Litre):"))
        self.input_birim = QLineEdit()
        self.input_birim.setPlaceholderText("Varsayılan: Adet")
        layout.addWidget(self.input_birim)

        self.btn_kaydet = QPushButton("📦 ÜRÜN TÜRÜNÜ SİSTEME İŞLE")
        self.btn_kaydet.setMinimumHeight(45)
        self.btn_kaydet.setStyleSheet("background-color: #8E44AD; color: white; font-weight: bold;")
        self.btn_kaydet.clicked.connect(self.urun_turu_kaydet)
        layout.addWidget(self.btn_kaydet)

        self.btn_iptal = QPushButton("GERİ")
        self.btn_iptal.clicked.connect(self.geri_don)
        layout.addWidget(self.btn_iptal)

        self.cb_material.currentIndexChanged.connect(self.gruplari_yukle)
        self.verileri_tazele()

    def verileri_tazele(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.veri = json.load(f)
                self.cb_material.clear()
                for m_id, m_ad in self.veri.get("material", {}).items():
                    self.cb_material.addItem(f"[{m_id}] {m_ad}", m_id)

    def gruplari_yukle(self):
        self.cb_group.clear()
        m_id = self.cb_material.currentData()
        if m_id and m_id in self.veri.get("group", {}):
            for g_id, g_ad in self.veri["group"][m_id].items():
                if g_id != "last_group_id":
                    self.cb_group.addItem(f"[{g_id}] {g_ad}", g_id)

    def urun_turu_kaydet(self):
        m_id = self.cb_material.currentData()
        g_id = self.cb_group.currentData()
        u_ad = self.input_urun_ad.text().strip().capitalize()
        u_birim = self.input_birim.text().strip().capitalize() or "Adet"

        if not all([m_id, g_id, u_ad]):
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
            return

        # Hiyerarşik Kayıt Mantığı
        if "product" not in self.veri: self.veri["product"] = {}
        if m_id not in self.veri["product"]: self.veri["product"][m_id] = {}
        if g_id not in self.veri["product"][m_id]: self.veri["product"][m_id][g_id] = {"last_product_id": 0}

        yeni_u_id = str(self.veri["product"][m_id][g_id].get("last_product_id", 0) + 1)
        self.veri["product"][m_id][g_id][yeni_u_id] = {"ad": u_ad, "birim": u_birim}
        self.veri["product"][m_id][g_id]["last_product_id"] = int(yeni_u_id)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.veri, f, indent=4, ensure_ascii=False)

        QMessageBox.information(self, "Başarılı", f"'{u_ad}' ürünü {m_id}.{g_id}.{yeni_u_id} koduyla eklendi.")
        self.input_urun_ad.clear()

    def geri_don(self):
        if self.ana_pencere: self.ana_pencere.close()

# --- BOSS ---
pencere_tutucu = None
def boss():
    global pencere_tutucu
    app = QApplication.instance() or QApplication(sys.argv)
    pencere_tutucu = QMainWindow()
    pencere_tutucu.setCentralWidget(UrunTuruOlusturmaPaneli(pencere_tutucu))
    pencere_tutucu.setWindowTitle("Yeni Malzeme Türü Oluştur")
    pencere_tutucu.resize(600, 700)
    pencere_tutucu.show()
    if __name__ == "__main__": sys.exit(app.exec())
    return pencere_tutucu