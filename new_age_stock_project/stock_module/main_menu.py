import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Mevcut modül yollarını ekleme mantığını koruyoruz
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(current_path)
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Modüllerini içe aktarıyoruz
import stock_module.stock_product_operations_management
import stock_module.stock_flow_product_automation  
import stock_module.stock_material_and_group_management
import stock_module.stock_keeping

class StokAnaMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("STOK TAKİP PROGRAMI")
        self.setFixedSize(400, 500) # Terminaldeki o kutu formunu koruyalım

        # Ana Widget ve Layout
        merkezi_widget = QWidget()
        self.setCentralWidget(merkezi_widget)
        layout = QVBoxLayout(merkezi_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Başlık
        baslik = QLabel("*** STOK TAKİP PROGRAMI ***")
        baslik.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        # Butonlar (Terminaldeki seçeneklerin karşılığı)
        self.btn_stok = self.buton_olustur("1 - Stok Takip İşlemleri", self.stok_git)
        self.btn_urun = self.buton_olustur("2 - Ürün İşlemleri", self.urun_git)
        self.btn_akis = self.buton_olustur("3 - Ürün Akış Otomasyonu", self.akis_git)
        self.btn_grup = self.buton_olustur("4 - Malzeme ve Grup Yönetimi", self.grup_git)
        self.btn_cikis = self.buton_olustur("0 - Çıkış", self.close)

        # Butonları Layout'a ekle
        layout.addWidget(self.btn_stok)
        layout.addWidget(self.btn_urun)
        layout.addWidget(self.btn_akis)
        layout.addWidget(self.btn_grup)
        layout.addStretch() # Çıkış butonunu en alta iter
        layout.addWidget(self.btn_cikis)

    def buton_olustur(self, metin, fonksiyon):
        btn = QPushButton(metin)
        btn.setFont(QFont("Consolas", 11))
        btn.setMinimumHeight(45)
        btn.clicked.connect(fonksiyon)
        return btn

    # Fonksiyon Tetikleyiciler
    def stok_git(self):
        # Terminaldeki boss() fonksiyonunu çağırıyoruz
        # Not: GUI geçişinde boss() fonksiyonlarının içeriğini de zamanla PyQt'ye çevireceğiz
        stock_module.stock_keeping.boss()

    def urun_git(self):
        stock_module.stock_product_operations_management.boss()

    def akis_git(self):
        stock_module.stock_flow_product_automation.boss()

    def grup_git(self):
        stock_module.stock_material_and_group_management.boss()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = StokAnaMenu()
    pencere.show()
    sys.exit(app.exec())