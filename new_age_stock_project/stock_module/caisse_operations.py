import os
import json
import msvcrt
from datetime import datetime

# --- DOSYA VE PATH YAPILANDIRMASI ---
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(current_path)

KATALOG_FILE = os.path.join(project_path, "urun_katalogu.json")
DEPO_STOK_FILE = os.path.join(project_path, "mevcut_stok.json")
REYON_STOK_FILE = os.path.join(project_path, "reyon_stok.json")
REYON_HAREKET_FILE = os.path.join(project_path, "reyon_hareketleri.json")
SATIS_LOG_FILE = os.path.join(project_path, "satis_hareketleri.json")

def verileri_yukle(dosya, varsayilan):
    if not os.path.exists(dosya): return varsayilan
    try:
        with open(dosya, "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            if not icerik: return varsayilan
            return json.loads(icerik)
    except: return varsayilan

def verileri_kaydet(dosya, veri):
    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=4, ensure_ascii=False)
        
def dinamik_liste_sec(opsiyonlar, baslik):
    secili_index = 0
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*50)
        print(f" {baslik:^48} ")
        print("="*50)
        for i, opt in enumerate(opsiyonlar):
            if i == secili_index:
                print(f" ==> \033[92m{opt:<42}\033[0m")
            else:
                print(f"     {opt:<42}")
        print("="*50)
        print("(↑/↓: Gez | Enter: Seç | ESC: Üst Menü)")

        key = msvcrt.getch()
        if key == b'\x1b': return -1
        elif key == b'\r': return secili_index
        elif key in (b'\x00', b'\xe0'):
            nx_key = msvcrt.getch()
            if nx_key == b'H': secili_index = (secili_index - 1) % len(opsiyonlar)
            elif nx_key == b'P': secili_index = (secili_index + 1) % len(opsiyonlar)

def urun_bul_barkodla(barkod, katalog):
    # Katalog yapın: { "2.1.1": { "PINAR": { "1": { "tam_ad": "...", "barkod": "..." } } } }
    for u_id_prefix, markalar in katalog.items():
        if not isinstance(markalar, dict): continue # #mevcut ürünler yorum satırı vb. için
        for marka, urunler in markalar.items():
            for sku, detay in urunler.items():
                if isinstance(detay, dict) and detay.get('barkod') == barkod:
                    return f"{u_id_prefix}.{marka}.{sku}", detay
    return None, None

