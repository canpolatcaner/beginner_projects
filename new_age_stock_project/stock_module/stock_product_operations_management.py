# stock_product_operations_management.py

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from . import stock_add_product  
from . import stock_del_product

class UrunIslemleriAnaMenu(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        layout = QVBoxLayout(self)
        
        lbl = QLabel("📦 ÜRÜN İŞLEMLERİ YÖNETİMİ")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(lbl)

        btn_ekle = QPushButton("🆕 Yeni Ürün Ekle")
        btn_ekle.clicked.connect(self.ac_urun_ekle)
        layout.addWidget(btn_ekle)

        btn_sil = QPushButton("🗑️ Ürün Sil / Arşivle")
        btn_sil.clicked.connect(self.ac_urun_sil)
        layout.addWidget(btn_sil)

        btn_geri = QPushButton("⬅️ Ana Menüye Dön")
        btn_geri.clicked.connect(self.ana_pencere.close)
        layout.addWidget(btn_geri)

    def ac_urun_ekle(self):
        # stock_add_product içindeki boss() fonksiyonunu çağırıyoruz
        self.ekle_pencere = stock_add_product.boss() 

    def ac_urun_sil(self):
        # stock_del_product içindeki boss() fonksiyonunu çağırıyoruz
        self.sil_pencere = stock_del_product.boss()

def boss():
    """Terminaldeki input'u tamamen devre dışı bırakan yeni giriş kapısı"""
    app = QApplication.instance() or QApplication(sys.argv)
    
    yeni_pencere = QMainWindow()
    panel = UrunIslemleriAnaMenu(yeni_pencere)
    yeni_pencere.setCentralWidget(panel)
    yeni_pencere.setWindowTitle("Ürün Yönetim Merkezi")
    yeni_pencere.resize(300, 250)
    yeni_pencere.show()
    
  
    return yeni_pencere