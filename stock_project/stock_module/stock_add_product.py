#add_product
#stock_product_catalogue
import os
import json
import msvcrt

# PATH AYARLARI
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(current_path)
KATEGORI_FILE = os.path.join(project_path, "kategoriler.json")
KATALOG_FILE = os.path.join(project_path, "urun_katalogu.json")

def verileri_yukle(dosya, varsayilan):
    if not os.path.exists(dosya): return varsayilan
    with open(dosya, "r", encoding="utf-8") as f:
        return json.load(f)

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

def sanal_barkod_uret(katalog):
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

def urun_mukerrer_kontrol(katalog, coord, marka, tam_ad, barkod):
    """Ürün adı veya Barkod çakışması varsa hata mesajı döner."""
    if coord in katalog and marka in katalog[coord]:
        for details in katalog[coord][marka].values():
            if details['tam_ad'].lower() == tam_ad.lower():
                return True, f"DİKKAT: '{tam_ad}' bu marka altında zaten kayıtlı!"
            if barkod and details['barkod'] == barkod:
                return True, f"DİKKAT: '{barkod}' barkodu başka bir ürüne tanımlı!"
    return False, ""

def boss():
    while True: # ANA DÖNGÜ: Kategori Seçimi
        kategoriler = verileri_yukle(KATEGORI_FILE, {})
        katalog = verileri_yukle(KATALOG_FILE, {})

        m_ids = list(kategoriler.get("material", {}).keys())
        m_opts = [f"[{i}] {kategoriler['material'][i]}" for i in m_ids] + ["ANA MENÜYE DÖN"]
        m_idx = dinamik_liste_sec(m_opts, "1. MALZEME TÜRÜ SEÇİN")
        if m_idx == -1 or m_idx == len(m_opts)-1: break
        sel_m = m_ids[m_idx]

        while True: # İKİNCİ DÖNGÜ: Grup Seçimi
            g_dict = kategoriler.get("group", {}).get(sel_m, {})
            g_ids = [k for k in g_dict.keys() if k != "last_group_id"]
            g_opts = [f"[{i}] {g_dict[i]}" for i in g_ids] + ["GERİ"]
            g_idx = dinamik_liste_sec(g_opts, "2. GRUP SEÇİN")
            if g_idx == -1 or g_idx == len(g_opts)-1: break
            sel_g = g_ids[g_idx]

            while True: # ÜÇÜNCÜ DÖNGÜ: Ürün Türü Seçimi
                p_dict = kategoriler.get("product", {}).get(sel_m, {}).get(sel_g, {})
                p_ids = [k for k in p_dict.keys() if k != "last_product_id"]
                p_opts = [f"[{i}] {p_dict[i]['ad']}" for i in p_ids] + ["GERİ"]
                p_idx = dinamik_liste_sec(p_opts, "3. ÜRÜN TÜRÜ SEÇİN")
                if p_idx == -1 or p_idx == len(p_opts)-1: break
                sel_p = p_ids[p_idx]
                coord = f"{sel_m}.{sel_g}.{sel_p}"

                while True: # DÖRDÜNCÜ DÖNGÜ: Marka Seçimi
                    katalog = verileri_yukle(KATALOG_FILE, {}) # Güncel veriyi çek
                    markalar = list(katalog.get(coord, {}).keys())
                    m_opts = markalar + ["[+] YENİ MARKA EKLE", "[<] GERİ"]
                    m_idx = dinamik_liste_sec(m_opts, f"{p_dict[sel_p]['ad']} - MARKA SEÇİMİ")
                    if m_idx == -1 or m_opts[m_idx] == "[<] GERİ": break
                    
                    if m_opts[m_idx] == "[+] YENİ MARKA EKLE":
                        marka_adi = input("\nYeni Marka Adı: ").strip().upper()
                        if not marka_adi: continue
                    else:
                        marka_adi = m_opts[m_idx]

                    while True: # BEŞİNCİ DÖNGÜ: Seri Ürün Kaydı
                        os.system('cls')
                        print(f"Kategori: {p_dict[sel_p]['ad']} | Marka: {marka_adi}")
                        print("=" * 45)
                        spesifik_ad = input("Ürün Detayı (Örn: Labne 250gr) [Çıkış: Enter]: ").strip().capitalize()
                        if not spesifik_ad: break 
                        
                        tam_ad_yeni = f"{marka_adi} {spesifik_ad}"
                        birim = input("Birim (Adet/Paket/KG) [Adet]: ").strip().capitalize() or "Adet"
                        
                        print("\n[Barkod yoksa boş geçin, sistem sanal atayacaktır]")
                        gercek_barkod = input("Gerçek Barkod No: ").strip()
                        
                        # --- MÜKERRER KAYIT KONTROLÜ ---
                        # Eğer gerçek barkod girilmediyse, kontrol için geçici sanal barkod alalım
                        temp_barkod = gercek_barkod if gercek_barkod else "VB-TEMP"
                        exists, msg = urun_mukerrer_kontrol(katalog, coord, marka_adi, tam_ad_yeni, gercek_barkod)
                        
                        if exists:
                            print(f"\n❌ HATA: {msg}")
                            print("Lütfen farklı bir ürün ismi veya barkod giriniz.")
                            msvcrt.getch()
                            continue # Bu ürün için bilgileri tekrar ister

                        # Kayıt onaylandığında gerçek sanal barkodu üret
                        final_barkod = gercek_barkod if gercek_barkod else sanal_barkod_uret(katalog)
                        
                        # Kayıt İşlemi
                        if coord not in katalog: katalog[coord] = {}
                        if marka_adi not in katalog[coord]: katalog[coord][marka_adi] = {}
                        
                        yeni_sku_id = str(len(katalog[coord][marka_adi]) + 1)
                        katalog[coord][marka_adi][yeni_sku_id] = {
                            "tam_ad": tam_ad_yeni,
                            "birim": birim,
                            "barkod": final_barkod
                        }

                        verileri_kaydet(KATALOG_FILE, katalog)
                        print(f"\n✅ KAYDEDİLDİ: {tam_ad_yeni} (Barkod: {final_barkod})")
                        print("-" * 45)
                        # Bir sonraki tur için veriyi tazele
                        katalog = verileri_yukle(KATALOG_FILE, {})

if __name__ == "__main__":
    boss()