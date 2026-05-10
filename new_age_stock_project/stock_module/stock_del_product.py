import sys
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QMessageBox, QFrame, 
                             QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

# --- YOL VE DOSYA AYARLARI ---
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

KATEGORI_FILE = os.path.join(project_root, "kategoriler.json")
KATALOG_FILE = os.path.join(project_root, "urun_katalogu.json")
ARSIV_FILE = os.path.join(project_root, "urun_arsivi_log.json")

class UrunSilmePaneli(QWidget):
    def __init__(self, ana_pencere=None):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.kategoriler = self.veri_yukle(KATEGORI_FILE)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Başlık (Kritik İşlem Uyarısı)
        baslik = QLabel("⚠️ ÜRÜN SİLME VE ARŞİVLEME")
        baslik.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #C0392B;") # Tehlike rengi: Kırmızı
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        # 1. BÖLÜM: NAVİGASYON (Seçim Alanları)
        nav_frame = QFrame()
        nav_layout = QVBoxLayout(nav_frame)
        
        self.cb_malzeme = QComboBox()
        self.cb_grup = QComboBox()
        self.cb_urun_turu = QComboBox()
        self.cb_marka = QComboBox()

        nav_layout.addWidget(QLabel("Malzeme Türü:"))
        nav_layout.addWidget(self.cb_malzeme)
        nav_layout.addWidget(QLabel("Ürün Grubu:"))
        nav_layout.addWidget(self.cb_grup)
        nav_layout.addWidget(QLabel("Ürün Türü:"))
        nav_layout.addWidget(self.cb_urun_turu)
        nav_layout.addWidget(QLabel("Marka:"))
        nav_layout.addWidget(self.cb_marka)
        
        layout.addWidget(nav_frame)

        # Bağlantılar
        self.cb_malzeme.currentIndexChanged.connect(self.gruplari_yukle)
        self.cb_grup.currentIndexChanged.connect(self.turleri_yukle)
        self.cb_urun_turu.currentIndexChanged.connect(self.markalari_yukle)
        self.cb_marka.currentIndexChanged.connect(self.urunleri_listele)

        # 2. BÖLÜM: ÜRÜN LİSTESİ (Tablo)
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(3)
        self.tablo.setHorizontalHeaderLabels(["Ürün Adı", "Barkod", "Birim"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.tablo)

        # 3. BÖLÜM: AKSİYON BUTONLARI
        btn_layout = QHBoxLayout()
        
        self.btn_geri = QPushButton("⬅️ GERİ DÖN")
        self.btn_geri.setMinimumHeight(40)
        self.btn_geri.clicked.connect(self.geri_don)

        self.btn_sil = QPushButton("🗑️ SEÇİLİ ÜRÜNÜ SİL")
        self.btn_sil.setMinimumHeight(40)
        self.btn_sil.setStyleSheet("background-color: #E74C3C; color: white; font-weight: bold;")
        self.btn_sil.clicked.connect(self.urun_sil)

        btn_layout.addWidget(self.btn_geri)
        btn_layout.addWidget(self.btn_sil)
        layout.addLayout(btn_layout)

        # İlk veriyi yükle
        self.malzemeleri_yukle()

    # --- VERİ YÖNETİMİ ---
    def veri_yukle(self, dosya):
        if not os.path.exists(dosya): return {}
        with open(dosya, "r", encoding="utf-8") as f:
            return json.load(f)

    def veri_kaydet(self, dosya, veri):
        with open(dosya, "w", encoding="utf-8") as f:
            json.dump(veri, f, indent=4, ensure_ascii=False)

    # --- COMBOBOX YÜKLEME ---
    def malzemeleri_yukle(self):
        self.cb_malzeme.clear()
        for m_id, m_ad in self.kategoriler.get("material", {}).items():
            self.cb_malzeme.addItem(f"[{m_id}] {m_ad}", m_id)

    def gruplari_yukle(self):
        self.cb_grup.clear()
        m_id = self.cb_malzeme.currentData()
        gruplar = self.kategoriler.get("group", {}).get(m_id, {})
        for g_id, g_ad in gruplar.items():
            if g_id != "last_group_id":
                self.cb_grup.addItem(f"[{g_id}] {g_ad}", g_id)

    def turleri_yukle(self):
        self.cb_urun_turu.clear()
        m_id = self.cb_malzeme.currentData()
        g_id = self.cb_grup.currentData()
        turler = self.kategoriler.get("product", {}).get(m_id, {}).get(g_id, {})
        for t_id, t_detay in turler.items():
            if t_id != "last_product_id":
                self.cb_urun_turu.addItem(f"[{t_id}] {t_detay['ad']}", t_id)

    def markalari_yukle(self):
        self.cb_marka.clear()
        katalog = self.veri_yukle(KATALOG_FILE)
        m_id = self.cb_malzeme.currentData()
        g_id = self.cb_grup.currentData()
        t_id = self.cb_urun_turu.currentData()
        coord = f"{m_id}.{g_id}.{t_id}"
        
        markalar = list(katalog.get(coord, {}).keys())
        self.cb_marka.addItems(markalar)

    def urunleri_listele(self):
        self.tablo.setRowCount(0)
        katalog = self.veri_yukle(KATALOG_FILE)
        m_id = self.cb_malzeme.currentData()
        g_id = self.cb_grup.currentData()
        t_id = self.cb_urun_turu.currentData()
        marka = self.cb_marka.currentText()
        coord = f"{m_id}.{g_id}.{t_id}"

        if coord in katalog and marka in katalog[coord]:
            urunler = katalog[coord][marka]
            self.tablo.setRowCount(len(urunler))
            for row, (sku_id, detay) in enumerate(urunler.items()):
                self.tablo.setItem(row, 0, QTableWidgetItem(detay['tam_ad']))
                self.tablo.setItem(row, 1, QTableWidgetItem(detay['barkod']))
                self.tablo.setItem(row, 2, QTableWidgetItem(detay['birim']))
                # SKU ID'yi gizli veri olarak sakla
                self.tablo.item(row, 0).setData(Qt.ItemDataRole.UserRole, sku_id)

    # --- SİLME MANTIĞI ---
    def urun_sil(self):
        secili_row = self.tablo.currentRow()
        if secili_row == -1:
            QMessageBox.warning(self, "Hata", "Lütfen silmek istediğiniz ürünü tablodan seçin!")
            return

        sku_id = self.tablo.item(secili_row, 0).data(Qt.ItemDataRole.UserRole)
        urun_ad = self.tablo.item(secili_row, 0).text()
        
        # Terminaldeki 'e' onayı yerine QMessageBox
        onay = QMessageBox.critical(self, "DİKKAT: KALICI SİLME", 
                                    f"'{urun_ad}' ürünü katalogdan silinecek ve arşive taşınacak.\n\nBu işlemi onaylıyor musunuz?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if onay == QMessageBox.StandardButton.Yes:
            katalog = self.veri_yukle(KATALOG_FILE)
            arsiv = self.veri_yukle(ARSIV_FILE)
            
            m_id = self.cb_malzeme.currentData()
            g_id = self.cb_grup.currentData()
            t_id = self.cb_urun_turu.currentData()
            marka = self.cb_marka.currentText()
            coord = f"{m_id}.{g_id}.{t_id}"

            silinecek_veri = katalog[coord][marka].pop(sku_id)
            silinecek_veri["arsiv_tarihi"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Arşive Ekle
            if coord not in arsiv: arsiv[coord] = {}
            if marka not in arsiv[coord]: arsiv[coord][marka] = {}
            arsiv[coord][marka][sku_id] = silinecek_veri

            # Marka boşaldıysa markayı da temizle
            if not katalog[coord][marka]:
                katalog[coord].pop(marka)

            self.veri_kaydet(KATALOG_FILE, katalog)
            self.veri_kaydet(ARSIV_FILE, arsiv)

            QMessageBox.information(self, "Başarılı", f"'{urun_ad}' başarıyla silindi ve arşivlendi.")
            self.markalari_yukle() # Listeyi tazele
            self.urunleri_listele()

    def geri_don(self):
        if self.ana_pencere:
            self.ana_pencere.close() # Mevcut pencereyi kapatır

# --- BOSS ---
pencere_tutucu = None
def boss():
    global pencere_tutucu
    app = QApplication.instance() or QApplication(sys.argv)
    pencere_tutucu = QMainWindow()
    pencere_tutucu.setCentralWidget(UrunSilmePaneli(pencere_tutucu))
    pencere_tutucu.setWindowTitle("Ürün Silme Sistemi")
    pencere_tutucu.resize(600, 700)
    pencere_tutucu.show()
    if __name__ == "__main__": sys.exit(app.exec())
    return pencere_tutucu