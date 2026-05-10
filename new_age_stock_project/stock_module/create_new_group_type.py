import sys
import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QLineEdit, QMessageBox, QApplication, QMainWindow)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Dosya Yolu Ayarı
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)
DATA_FILE = os.path.join(project_root, "kategoriler.json")

class MalzemeOlusturmaPaneli(QWidget):
    def __init__(self, ana_pencere=None):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        baslik = QLabel("🏗️ YENİ MALZEME TÜRÜ TANIMLA")
        baslik.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        layout.addWidget(QLabel("Malzeme Adı (Örn: Gıda, Temizlik):"))
        self.input_ad = QLineEdit()
        self.input_ad.setPlaceholderText("Malzeme türünü yazın...")
        layout.addWidget(self.input_ad)

        self.btn_kaydet = QPushButton("✅ MALZEMEYİ KAYDET")
        self.btn_kaydet.setMinimumHeight(45)
        self.btn_kaydet.setStyleSheet("background-color: #2E86C1; color: white; font-weight: bold;")
        self.btn_kaydet.clicked.connect(self.malzeme_kaydet)
        layout.addWidget(self.btn_kaydet)

        self.btn_iptal = QPushButton("❌ İPTAL")
        self.btn_iptal.clicked.connect(self.geri_don)
        layout.addWidget(self.btn_iptal)

        layout.addStretch()

    def malzeme_kaydet(self):
        ad = self.input_ad.text().strip().capitalize()
        if not ad:
            QMessageBox.warning(self, "Hata", "Lütfen bir isim giriniz!")
            return

        # Veri Yükleme ve İşleme
        if not os.path.exists(DATA_FILE):
            veri = {"material": {}, "group": {}, "product": {}, "last_material_id": 0}
        else:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                veri = json.load(f)

        yeni_id = str(veri.get("last_material_id", 0) + 1)
        veri["material"][yeni_id] = ad
        veri["last_material_id"] = int(yeni_id)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(veri, f, indent=4, ensure_ascii=False)

        QMessageBox.information(self, "Başarılı", f"'{ad}' başarıyla {yeni_id} ID'si ile kaydedildi.")
        self.input_ad.clear()

    def geri_don(self):
        if self.ana_pencere: self.ana_pencere.close()

def boss():
    app = QApplication.instance() or QApplication(sys.argv)
    yeni_pencere = QMainWindow()
    yeni_pencere.setCentralWidget(MalzemeOlusturmaPaneli(yeni_pencere))
    yeni_pencere.setWindowTitle("Yeni Grup Türü Oluştur")
    yeni_pencere.resize(300, 250)
    yeni_pencere.show()
    return yeni_pencere