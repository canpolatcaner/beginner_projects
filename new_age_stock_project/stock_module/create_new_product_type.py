import sys
import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QComboBox, QMessageBox, QFrame, 
                             QApplication, QMainWindow)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# --- YOL VE DOSYA AYARLARI ---
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)
DATA_FILE = os.path.join(project_root, "kategoriler.json")

class UrunTuruOlusturmaPaneli(QWidget):
    def __init__(self, ana_pencere=None):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.veri = self.verileri_yukle()
        self.init_ui()

    def verileri_yukle(self):
        if not os.path.exists(DATA_FILE):
            return {"material": {}, "group": {}, "product": {}}
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def verileri_kaydet(self, veri):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(veri, f, indent=4, ensure_ascii=False)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Başlık
        baslik = QLabel("📦 YENİ ÜRÜN TÜRÜ TANIMLAMA")
        baslik.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        # 1. ADIM: HİYERARŞİ SEÇİMİ
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.Shape.StyledPanel)
        form_layout = QVBoxLayout(form_frame)

        form_layout.addWidget(QLabel("<b>1. Üst Malzeme Seçin:</b>"))
        self.cb_material = QComboBox()
        form_layout.addWidget(self.cb_material)

        form_layout.addWidget(QLabel("<b>2. Bağlı Olduğu Grubu Seçin:</b>"))
        self.cb_group = QComboBox()
        form_layout.addWidget(self.cb_group)

        layout.addWidget(form_frame)

        # 2. ADIM: ÜRÜN TANIMI
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)

        input_layout.addWidget(QLabel("<b>3. Yeni Ürün Türü Adı:</b>"))
        self.input_urun_ad = QLineEdit()
        self.input_urun_ad.setPlaceholderText("Örn: Süt, Zeytinyağı, Sabun...")
        input_layout.addWidget(self.input_urun_ad)

        input_layout.addWidget(QLabel("<b>4. Ölçü Birimi:</b>"))
        self.cb_birim = QComboBox()
        self.cb_birim.addItems(["Adet", "Kilogram", "Litre", "Metre", "Koli"])
        input_layout.addWidget(self.cb_birim)

        layout.addWidget(input_frame)

        # 3. ADIM: AKSİYON BUTONLARI
        btn_layout = QHBoxLayout()
        
        self.btn_geri = QPushButton("⬅️ GERİ DÖN")
        self.btn_geri.setMinimumHeight(40)
        self.btn_geri.clicked.connect(self.geri_don)

        self.btn_kaydet = QPushButton("✅ ÜRÜN TÜRÜNÜ EKLE")
        self.btn_kaydet.setMinimumHeight(40)
        self.btn_kaydet.setStyleSheet("background-color: #8E44AD; color: white; font-weight: bold;")
        self.btn_kaydet.clicked.connect(self.urun_turu_kaydet)

        btn_layout.addWidget(self.btn_geri)
        btn_layout.addWidget(self.btn_kaydet)
        layout.addLayout(btn_layout)

        # Eventler
        self.cb_material.currentIndexChanged.connect(self.gruplari_yukle)
        
        # İlk yükleme
        self.malzemeleri_yukle()

    def malzemeleri_yukle(self):
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
        birim = self.cb_birim.currentText()

        if not (m_id and g_id and u_ad):
            QMessageBox.warning(self, "Eksik Veri", "Lütfen tüm seçimleri yapın ve ürün adını girin!"); return

        # Veri Yapısı Kontrolü ve ID Üretimi
        if "product" not in self.veri: self.veri["product"] = {}
        if m_id not in self.veri["product"]: self.veri["product"][m_id] = {}
        if g_id not in self.veri["product"][m_id]:
            self.veri["product"][m_id][g_id] = {"last_product_id": 0}

        last_id = self.veri["product"][m_id][g_id].get("last_product_id", 0)
        yeni_id = str(last_id + 1)

        # Mükerrer Kontrolü (Aynı isimde ürün türü var mı?)
        for p_id, p_info in self.veri["product"][m_id][g_id].items():
            if p_id != "last_product_id" and p_info['ad'].lower() == u_ad.lower():
                QMessageBox.warning(self, "Hata", "Bu ürün türü zaten mevcut!"); return

        # Kayıt
        self.veri["product"][m_id][g_id][yeni_id] = {"ad": u_ad, "birim": birim}
        self.veri["product"][m_id][g_id]["last_product_id"] = int(yeni_id)

        self.verileri_kaydet(self.veri)
        QMessageBox.information(self, "Başarılı", f"'{u_ad}' ürün türü {m_id}.{g_id}.{yeni_id} koduyla sisteme işlendi.")
        self.input_urun_ad.clear()

    def geri_don(self):
        if self.ana_pencere: self.ana_pencere.close()

def boss():
    app = QApplication.instance() or QApplication(sys.argv)
    yeni_pencere = QMainWindow()
    yeni_pencere.setCentralWidget(UrunTuruOlusturmaPaneli(yeni_pencere))
    yeni_pencere.setWindowTitle("Yeni Ürün Türü Oluştur")
    yeni_pencere.resize(400, 450)
    yeni_pencere.show()
    return yeni_pencere