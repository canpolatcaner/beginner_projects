import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QMessageBox, QApplication, QMainWindow)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Orijinal dosya yolu ve import mantığına sadık kalıyoruz
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)

if project_root not in sys.path:
    sys.path.insert(0, project_root)


try:
    import stock_module.statistics_of_sales
    import stock_module.product_price_operations
except ImportError:
    import statistics_of_sales
    import product_price_operations

class UrunAkisEkrani(QWidget):
    def __init__(self, ana_pencere=None):
        super().__init__()
        self.ana_pencere = ana_pencere # Ana menüye dönüş için referans
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(60, 60, 60, 60)


        baslik = QLabel("╔═════════════════════════════╗\n║ ***ÜRÜN AKIŞ OTOMASYONU***  ║\n╚═════════════════════════════╝")
        baslik.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)


        self.btn_istatistik = self.buton_olustur("1 - Satış İstatistikleri", self.istatistik_git)
        self.btn_fiyat = self.buton_olustur("2 - Ürün Fiyat İşlemleri", self.fiyat_islem_git)
        self.btn_geri = self.buton_olustur("0 - Geri Dön", self.geri_don)

        layout.addWidget(self.btn_istatistik)
        layout.addWidget(self.btn_fiyat)
        layout.addStretch()
        layout.addWidget(self.btn_geri)

    def buton_olustur(self, metin, fonksiyon):
        btn = QPushButton(metin)
        btn.setFont(QFont("Consolas", 11))
        btn.setMinimumHeight(55)
        btn.clicked.connect(fonksiyon)
        return btn

    def istatistik_git(self):

        print("Satış İstatistikleri kısmına yönlendiriliyorsunuz...")
        try:
            stock_module.statistics_of_sales.boss()
        except:
            statistics_of_sales.boss()

    def fiyat_islem_git(self):

        print("Ürün Fiyat İşlemleri kısmına yönlendiriliyorsunuz...")
        try:
            stock_module.product_price_operations.boss()
        except:
            product_price_operations.boss()

    def geri_don(self):
        if self.ana_pencere:
           
            self.ana_pencere.pages.setCurrentIndex(0)

def boss():
    app = QApplication.instance() or QApplication(sys.argv)
    yeni_pencere = QMainWindow()
    yeni_pencere.setCentralWidget(UrunAkisEkrani(yeni_pencere))
    yeni_pencere.setWindowTitle("ÜRÜN AKIŞ OTOMASYONU")
    yeni_pencere.resize(500, 400)
    yeni_pencere.show()
    return yeni_pencere