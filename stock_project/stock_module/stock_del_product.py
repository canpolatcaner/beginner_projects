#del_product
#stock_product_catalogue
import os
import json
import msvcrt

# PATH AYARLARI
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(current_path)
KATEGORI_FILE = os.path.join(project_path, "kategoriler.json")
KATALOG_FILE = os.path.join(project_path, "urun_katalogu.json")
ARSIV_FILE = os.path.join(project_path, "urun_arsivi_log.json")

def verileri_yukle(dosya):
    if not os.path.exists(dosya): return {}
    with open(dosya, "r", encoding="utf-8") as f:
        return json.load(f)

def verileri_kaydet(dosya, veri):
    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=4, ensure_ascii=False)

def dinamik_liste_sec(opsiyonlar, baslik):
    secili_index = 0
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*55)
        print(f" {baslik:^53} ")
        print("="*55)
        for i, opt in enumerate(opsiyonlar):
            if i == secili_index:
                print(f" ==> \033[91m{opt:<47}\033[0m") # Silme tehlikesi: Kırmızı
            else:
                print(f"     {opt:<47}")
        print("="*55)
        print("(↑/↓: Gez | Enter: Seç | ESC: İptal)")

        key = msvcrt.getch()
        if key == b'\x1b': return -1
        elif key == b'\r': return secili_index
        elif key in (b'\x00', b'\xe0'):
            nx_key = msvcrt.getch()
            if nx_key == b'H': secili_index = (secili_index - 1) % len(opsiyonlar)
            elif nx_key == b'P': secili_index = (secili_index + 1) % len(opsiyonlar)

def boss():
    while True:
        kategoriler = verileri_yukle(KATEGORI_FILE)
        katalog = verileri_yukle(KATALOG_FILE)
        arsiv = verileri_yukle(ARSIV_FILE)

        # 1. ADIM: Material -> Group -> Product Navigasyonu
        m_ids = list(kategoriler.get("material", {}).keys())
        m_opts = [f"[{i}] {kategoriler['material'][i]}" for i in m_ids] + ["İPTAL / GERİ"]
        m_idx = dinamik_liste_sec(m_opts, "SİLİNECEK ÜRÜN: MALZEME TÜRÜ")
        if m_idx == -1 or m_idx == len(m_opts)-1: break
        sel_m = m_ids[m_idx]

        g_dict = kategoriler.get("group", {}).get(sel_m, {})
        g_ids = [k for k in g_dict.keys() if k != "last_group_id"]
        g_opts = [f"[{i}] {g_dict[i]}" for i in g_ids] + ["GERİ"]
        g_idx = dinamik_liste_sec(g_opts, "SİLİNECEK ÜRÜN: GRUP TÜRÜ")
        if g_idx == -1 or g_idx == len(g_opts)-1: continue
        sel_g = g_ids[g_idx]

        p_dict = kategoriler.get("product", {}).get(sel_m, {}).get(sel_g, {})
        p_ids = [k for k in p_dict.keys() if k != "last_product_id"]
        p_opts = [f"[{i}] {p_dict[i]['ad']}" for i in p_ids] + ["GERİ"]
        p_idx = dinamik_liste_sec(p_opts, "SİLİNECEK ÜRÜN: ÜRÜN TÜRÜ")
        if p_idx == -1 or p_idx == len(p_opts)-1: continue
        sel_p = p_ids[p_idx]
        
        coord = f"{sel_m}.{sel_g}.{sel_p}"

        # 2. ADIM: Katalog Kontrolü (O koordinatta ürün var mı?)
        if coord not in katalog:
            print(f"\n⚠️ Bu kategoride ({p_dict[sel_p]['ad']}) henüz kayıtlı ürün yok!")
            msvcrt.getch()
            continue

        # 3. ADIM: Marka Seçimi
        markalar = list(katalog[coord].keys())
        m_opts = markalar + ["GERİ"]
        m_idx = dinamik_liste_sec(m_opts, f"{p_dict[sel_p]['ad']} - MARKA SEÇİMİ")
        if m_idx == -1 or m_opts[m_idx] == "GERİ": continue
        sel_marka = markalar[m_idx]

        # 4. ADIM: Spesifik Ürün (SKU) Seçimi
        sku_listesi = katalog[coord][sel_marka]
        sku_ids = list(sku_listesi.keys())
        sku_opts = [f"{sku_listesi[i]['tam_ad']} ({sku_listesi[i]['barkod']})" for i in sku_ids] + ["GERİ"]
        
        sku_idx = dinamik_liste_sec(sku_opts, f"{sel_marka} - SİLİNECEK ÜRÜNÜ SEÇİN")
        if sku_idx == -1 or sku_opts[sku_idx] == "GERİ": continue
        
        sel_sku_id = sku_ids[sku_idx]
        silinecek_urun = sku_listesi[sel_sku_id]

        # 5. ADIM: Klavye 'e' Onayı ile Silme
        os.system('cls')
        print("\n" + "!"*45)
        print(f" ÜRÜN SİLME ONAYI ".center(45, "!"))
        print("!"*45)
        print(f"\n SİLECEĞİNİZ ÜRÜN: {silinecek_urun['tam_ad']}")
        print(f" BARKOD          : {silinecek_urun['barkod']}")
        print(f" BİRİM           : {silinecek_urun['birim']}")
        print("\n" + "-"*45)
        print("BU İŞLEM GERİ ALINAMAZ!")
        onay = input("\nSilme işlemini onaylıyor musunuz? (onay için 'e' basın): ").lower()

        if onay == 'e':
            # --- İstatistikler için Arşive ekle ---
            if coord not in arsiv: arsiv[coord] = {}
            if sel_marka not in arsiv[coord]: arsiv[coord][sel_marka] = {}
            arsiv[coord][sel_marka][sel_sku_id] = silinecek_urun
            arsiv[coord][sel_marka][sel_sku_id]["arsiv_tarihi"] = "2026-03-30"

            # --- Katalogdan Çıkar ---
            katalog[coord][sel_marka].pop(sel_sku_id)

            # EĞER MARKANIN ALTINDA HİÇ ÜRÜN KALMADIYSA MARKAYI DA SİL
            if not katalog[coord][sel_marka]:
                katalog[coord].pop(sel_marka)
                print(f"\n💡 {sel_marka} markasına ait ürün kalmadığı için marka da silindi.")

            verileri_kaydet(KATALOG_FILE, katalog)
            verileri_kaydet(ARSIV_FILE, arsiv)
            print(f"\n✅ {silinecek_urun['tam_ad']} silindi ve arşive taşındı.")
        else:
            print("\n❌ İşlem iptal edildi.")
        
        print("\nDevam etmek için bir tuşa basın...")
        msvcrt.getch()

if __name__ == "__main__":
    boss()