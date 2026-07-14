import sys
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QFormLayout, QMessageBox, QFrame, QApplication, QMainWindow)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# --- YOL VE DOSYA AYARLARI ---
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

KATALOG_FILE = os.path.join(project_root, "urun_katalogu.json")
CURRENT_STOCK = os.path.join(project_root, "mevcut_stok.json")

class DepoGirisPaneli(QWidget):
    def __init__(self, ana_pencere=None):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.bulunan_urun_id = None
        self.bulunan_urun_ad = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # 1. BÖLÜM: BARKOD GİRİŞİ
        ust_layout = QHBoxLayout()
        self.barkod_input = QLineEdit()
        self.barkod_input.setPlaceholderText("Barkod okutun ve Enter'a basın...")
        self.barkod_input.setMinimumHeight(45)
        self.barkod_input.setFont(QFont("Consolas", 12))
        self.barkod_input.returnPressed.connect(self.urun_getir)
        
        btn_bul = QPushButton("BUL")
        btn_bul.setMinimumHeight(45)
        btn_bul.clicked.connect(self.urun_getir)
        
        ust_layout.addWidget(QLabel("🏷️ BARKOD:"))
        ust_layout.addWidget(self.barkod_input)
        ust_layout.addWidget(btn_bul)
        layout.addLayout(ust_layout)

        # 2. BÖLÜM: ÜRÜN BİLGİ KARTI
        self.bilgi_karti = QFrame()
        self.bilgi_karti.setFrameShape(QFrame.Shape.StyledPanel)
        self.bilgi_karti.setStyleSheet("background-color: #2C3E50; color: white; border-radius: 10px;")
        card_layout = QFormLayout(self.bilgi_karti)
        
        self.lbl_urun_adi = QLabel("---")
        self.lbl_eski_raf = QLabel("Veri bekleniyor...")
        
        card_layout.addRow("📦 Ürün:", self.lbl_urun_adi)
        card_layout.addRow("📍 Kayıtlı Raf:", self.lbl_eski_raf)
        layout.addWidget(self.bilgi_karti)

        # 3. BÖLÜM: GİRİŞ FORMU
        form_frame = QFrame()
        self.input_form = QFormLayout(form_frame)
        
        self.input_miktar = QLineEdit()
        self.input_maliyet = QLineEdit()
        self.input_raf = QLineEdit()
        self.input_stt = QLineEdit()
        self.input_stt.setPlaceholderText("GG.AA.YYYY")

        self.input_form.addRow("🔢 Miktar:", self.input_miktar)
        self.input_form.addRow("💰 Birim Maliyet (TL):", self.input_maliyet)
        self.input_form.addRow("🎯 Yerleştirilecek Raf:", self.input_raf)
        self.input_form.addRow("⌛ Son Tüketim (STT):", self.input_stt)
        
        layout.addWidget(form_frame)

        # 4. BÖLÜM: AKSİYON BUTONLARI
        btn_layout = QHBoxLayout()
        self.btn_kaydet = QPushButton("DEPOYA KAYDET")
        self.btn_kaydet.setMinimumHeight(50)
        self.btn_kaydet.setStyleSheet("background-color: #27AE60; color: white; font-weight: bold;")
        self.btn_kaydet.clicked.connect(self.stok_kaydet)

        self.btn_iptal = QPushButton("KAPAT")
        self.btn_iptal.clicked.connect(self.close_app)
        
        btn_layout.addWidget(self.btn_iptal)
        btn_layout.addWidget(self.btn_kaydet)
        layout.addLayout(btn_layout)

    def veri_yukle(self, dosya):
        if not os.path.exists(dosya): return {}
        with open(dosya, "r", encoding="utf-8") as f:
            return json.load(f)

    def urun_getir(self):
        barkod = self.barkod_input.text().strip()
        if not barkod: return

        katalog = self.veri_yukle(KATALOG_FILE)
        stok = self.veri_yukle(CURRENT_STOCK)
        
        self.bulunan_urun_id = None
        self.bulunan_urun_ad = None

        # 1. Katalogda Ürünü Bul
        for c_id, markalar in katalog.items():
            for marka, urunler in markalar.items():
                for sku, detay in urunler.items():
                    if detay.get('barkod') == barkod:
                        self.bulunan_urun_id = f"{c_id}.{marka}.{sku}"
                        self.bulunan_urun_ad = detay['tam_ad']
                        break
        
        if self.bulunan_urun_id:
            self.lbl_urun_adi.setText(self.bulunan_urun_ad)
            
            # 2. Stokta varsa "En Son Konulan Rafı" bul (Hafıza Özelliği)
            if self.bulunan_urun_id in stok:
                son_parti = stok[self.bulunan_urun_id]['partiler'][-1]
                eski_raf = son_parti.get('lokasyon', "Bilinmiyor")
                self.lbl_eski_raf.setText(eski_raf)
                self.input_raf.setText(eski_raf) # Otomatik doldur
            else:
                self.lbl_eski_raf.setText("Yeni Ürün (Raf Kaydı Yok)")
                self.input_raf.clear()
        else:
            QMessageBox.warning(self, "Hata", "Bu barkod katalogda kayıtlı değil!")

    def stok_kaydet(self):
        if not self.bulunan_urun_id:
            QMessageBox.warning(self, "Hata", "Önce geçerli bir ürün okutun!"); return

        try:
            miktar = float(self.input_miktar.text().replace(",", "."))
            maliyet = float(self.input_maliyet.text().replace(",", "."))
            raf = self.input_raf.text().strip()
            stt = self.input_stt.text().strip()
        except ValueError:
            QMessageBox.critical(self, "Hata", "Lütfen miktar ve maliyet alanlarını sayısal girin!"); return

        if not raf or not stt:
            QMessageBox.warning(self, "Hata", "Raf ve STT alanları boş bırakılamaz!"); return

        # Onay Al
        onay = QMessageBox.question(self, "Onay", f"{self.bulunan_urun_ad} için {miktar} adet girişi onaylıyor musunuz?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if onay == QMessageBox.StandardButton.Yes:
            stok = self.veri_yukle(CURRENT_STOCK)
            
            # Batch ID Üretimi (B-YılAyGünSaatDakikaSaniye)
            batch_id = "B-" + datetime.now().strftime("%Y%m%d%H%M%S")
            
            yeni_parti = {
                "batch_id": batch_id,
                "miktar_mevcut": miktar,
                "maliyet": maliyet,
                "lokasyon": raf,
                "stt": stt,
                "giris_zamani": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            if self.bulunan_urun_id not in stok:
                stok[self.bulunan_urun_id] = {"urun_ad": self.bulunan_urun_ad, "partiler": []}
            
            stok[self.bulunan_urun_id]["partiler"].append(yeni_parti)

            with open(CURRENT_STOCK, "w", encoding="utf-8") as f:
                json.dump(stok, f, indent=4, ensure_ascii=False)

            QMessageBox.information(self, "Başarılı", f"Kayıt Tamamlandı!\nBatch ID: {batch_id}")
            self.temizle()

    def temizle(self):
        self.barkod_input.clear()
        self.input_miktar.clear()
        self.input_maliyet.clear()
        self.input_stt.clear()
        self.lbl_urun_adi.setText("---")
        self.lbl_eski_raf.setText("---")

    def close_app(self):
        if self.ana_pencere: self.ana_pencere.close()
        else: self.close()

# --- BOSS ---
pencere_tutucu = None
def boss():
    global pencere_tutucu
    app = QApplication.instance() or QApplication(sys.argv)
    pencere_tutucu = QMainWindow()
    pencere_tutucu.setCentralWidget(DepoGirisPaneli(pencere_tutucu))
    pencere_tutucu.setWindowTitle("Depo Stok Giriş Sistemi")
    pencere_tutucu.resize(450, 600)
    pencere_tutucu.show()
    if __name__ == "__main__": sys.exit(app.exec())
    return pencere_tutucu