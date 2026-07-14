import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QApplication, QMainWindow, QFrame)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Diğer modülleri import ediyoruz (Dosya isimlerinle eşleşmeli)
import stock_module.create_new_material_type
import stock_module.create_new_group_type
import stock_module.create_new_product_type
import stock_module.stock_delete_operations_management
# import stock_module.stock_delete_operations_management # Henüz PyQt değilse hata verebilir, dikkat!

class MalzemeGrupYonetimPaneli(QWidget):
    def __init__(self, ana_pencere=None):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Başlık
        baslik = QLabel("🏗️ MALZEME VE GRUP YÖNETİMİ")
        baslik.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        # Butonlar
        self.btn_mat = QPushButton("1- Yeni Malzeme Türü Oluştur")
        self.btn_grp = QPushButton("2- Yeni Grup Türü Oluştur")
        self.btn_prd = QPushButton("3- Yeni Ürün Türü Oluştur")
        self.btn_sil = QPushButton("4- Silme İşlemleri (!!!)")
        
        # Buton Tasarımları
        self.btn_sil.setStyleSheet("background-color: #C0392B; color: white; font-weight: bold;")
        
        # --- KRİTİK NOKTA: Butonları Fonksiyonlara Bağlıyoruz ---
        self.btn_mat.clicked.connect(self.git_malzeme_olustur)
        self.btn_grp.clicked.connect(self.git_grup_olustur)
        self.btn_prd.clicked.connect(self.git_urun_turu_olustur)
        self.btn_sil.clicked.connect(self.git_silme_islemleri)

        # Butonları Layout'a Ekle
        for btn in [self.btn_mat, self.btn_grp, self.btn_prd, self.btn_sil]:
            btn.setMinimumHeight(45)
            layout.addWidget(btn)
        
        self.btn_geri = QPushButton("⬅️ ANA MENÜYE DÖN")
        self.btn_geri.setMinimumHeight(40)
        self.btn_geri.clicked.connect(self.geri_don)

        layout.addStretch()
        layout.addWidget(self.btn_geri)

    # --- YÖNLENDİRME FONKSİYONLARI ---
    def git_malzeme_olustur(self):
        # Diğer dosyadaki boss() fonksiyonunu çağırıp dönen pencereyi referans alıyoruz
        self.ek_pencere = stock_module.create_new_material_type.boss()

    def git_grup_olustur(self):
        self.ek_pencere = stock_module.create_new_group_type.boss()

    def git_urun_turu_olustur(self):
        self.ek_pencere = stock_module.create_new_product_type.boss()

    def git_silme_islemleri(self):
        
        self.ek_pencere = stock_module.stock_delete_operations_management.boss()
        print("Silme işlemleri tetiklendi...")

    def geri_don(self):
        if self.ana_pencere:
            self.ana_pencere.close()

def boss():
    app = QApplication.instance() or QApplication(sys.argv)
    pencere = QMainWindow()
    pencere.setCentralWidget(MalzemeGrupYonetimPaneli(pencere))
    pencere.setWindowTitle("Malzeme & Grup Yönetimi")
    pencere.resize(400, 500)
    pencere.show()
    return pencere