import os
import sys


current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)

if project_root not in sys.path:
    sys.path.insert(0, project_root)


try:
    import stock_module.situation_of_stock_in_aisle
    import stock_module.situation_of_stock_in_depo
except ImportError:
    # Eğer üst klasör eklenemezse doğrudan isimle çağırmayı dener
    import situation_of_stock_in_aisle
    import situation_of_stock_in_depo

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QApplication, QMainWindow)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


import stock_module.situation_of_stock_in_aisle 
import stock_module.situation_of_stock_in_depo

class StokTakipEkrani(QWidget): # QWidget olarak tasarlıyoruz ki Ana Menüye gömülebilsin
    def __init__(self, ana_pencere=None):
        super().__init__()
        self.ana_pencere = ana_pencere # Geri dönmek gerekirse ana pencere referansı
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(50, 50, 50, 50)

        # Başlık
        baslik = QLabel("╔═════════════════════════════╗\n║  ***STOK TAKİP İŞLEMLERİ*** ║\n╚═════════════════════════════╝")
        baslik.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        # Seçenek Butonları
        self.btn_reyon = self.buton_olustur("1 - Reyona Sevk İşlemleri", self.reyon_islem)
        self.btn_depo = self.buton_olustur("2 - Depo Stok Giriş", self.depo_islem)
        self.btn_geri = self.buton_olustur("0 - Geri Dön", self.geri_don)

        layout.addWidget(self.btn_reyon)
        layout.addWidget(self.btn_depo)
        layout.addStretch()
        layout.addWidget(self.btn_geri)

    def buton_olustur(self, metin, fonksiyon):
        btn = QPushButton(metin)
        btn.setFont(QFont("Consolas", 11))
        btn.setMinimumHeight(50)
        btn.clicked.connect(fonksiyon)
        return btn

    def reyon_islem(self):
        print("Reyon Stok Durumu kısmına yönlendiriliyorsunuz...")
        stock_module.situation_of_stock_in_aisle.boss() # Geçici olarak eski boss çalışır

    def depo_islem(self):
        print("Depo Stok Giriş kısmına yönlendiriliyorsunuz...")
        stock_module.situation_of_stock_in_depo.boss() # Geçici olarak eski boss çalışır

    def geri_don(self):
        if self.ana_pencere:
            self.ana_pencere.pages.setCurrentIndex(0) # Ana menüye (ilk sayfaya) döner

# Global bir değişken kullanarak pencerenin hafızada kalmasını sağlıyoruz
pencere_tutucu = None 

def boss():
    global pencere_tutucu
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    pencere_tutucu = QMainWindow()
    ekran = StokTakipEkrani() 
    pencere_tutucu.setCentralWidget(ekran)
    pencere_tutucu.setWindowTitle("STOK TAKİP İŞLEMLERİ")
    pencere_tutucu.show()
    
    if __name__ == "__main__":
        sys.exit(app.exec())
    return pencere_tutucu