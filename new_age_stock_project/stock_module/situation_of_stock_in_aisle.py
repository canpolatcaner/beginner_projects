import sys
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QFrame, QApplication, QMainWindow, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# --- YOL AYARLARI ---
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Dosya Yolları
CURRENT_STOCK = os.path.join(project_root, "mevcut_stok.json") 
REYON_STOCK = os.path.join(project_root, "reyon_stok.json")

class ReyonSevkPaneli(QWidget):
    def __init__(self, ana_pencere=None):
        super().__init__()
        self.ana_pencere = ana_pencere
        # Veriyi işlerken kullanacağımız geçici referanslar
        self.bulunan_depo_parti = None
        self.bulunan_urun_anahtari = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 1. BÖLÜM: BATCH ID İLE SORGULAMA
        arama_layout = QHBoxLayout()
        self.batch_input = QLineEdit()
        self.batch_input.setPlaceholderText("Batch ID Giriniz:")
        self.batch_input.setMinimumHeight(40)
        self.btn_sorgula = QPushButton("Parti Sorgula")
        self.btn_sorgula.clicked.connect(self.batch_sorgula)
        arama_layout.addWidget(self.batch_input)
        arama_layout.addWidget(self.btn_sorgula)
        layout.addLayout(arama_layout)

        # 2. BÖLÜM: DEPO VE REYON BİLGİ KARTI
        self.bilgi_karti = QFrame()
        self.bilgi_karti.setFrameShape(QFrame.Shape.StyledPanel)
        self.bilgi_karti.setStyleSheet("background-color: #2c3e50; color: white; border-radius: 10px;")
        info_layout = QVBoxLayout(self.bilgi_karti)

        self.lbl_urun_ad = QLabel("Ürün: -")
        self.lbl_depo_bilgi = QLabel("📦 DEPO DURUMU: -")
        self.lbl_reyon_bilgi = QLabel("🏪 REYON DURUMU: -")
        self.lbl_stt = QLabel("⏳ STT: -")
        self.lbl_maliyet = QLabel("💰 Maliyet: -")

        for lbl in [self.lbl_urun_ad, self.lbl_depo_bilgi, self.lbl_reyon_bilgi, self.lbl_stt, self.lbl_maliyet]:
            lbl.setFont(QFont("Consolas", 10))
            info_layout.addWidget(lbl)
        
        layout.addWidget(self.bilgi_karti)

        # 3. BÖLÜM: SEVK İŞLEMİ
        form_layout = QVBoxLayout()
        self.input_miktar = QLineEdit()
        self.input_miktar.setPlaceholderText("Sevk Edilecek Miktar")
        self.input_fiyat = QLineEdit()
        self.input_fiyat.setPlaceholderText("Reyon Satış Fiyatı (TL)")
        
        form_layout.addWidget(QLabel("Miktar:"))
        form_layout.addWidget(self.input_miktar)
        form_layout.addWidget(QLabel("Satış Fiyatı:"))
        form_layout.addWidget(self.input_fiyat)
        layout.addLayout(form_layout)

        # 4. BÖLÜM: ONAY
        self.btn_onayla = QPushButton("SEVKİ TAMAMLA")
        self.btn_onayla.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; height: 40px;")
        self.btn_onayla.clicked.connect(self.sevk_et)
        layout.addWidget(self.btn_onayla)

    def veri_yukle(self, dosya):
        if not os.path.exists(dosya): return {}
        with open(dosya, "r", encoding="utf-8") as f:
            return json.load(f)

    def batch_sorgula(self):
        target_batch = self.batch_input.text().strip()
        if not target_batch: return

        depo = self.veri_yukle(CURRENT_STOCK)
        reyon = self.veri_yukle(REYON_STOCK)
        
        found = False
        # Depoda Ara
        for key, urun in depo.items():
            for parti in urun.get("partiler", []):
                if parti["batch_id"] == target_batch:
                    self.bulunan_urun_anahtari = key
                    self.bulunan_depo_parti = parti
                    self.lbl_urun_ad.setText(f"Ürün: {urun['urun_ad']}")
                    self.lbl_depo_bilgi.setText(f"📦 DEPO: {parti['miktar_mevcut']} Adet (Raf: {parti['lokasyon']})")
                    self.lbl_stt.setText(f"⏳ STT: {parti['stt']}")
                    self.lbl_maliyet.setText(f"💰 Maliyet: {parti['maliyet']} TL")
                    found = True
                    break
        
        # Reyonda Ara
        reyon_miktar = 0
        for r_key, r_urun in reyon.items():
            # Reyon dosyanda "partiler" veya senin örneğindeki gibi "reyon_partileri" olabilir
            parti_listesi = r_urun.get("partiler", []) or r_urun.get("reyon_partileri", [])
            for r_parti in parti_listesi:
                if r_parti["batch_id"] == target_batch:
                    reyon_miktar += r_parti["miktar_mevcut"] if "miktar_mevcut" in r_parti else r_parti.get("miktar", 0)
        
        self.lbl_reyon_bilgi.setText(f"🏪 REYON: {reyon_miktar} Adet")

        if not found:
            QMessageBox.warning(self, "Hata", "Batch ID Depo kayıtlarında bulunamadı!")

    def sevk_et(self):
        if not self.bulunan_depo_parti: return

        try:
            miktar = float(self.input_miktar.text().replace(",", "."))
            fiyat = float(self.input_fiyat.text().replace(",", "."))
        except:
            QMessageBox.critical(self, "Hata", "Lütfen geçerli miktar ve fiyat girin!"); return

        if miktar > self.bulunan_depo_parti["miktar_mevcut"]:
            QMessageBox.warning(self, "Yetersiz Stok", "Depodaki mevcut miktardan fazlasını sevk edemezsiniz!"); return

        # Dosyaları Güncelle
        depo = self.veri_yukle(CURRENT_STOCK)
        reyon = self.veri_yukle(REYON_STOCK)

        # 1. Depodan Düş
        for p in depo[self.bulunan_urun_anahtari]["partiler"]:
            if p["batch_id"] == self.bulunan_depo_parti["batch_id"]:
                p["miktar_mevcut"] -= miktar
                break

        # 2. Reyona Ekle
        if self.bulunan_urun_anahtari not in reyon:
            reyon[self.bulunan_urun_anahtari] = {"urun_ad": depo[self.bulunan_urun_anahtari]["urun_ad"], "partiler": []}
        
        reyon[self.bulunan_urun_anahtari]["partiler"].append({
            "batch_id": self.bulunan_depo_parti["batch_id"],
            "miktar_mevcut": miktar,
            "maliyet": self.bulunan_depo_parti["maliyet"],
            "satis_fiyati": fiyat,
            "reyona_giris_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stt": self.bulunan_depo_parti["stt"]
        })

        # Kaydet
        with open(CURRENT_STOCK, "w", encoding="utf-8") as f: json.dump(depo, f, indent=4, ensure_ascii=False)
        with open(REYON_STOCK, "w", encoding="utf-8") as f: json.dump(reyon, f, indent=4, ensure_ascii=False)

        QMessageBox.information(self, "Başarılı", "Sevk işlemi tamamlandı!")
        self.batch_sorgula() # Bilgileri tazele

# --- BOSS ---
pencere_tutucu = None
def boss():
    global pencere_tutucu
    app = QApplication.instance() or QApplication(sys.argv)
    pencere_tutucu = QMainWindow()
    pencere_tutucu.setCentralWidget(ReyonSevkPaneli(pencere_tutucu))
    pencere_tutucu.setWindowTitle("Batch ID Stok Yönetimi")
    pencere_tutucu.show()
    if __name__ == "__main__": sys.exit(app.exec())
    return pencere_tutucu