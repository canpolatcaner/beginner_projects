import sys
import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QFormLayout, QMessageBox, QFrame, 
                             QApplication, QMainWindow, QComboBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# --- YOL VE DOSYA AYARLARI ---
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

KATEGORI_FILE = os.path.join(project_root, "kategoriler.json")
KATALOG_FILE = os.path.join(project_root, "urun_katalogu.json")

class UrunEklemePaneli(QWidget):
    def __init__(self, ana_pencere=None):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.kategoriler = self.veri_yukle(KATEGORI_FILE)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Başlık
        baslik = QLabel("🆕 YENİ ÜRÜN KATALOG KAYDI")
        baslik.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        # 1. BÖLÜM: HİYERARŞİK SEÇİM (ComboBoxlar)
        self.combo_frame = QFrame()
        self.combo_frame.setFrameShape(QFrame.Shape.StyledPanel)
        combo_layout = QFormLayout(self.combo_frame)

        self.cb_malzeme = QComboBox()
        self.cb_grup = QComboBox()
        self.cb_urun_turu = QComboBox()
        self.cb_marka = QComboBox()
        self.cb_marka.setEditable(True) # Yeni marka elle girilebilsin

        combo_layout.addRow("1. Malzeme Türü:", self.cb_malzeme)
        combo_layout.addRow("2. Ürün Grubu:", self.cb_grup)
        combo_layout.addRow("3. Ürün Türü:", self.cb_urun_turu)
        combo_layout.addRow("4. Marka (Seçin veya Yazın):", self.cb_marka)
        
        layout.addWidget(self.combo_frame)

        # Bağlantıları Kur (Zincirleme Seçim)
        self.cb_malzeme.currentIndexChanged.connect(self.gruplari_yukle)
        self.cb_grup.currentIndexChanged.connect(self.turleri_yukle)
        self.cb_urun_turu.currentIndexChanged.connect(self.markalari_yukle)

        # 2. BÖLÜM: ÜRÜN DETAYLARI
        self.detay_frame = QFrame()
        detay_layout = QFormLayout(self.detay_frame)

        self.input_detay = QLineEdit()
        self.input_detay.setPlaceholderText("Örn: Tam Yağlı Süt 1L")
        
        self.input_birim = QLineEdit("Adet")
        
        self.input_barkod = QLineEdit()
        self.input_barkod.setPlaceholderText("Boş bırakılırsa sanal barkod üretilir")

        detay_layout.addRow("🔍 Ürün Detayı:", self.input_detay)
        detay_layout.addRow("📦 Birim:", self.input_birim)
        detay_layout.addRow("🏷️ Barkod:", self.input_barkod)

        layout.addWidget(self.detay_frame)

        # 3. BÖLÜM: BUTONLAR
        btn_layout = QHBoxLayout()
        self.btn_kaydet = QPushButton("KATALOGA EKLE")
        self.btn_kaydet.setStyleSheet("background-color: #27AE60; color: white; font-weight: bold; height: 40px;")
        self.btn_kaydet.clicked.connect(self.urun_kaydet)

        self.btn_geri = QPushButton("GERİ DÖN")
        self.btn_geri.clicked.connect(self.geri_don)
        
        btn_layout.addWidget(self.btn_geri)
        btn_layout.addWidget(self.btn_kaydet)
        layout.addLayout(btn_layout)

        # İlk yüklemeyi başlat
        self.malzemeleri_yukle()

    # --- VERİ YÖNETİMİ ---
    def veri_yukle(self, dosya):
        if not os.path.exists(dosya): return {}
        with open(dosya, "r", encoding="utf-8") as f:
            return json.load(f)

    def sanal_barkod_uret(self, katalog):
        max_id = 1000
        for kat in katalog.values():
            for marka in kat.values():
                for urun in marka.values():
                    b = urun.get("barkod", "")
                    if b.startswith("VB-"):
                        try:
                            num = int(b.split("-")[1])
                            if num > max_id: max_id = num
                        except: pass
        return f"VB-{max_id + 1}"

    # --- COMBOBOX DOLDURMA MANTIĞI ---
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

    # --- KAYIT MANTIĞI ---
    def urun_kaydet(self):
        m_id = self.cb_malzeme.currentData()
        g_id = self.cb_grup.currentData()
        t_id = self.cb_urun_turu.currentData()
        marka = self.cb_marka.currentText().strip().upper()
        detay = self.input_detay.text().strip().capitalize()
        birim = self.input_birim.text().strip()
        barkod = self.input_barkod.text().strip()

        if not (marka and detay):
            QMessageBox.warning(self, "Hata", "Marka ve Ürün Detayı boş bırakılamaz!"); return

        katalog = self.veri_yukle(KATALOG_FILE)
        coord = f"{m_id}.{g_id}.{t_id}"
        tam_ad = f"{marka} {detay}"

        # Mükerrer Kontrolü
        if coord in katalog and marka in katalog[coord]:
            for urun in katalog[coord][marka].values():
                if urun['tam_ad'].lower() == tam_ad.lower():
                    QMessageBox.warning(self, "Hata", "Bu ürün zaten kayıtlı!"); return
                if barkod and urun['barkod'] == barkod:
                    QMessageBox.warning(self, "Hata", "Bu barkod başka bir ürüne ait!"); return

        # Kayıt İşlemi
        if not barkod:
            barkod = self.sanal_barkod_uret(katalog)

        if coord not in katalog: katalog[coord] = {}
        if marka not in katalog[coord]: katalog[coord][marka] = {}

        yeni_id = str(len(katalog[coord][marka]) + 1)
        katalog[coord][marka][yeni_id] = {
            "tam_ad": tam_ad,
            "birim": birim,
            "barkod": barkod
        }

        with open(KATALOG_FILE, "w", encoding="utf-8") as f:
            json.dump(katalog, f, indent=4, ensure_ascii=False)

        QMessageBox.information(self, "Başarılı", f"Ürün Kataloga Eklendi!\nBarkod: {barkod}")
        self.input_detay.clear()
        self.input_barkod.clear()
        self.markalari_yukle()

    def geri_don(self):
        if self.ana_pencere: self.ana_pencere.close()

# --- BOSS ---
pencere_tutucu = None
def boss():
    global pencere_tutucu
    app = QApplication.instance() or QApplication(sys.argv)
    pencere_tutucu = QMainWindow()
    pencere_tutucu.setCentralWidget(UrunEklemePaneli(pencere_tutucu))
    pencere_tutucu.setWindowTitle("Katalog Ürün Kaydı")
    pencere_tutucu.resize(500, 500)
    pencere_tutucu.show()
    if __name__ == "__main__": sys.exit(app.exec())
    return pencere_tutucu