import sys
import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QMessageBox, QFrame, 
                             QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# --- YOL VE DOSYA AYARLARI ---
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)
DATA_FILE = os.path.join(project_root, "kategoriler.json")

class SilmeIslemleriPaneli(QWidget):
    def __init__(self, ana_pencere=None):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.veri = self.verileri_yukle()
        self.init_ui()

    def verileri_yukle(self):
        if not os.path.exists(DATA_FILE):
            return {"material": {}, "group": {}, "product": {}, "last_material_id": 0}
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def verileri_kaydet(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.veri, f, indent=4, ensure_ascii=False)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Başlık
        baslik = QLabel("⚠️ KATEGORİ VE HİYERARŞİ SİLME YÖNETİMİ")
        baslik.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #E74C3C;")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        # --- BÖLÜM 1: MALZEME TÜRÜ SİL ---
        m_frame = QFrame()
        m_frame.setFrameShape(QFrame.Shape.StyledPanel)
        m_layout = QVBoxLayout(m_frame)
        m_layout.addWidget(QLabel("<b>1. Malzeme Türü Sil</b> (Tüm alt gruplar silinir!)"))
        
        h_m = QHBoxLayout()
        self.cb_mat = QComboBox()
        self.btn_mat_sil = QPushButton("Malzemeyi Sil")
        self.btn_mat_sil.setStyleSheet("background-color: #C0392B; color: white;")
        self.btn_mat_sil.clicked.connect(self.malzeme_sil)
        h_m.addWidget(self.cb_mat, 4)
        h_m.addWidget(self.btn_mat_sil, 1)
        m_layout.addLayout(h_m)
        layout.addWidget(m_frame)

        # --- BÖLÜM 2: GRUP TÜRÜ SİL ---
        g_frame = QFrame()
        g_frame.setFrameShape(QFrame.Shape.StyledPanel)
        g_layout = QVBoxLayout(g_frame)
        g_layout.addWidget(QLabel("<b>2. Grup Türü Sil</b> (Gruba bağlı ürünler silinir!)"))
        
        h_g = QHBoxLayout()
        self.cb_mat_for_group = QComboBox()
        self.cb_group = QComboBox()
        self.btn_group_sil = QPushButton("Grubu Sil")
        self.btn_group_sil.setStyleSheet("background-color: #C0392B; color: white;")
        self.btn_group_sil.clicked.connect(self.grup_sil)
        
        h_g.addWidget(self.cb_mat_for_group, 2)
        h_g.addWidget(self.cb_group, 2)
        h_g.addWidget(self.btn_group_sil, 1)
        g_layout.addLayout(h_g)
        layout.addWidget(g_frame)

        # ComboBox Bağlantıları
        self.cb_mat_for_group.currentIndexChanged.connect(self.gruplari_guncelle)

        # Alt Menü Butonları
        self.btn_geri = QPushButton("⬅️ GERİ DÖN")
        self.btn_geri.setMinimumHeight(40)
        self.btn_geri.clicked.connect(self.geri_don)
        layout.addStretch()
        layout.addWidget(self.btn_geri)

        self.arayuz_tazele()

    def arayuz_tazele(self):
        self.veri = self.verileri_yukle()
        # Malzeme listelerini doldur
        self.cb_mat.clear()
        self.cb_mat_for_group.clear()
        for m_id, m_ad in self.veri.get("material", {}).items():
            self.cb_mat.addItem(f"[{m_id}] {m_ad}", m_id)
            self.cb_mat_for_group.addItem(f"[{m_id}] {m_ad}", m_id)

    def gruplari_guncelle(self):
        self.cb_group.clear()
        m_id = self.cb_mat_for_group.currentData()
        if m_id and m_id in self.veri.get("group", {}):
            for g_id, g_ad in self.veri["group"][m_id].items():
                if g_id != "last_group_id":
                    self.cb_group.addItem(f"[{g_id}] {g_ad}", g_id)

    def malzeme_sil(self):
        m_id = self.cb_mat.currentData()
        m_ad = self.cb_mat.currentText()
        if not m_id: return

        onay = QMessageBox.critical(self, "KRİTİK ONAY", 
            f"'{m_ad}' Malzeme Türü silindiğinde buna bağlı TÜM GRUPLAR ve ÜRÜNLER yok olacaktır.\n\nEmin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if onay == QMessageBox.StandardButton.Yes:
            self.veri["material"].pop(m_id)
            self.veri["group"].pop(m_id, None)
            self.veri["product"].pop(m_id, None)
            self.verileri_kaydet()
            QMessageBox.information(self, "Silindi", "Malzeme ve bağlı tüm hiyerarşi temizlendi.")
            self.arayuz_tazele()

    def grup_sil(self):
        m_id = self.cb_mat_for_group.currentData()
        g_id = self.cb_group.currentData()
        g_ad = self.cb_group.currentText()
        if not g_id: return

        onay = QMessageBox.warning(self, "Grup Silme Onayı", 
            f"'{g_ad}' Grubu ve bu gruba tanımlı tüm ürün türleri silinecek. Onaylıyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if onay == QMessageBox.StandardButton.Yes:
            self.veri["group"][m_id].pop(g_id)
            if m_id in self.veri["product"] and g_id in self.veri["product"][m_id]:
                self.veri["product"][m_id].pop(g_id)
            self.verileri_kaydet()
            QMessageBox.information(self, "Silindi", "Grup ve bağlı ürünler silindi.")
            self.arayuz_tazele()

    def geri_don(self):
        if self.ana_pencere: self.ana_pencere.close()

def boss():
    app = QApplication.instance() or QApplication(sys.argv)
    yeni_pencere = QMainWindow()
    yeni_pencere.setCentralWidget(SilmeIslemleriPaneli(yeni_pencere))
    yeni_pencere.setWindowTitle("Hiyerarşi Silme Yönetimi")
    yeni_pencere.resize(500, 400)
    yeni_pencere.show()
    return yeni_pencere