def satis_yap():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        katalog = verileri_yukle(KATALOG_FILE, {})
        reyon = verileri_yukle(REYON_STOK_FILE, {})
        
        print("\n" + "█"*50)
        print(f"{'HIZLI KASA / SATIŞ EKRANI':^50}")
        print("█"*50)
        print("\n(Çıkış için ESC'ye basın veya boş bırakıp Enter yapın)")
        
        barkod = input("\n👉 Barkod Okutun: ").strip()
        if not barkod: break
        
        u_id, u_detay = urun_bul_barkodla(barkod, katalog)
        
        if not u_id or u_id not in reyon or not reyon[u_id].get("partiler"):
            print("\n❌ Ürün reyonda bulunamadı veya stokta yok!"); msvcrt.getch(); continue

        # FIFO (İlk giren ilk çıkar)
        parti = reyon[u_id]["partiler"][0]
        
        print(f"\nÜrün: {u_detay['tam_ad']}")
        print(f"Lot: {parti['batch_id']} | Reyon Mevcut: {parti['miktar_mevcut']}")
        
        # Eğer reyon_stok'ta satış fiyatı 0 ise katalogdan veya varsayılan bir yerden alabilirsin
        fiyat = parti.get('satis_fiyati', 0)
        print(f"Birim Fiyat: {fiyat:.2f} TL")

        try:
            miktar_raw = input("Satış Miktarı: ").replace(",", ".")
            miktar = float(miktar_raw)
            
            if miktar > parti['miktar_mevcut']:
                print("⚠️ Bu lotun stoğu yetersiz!"); msvcrt.getch(); continue
            
            # 1. Reyon Stok Güncelleme
            parti['miktar_mevcut'] -= miktar
            parti['son_satis_zamani'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if parti['miktar_mevcut'] <= 0:
                reyon[u_id]["partiler"].pop(0)

            # 2. Satış Logu
            satislar = verileri_yukle(SATIS_LOG_FILE, {"satislar": []})
            satislar["satislar"].append({
                "satis_zamani": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "urun_id": u_id,
                "urun_ad": u_detay['tam_ad'],
                "batch_id": parti['batch_id'],
                "miktar": miktar,
                "maliyet": parti.get('maliyet', 0),
                "satis_fiyati": fiyat,
                "toplam": miktar * fiyat
            })

            verileri_kaydet(REYON_STOK_FILE, reyon)
            verileri_kaydet(SATIS_LOG_FILE, satislar)
            print(f"\n✅ Satış Tamamlandı! Toplam: {miktar*fiyat:.2f} TL"); msvcrt.getch()
        except ValueError:
            print("\n❌ Geçersiz miktar!"); msvcrt.getch()

def iade_islemi():
    os.system('cls' if os.name == 'nt' else 'clear')
    katalog = verileri_yukle(KATALOG_FILE, {})
    
    print("\n" + "!"*50)
    print(f"{'MÜŞTERİ İADE YÖNETİMİ':^50}")
    print("!"*50)
    
    barkod = input("\n👉 İade Ürün Barkodu: ").strip()
    u_id, u_detay = urun_bul_barkodla(barkod, katalog)
    
    if not u_id:
        print("\n❌ Ürün katalogda bulunamadı!"); msvcrt.getch(); return

    try:
        miktar = float(input("İade Miktarı: ").replace(",", "."))
        print("\n1 - Sağlam (Depoya Geri Gönder)\n2 - Bozuk/Uygunsuz (Fire Loguna İşle)")
        secim = input("Seçim: ")

        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if secim == "1":
            depo = verileri_yukle(DEPO_STOK_FILE, {})
            if u_id not in depo: depo[u_id] = {"urun_ad": u_detay['tam_ad'], "partiler": []}
            
            depo[u_id]["partiler"].append({
                "batch_id": f"IADE-{datetime.now().strftime('%m%d%H%M')}",
                "miktar_mevcut": miktar,
                "maliyet": 0,
                "lokasyon": "IADE-RAFI",
                "stt": "01.01.2099",
                "giris_zamani": zaman,
                "not": "Müşteri İadesi (Sağlam)"
            })
            verileri_kaydet(DEPO_STOK_FILE, depo)
            print("\n✅ Ürün Depoya (İade Rafı) aktarıldı."); msvcrt.getch()

        elif secim == "2":
            hareketler = verileri_yukle(REYON_HAREKET_FILE, {"log": []})
            neden = input("Hasar Nedeni: ")
            hareketler["log"].append({
                "zaman": zaman,
                "urun_id": u_id,
                "urun_ad": u_detay['tam_ad'],
                "miktar": miktar,
                "islem": "MUSTERI_IADE_KUSURLU",
                "neden": neden
            })
            verileri_kaydet(REYON_HAREKET_FILE, hareketler)
            print("\n✅ Kusurlu ürün kayda alındı (Fire)."); msvcrt.getch()
    except Exception as e:
        print(f"\n❌ Hata: {e}"); msvcrt.getch()


def boss():
    while True:
        # Menü seçeneklerini bir listeye alıyoruz
        menu_opts = ["1- Kasa Satış", "2- Müşteri İadesi", "3- Çıkış"]
        
        # Fonksiyon bize seçilen elemanın İNDEKSİNİ (0, 1, 2) döndürür
        secim = dinamik_liste_sec(menu_opts, "KASA İŞLEMLERİ")
        
        if secim == 0:    # 0. indeks "1- Kasa Satış" demektir
            satis_yap()
            
        elif secim == 1:  # 1. indeks "2- Müşteri İadesi" demektir
            iade_islemi()
            
        elif secim == 2 or secim == -1: # 2. indeks "Çıkış" veya ESC (-1)
            print("\nKasa kapatıldı. İyi çalışmalar!")
            break

if __name__ == "__main__":
    boss()