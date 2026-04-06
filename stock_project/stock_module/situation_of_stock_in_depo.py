import json
import os
from datetime import datetime
import msvcrt
import sys

# Path Ayarları
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(current_path)
KATEGORI_FILE = os.path.join(project_path, "kategoriler.json")
KATALOG_FILE = os.path.join(project_path, "urun_katalogu.json")
CURRENT_STOCK = os.path.join(project_path, "mevcut_stok.json")

def veri_yukle(dosya):
    if not os.path.exists(dosya): return {}
    with open(dosya, "r", encoding="utf-8") as f:
        return json.load(f)

def veri_kaydet(dosya, veri):
    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=4, ensure_ascii=False)

def esc_destekli_input(mesaj, varsayilan=""):
    """ESC ile iptal, Enter ile onay. Varsayılan değer desteği (Raf Hafızası için)."""
    print(mesaj, end="", flush=True)
    if varsayilan:
        print(f"[{varsayilan}]", end="", flush=True)
    
    input_str = ""
    while True:
        char = msvcrt.getch()
        if char == b'\x1b': return None
        elif char == b'\r': 
            print()
            return input_str if input_str else varsayilan
        elif char == b'\x08': # Backspace
            if len(input_str) > 0:
                input_str = input_str[:-1]
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        else:
            try:
                c = char.decode('utf-8')
                input_str += c
                print(c, end="", flush=True)
            except: pass

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
        print("(↑/↓: Gez | Enter: Seç | ESC: Geri)")

        key = msvcrt.getch()
        if key == b'\x1b': return -1
        elif key == b'\r': return secili_index
        elif key in (b'\x00', b'\xe0'):
            nx_key = msvcrt.getch()
            if nx_key == b'H': secili_index = (secili_index - 1) % len(opsiyonlar)
            elif nx_key == b'P': secili_index = (secili_index + 1) % len(opsiyonlar)

def urun_bul_veya_sec():
    katalog = veri_yukle(KATALOG_FILE)
    kategoriler = veri_yukle(KATEGORI_FILE)
    
    while True:
        # ANA GİRİŞ YÖNTEMİ SEÇİMİ
        ana_secenekler = ["1. BARKOD OKUT", "2. MANUEL NAVİGASYON", "3. SİSTEMİ KAPAT"]
        secim = dinamik_liste_sec(ana_secenekler, "GİRİŞ YÖNTEMİ SEÇİN")
        
        if secim == -1 or secim == 2: return "EXIT", None
        
        # BARKOD OKUTMA
        if secim == 0:
            os.system('cls')
            print("--- BARKOD MODU ---")
            barkod = esc_destekli_input("👉 Barkodu Okutun veya Yazın: ")
            if not barkod: continue
            
            for coord, markalar in katalog.items():
                for marka, urunler in markalar.items():
                    for sku_id, detay in urunler.items():
                        if detay['barkod'] == barkod:
                            return f"{coord}.{marka}.{sku_id}", detay
            print("\n❌ Barkod bulunamadı!"); msvcrt.getch(); continue

        # MANUEL NAVİGASYON
        if secim == 1:
            m_ids = list(kategoriler.get("material", {}).keys())
            m_idx = dinamik_liste_sec([f"[{i}] {kategoriler['material'][i]}" for i in m_ids], "MALZEME TÜRÜ")
            if m_idx == -1: continue
            sel_m = m_ids[m_idx]

            g_dict = kategoriler.get("group", {}).get(sel_m, {})
            g_ids = [k for k in g_dict.keys() if k != "last_group_id"]
            g_idx = dinamik_liste_sec([f"[{i}] {g_dict[i]}" for i in g_ids], "GRUP TÜRÜ")
            if g_idx == -1: continue
            sel_g = g_ids[g_idx]

            p_dict = kategoriler.get("product", {}).get(sel_m, {}).get(sel_g, {})
            p_ids = [k for k in p_dict.keys() if k != "last_product_id"]
            p_idx = dinamik_liste_sec([f"[{i}] {p_dict[i]['ad']}" for i in p_ids], "ÜRÜN TÜRÜ")
            if p_idx == -1: continue
            sel_p = p_ids[p_idx]

            coord = f"{sel_m}.{sel_g}.{sel_p}"
            if coord not in katalog:
                print("\n⚠️ Marka kaydı yok!"); msvcrt.getch(); continue

            markalar = list(katalog[coord].keys())
            m_idx = dinamik_liste_sec(markalar, "MARKA SEÇİMİ")
            if m_idx == -1: continue
            sel_marka = markalar[m_idx]

            urunler = katalog[coord][sel_marka]
            u_ids = list(urunler.keys())
            u_idx = dinamik_liste_sec([f"{urunler[i]['tam_ad']}" for i in u_ids], "ÜRÜNÜ SEÇİN")
            if u_idx == -1: continue
            
            return f"{coord}.{sel_marka}.{u_ids[u_idx]}", urunler[u_ids[u_idx]]

def boss():
    while True:
        stok = veri_yukle(CURRENT_STOCK)
        full_id, urun_verisi = urun_bul_veya_sec()
        
        if full_id == "EXIT": break

        # RAF HAFIZASI: Bu ürün daha önce nereye girmiş?
        eski_lokasyon = ""
        if full_id in stok and stok[full_id]["partiler"]:
            eski_lokasyon = stok[full_id]["partiler"][-1]["lokasyon"]

        while True:
            os.system('cls')
            print(f"--- {urun_verisi['tam_ad']} GİRİŞİ ---")
            
            miktar_raw = esc_destekli_input("📥 Miktar (Lütfen birim girmeden yazınız(!)): ")
            if miktar_raw is None: break
            
            maliyet_raw = esc_destekli_input("💰 Maliyet (TL): ")
            if maliyet_raw is None: break
            
            # LOKASYON: Hafızadaki yeri otomatik getir, sadece ENTER'a basması yetsin!
            print(f"📍 Lokasyon Hafızası: {eski_lokasyon if eski_lokasyon else 'Yeni Ürün'}")
            loc = esc_destekli_input("👉 Raf (Örn: 02-A1): ", varsayilan=eski_lokasyon)
            if loc is None: break

            stt = esc_destekli_input("⏳ STT/TETT: ")
            if stt is None: break

            print(f"\nOnaylıyor musunuz? (E/H)")
            if msvcrt.getch().lower() == b'e':
                if full_id not in stok: stok[full_id] = {"urun_ad": urun_verisi['tam_ad'], "partiler": []}
                stok[full_id]["partiler"].append({
                    "batch_id": f"B-{datetime.now().strftime('%m%d%H%M')}",
                    "miktar_mevcut": float(miktar_raw.replace(",",".")),
                    "maliyet": float(maliyet_raw.replace(",",".")),
                    "lokasyon": loc,
                    "stt": stt,
                    "giris_zamani": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                veri_kaydet(CURRENT_STOCK, stok)
                print("\n✅ Tamamdır!"); msvcrt.getch(); break
            else: break

if __name__ == "__main__":
    boss()