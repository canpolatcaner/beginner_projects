import sys
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,QFileDialog, 
                             QLabel, QComboBox, QMessageBox, QTableWidget, QMessageBox, 
                             QTableWidgetItem, QHeaderView, QFrame, QApplication, QMainWindow)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt



# --- PROJE YOLLARI ---
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)
KATEGORI_FILE = os.path.join(project_root, "kategoriler.json")
SATIS_FILE = os.path.join(project_root, "satis_hareketleri.json")

class SatisAnalizPaneli(QWidget):
    def __init__(self, ana_pencere=None):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.verileri_yukle()
        self.init_ui()

    def verileri_yukle(self):
        def load_json(path, default):
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return default
        self.kategoriler = load_json(KATEGORI_FILE, {})
        self.satis_verisi = load_json(SATIS_FILE, {"satislar": []})["satislar"]

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # ÜST BAŞLIK VE FİLTRELEME ALANI
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #F8F9F9; border-radius: 10px; border: 1px solid #D5DBDB;")
        header_layout = QVBoxLayout(header_frame)

        baslik = QLabel("📊 SATIŞ PERFORMANS ANALİZİ")
        baslik.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(baslik)

        # FİLTRELER (Malzeme -> Grup -> Ürün)
        filter_layout = QHBoxLayout()
        self.cb_m = QComboBox(); self.cb_g = QComboBox(); self.cb_p = QComboBox()
        filter_layout.addWidget(QLabel("Malzeme:")); filter_layout.addWidget(self.cb_m)
        filter_layout.addWidget(QLabel("Grup:")); filter_layout.addWidget(self.cb_g)
        filter_layout.addWidget(QLabel("Ürün:")); filter_layout.addWidget(self.cb_p)
        header_layout.addLayout(filter_layout)
        
        layout.addWidget(header_frame)

        # TABLO ALANI
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["Tarih", "Ürün Adı", "Miktar", "Birim Fiyat", "Toplam"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tablo)

        # AKSİYON BUTONLARI (Excel ve Grafik)
        btn_layout = QHBoxLayout()
        
        self.btn_grafik = QPushButton("📉 GRAFİK OLUŞTUR")
        self.btn_grafik.setStyleSheet("background-color: #3498DB; color: white; font-weight: bold;")
        self.btn_grafik.setMinimumHeight(45)
        self.btn_grafik.clicked.connect(self.grafik_goster)

        self.btn_excel = QPushButton("Excel'e Aktar (Rapor)")
        self.btn_excel.setStyleSheet("background-color: #27AE60; color: white;")
        self.btn_excel.setMinimumHeight(45)
        self.btn_excel.clicked.connect(self.excel_aktar)

        btn_layout.addWidget(self.btn_grafik)
        btn_layout.addWidget(self.btn_excel)
        layout.addLayout(btn_layout)

        # Alt Navigasyon
        self.btn_geri = QPushButton("⬅️ ANA MENÜYE DÖN")
        self.btn_geri.clicked.connect(self.geri_don)
        layout.addWidget(self.btn_geri)

        # Eventler ve Başlangıç
        self.cb_m.currentIndexChanged.connect(self.gruplari_yukle)
        self.cb_g.currentIndexChanged.connect(self.urunleri_yukle)
        self.cb_p.currentIndexChanged.connect(self.tabloyu_doldur)
        self.malzemeleri_yukle()

    def malzemeleri_yukle(self):
        self.cb_m.clear()
        self.cb_m.addItem("TÜMÜ", None)
        for m_id, m_ad in self.kategoriler.get("material", {}).items():
            self.cb_m.addItem(m_ad, m_id)

    def gruplari_yukle(self):
        self.cb_g.clear()
        self.cb_g.addItem("TÜMÜ", None)
        m_id = self.cb_m.currentData()
        if m_id:
            for g_id, g_ad in self.kategoriler.get("group", {}).get(m_id, {}).items():
                if g_id != "last_group_id":
                    self.cb_g.addItem(g_ad, g_id)

    def urunleri_yukle(self):
        self.cb_p.clear()
        self.cb_p.addItem("TÜMÜ", None)
        m_id = self.cb_m.currentData()
        g_id = self.cb_g.currentData()
        if m_id and g_id:
            for p_id, p_info in self.kategoriler.get("product", {}).get(m_id, {}).get(g_id, {}).items():
                if p_id != "last_product_id":
                    self.cb_p.addItem(p_info["ad"], p_id)

    def veri_filtrele(self):
        if not self.satis_verisi:
            return pd.DataFrame()
            
        df = pd.DataFrame(self.satis_verisi)
        
        # --- ANAHTARLARI EŞLEŞTİRİYORUZ (RENAME) ---
        # Senin JSON'undaki isimleri kodun beklediği isimlere çeviriyoruz
        renamer = {
            'satis_zamani': 'tarih',
            'urun_ad': 'urun_adi',
            'toplam': 'toplam_tutar',
            'urun_id': 'koordinat' # urun_id içindeki 2.1.1 kısmını kullanacağız
        }
        df = df.rename(columns=renamer)
        
        m_id = self.cb_m.currentData()
        g_id = self.cb_g.currentData()
        p_id = self.cb_p.currentData()

        # Filtreleme mantığı (koordinat artık urun_id'den geliyor)
        if m_id:
            df = df[df['koordinat'].str.startswith(f"{m_id}.")]
        if g_id:
            # Örn: 2.1.1 içindeki ".1." kısmını kontrol eder
            df = df[df['koordinat'].str.contains(f".{g_id}.")]
        if p_id:
            # Örn: 2.1.1.SEK içindeki ".1." (urun türü) kısmını kontrol eder
            df = df[df['koordinat'].str.contains(f".{g_id}.{p_id}.")]
        
        return df

    def tabloyu_doldur(self):
        df = self.veri_filtrele()
        self.tablo.setRowCount(0)
        
        if df.empty:
            return

        for i, row in df.iterrows():
            pos = self.tablo.rowCount()
            self.tablo.insertRow(pos)
            
            # .get() ile güvenli okuma yapıyoruz (Eksik veri olsa da çökmez)
            tarih = str(row.get('tarih', ''))
            ad = str(row.get('urun_adi', ''))
            miktar = f"{row.get('miktar', 0)} {row.get('birim', 'Adet')}"
            fiyat = f"{row.get('satis_fiyati', 0)} TL"
            toplam = f"{row.get('toplam_tutar', 0)} TL"

            self.tablo.setItem(pos, 0, QTableWidgetItem(tarih))
            self.tablo.setItem(pos, 1, QTableWidgetItem(ad))
            self.tablo.setItem(pos, 2, QTableWidgetItem(miktar))
            self.tablo.setItem(pos, 3, QTableWidgetItem(fiyat))
            self.tablo.setItem(pos, 4, QTableWidgetItem(toplam))

    def grafik_goster(self):
        df = self.veri_filtrele()
        if df.empty:
            QMessageBox.warning(self, "Hata", "Gösterilecek veri bulunamadı!"); return

        # Tarihe göre grupla (Terminaldeki seaborn grafik mantığı)
        df['tarih'] = pd.to_datetime(df['tarih'])
        gunluk_satis = df.groupby('tarih')['toplam_tutar'].sum()

        plt.figure(figsize=(10, 5))
        gunluk_satis.plot(kind='line', marker='o', color='#E67E22')
        plt.title(f"Satış Trendi - {self.cb_m.currentText()}")
        plt.xlabel("Tarih"); plt.ylabel("Toplam Kazanç (TL)")
        plt.grid(True, linestyle='--')
        plt.show()

    def excel_aktar(self):
        df = self.veri_filtrele()
        if df.empty:
            QMessageBox.warning(self, "Hata", "Aktarılacak veri bulunamadı!")
            return
        
        # 1. Varsayılan bir dosya adı oluşturuyoruz
        tarih_etiketi = datetime.now().strftime('%Y%m%d_%H%M')
        varsayilan_ad = f"Satis_Raporu_{tarih_etiketi}.xlsx"
        
        # 2. İŞTE BURASI ÖNEMLİ: Kullanıcıya "Nereye Kaydedeyim?" diye soruyoruz
        dosya_yolu, _ = QFileDialog.getSaveFileName(
            self,
            "Raporu Kaydedilecek Yeri Seçin", # Pencere başlığı
            varsayilan_ad,                  # Varsayılan isim
            "Excel Dosyası (*.xlsx)"        # Filtre
        )

        # 3. Eğer kullanıcı iptal etmeyip bir yol seçtiyse
        if dosya_yolu:
            try:
                # Pandas ile seçilen yola kaydediyoruz
                df.to_excel(dosya_yolu, index=False)
                
                # Kayıttan sonra başarı mesajı veriyoruz
                QMessageBox.information(self, "Başarılı", f"Rapor başarıyla kaydedildi:\n{dosya_yolu}")
                        
                
                os.startfile(os.path.dirname(dosya_yolu)) 
            
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilirken bir hata oluştu: {e}")

    def geri_don(self):
        if self.ana_pencere: self.ana_pencere.close()

def boss():
    app = QApplication.instance() or QApplication(sys.argv)
    pencere = QMainWindow()
    pencere.setCentralWidget(SatisAnalizPaneli(pencere))
    pencere.setWindowTitle("Gelişmiş Analiz Sistemi")
    pencere.resize(900, 600)
    pencere.show()
    return pencere