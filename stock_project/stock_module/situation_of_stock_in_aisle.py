# from depot to aisle transfer and stock deduction module
import json
import os
from datetime import datetime, timedelta
import msvcrt
import sys

# Dosya Yolları
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(current_path)
KATEGORI_FILE = os.path.join(project_path, "kategoriler.json")
CURRENT_STOCK = os.path.join(project_path, "mevcut_stok.json")
LOG_FILE = os.path.join(project_path, "reyon_hareketleri.json")
REYON_STOCK_FILE = os.path.join(project_path, "reyon_stok.json")
KATALOG_FILE = os.path.join(project_path, "urun_katalogu.json")
SATIS_HAREKETLERI_FILE = os.path.join(project_path, "satis_hareketleri.json") # YENİ

# --- YARDIMCI FONKSİYONLAR ---
def veri_yukle(dosya):
    if not os.path.exists(dosya): return {}
    try:
        with open(dosya, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def veri_kaydet(dosya, veri):
    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=4, ensure_ascii=False)

# --- FİYAT ANALİZ VE İSTATİSTİK MOTORU (YENİ) ---
def satis_hizi_analizi(urun_id):
    """Ürünün günlük ortalama satış hızını hesaplar."""
    satis_verisi = veri_yukle(SATIS_HAREKETLERI_FILE)
    satislar = satis_verisi.get("satislar", [])
    ilgili_satislar = [s for s in satislar if s["urun_id"] == urun_id]
    
    if not ilgili_satislar:
        return 0.5 # Veri yoksa günde yarım adet satıyor varsayalım (muhafazakar tahmin)
    
    toplam_miktar = sum(s["miktar"] for s in ilgili_satislar)
    tarihler = [datetime.strptime(s["satis_zamani"], "%Y-%m-%d %H:%M:%S") for s in ilgili_satislar]
    gun_farki = (max(tarihler) - min(tarihler)).days
    
    return toplam_miktar / max(gun_farki, 1)

def fiyat_onerisi_al(urun_id, batch_data, reyon_stok_data):
    """STT ve Satış hızına göre indirim önerisi üretir."""
    bugun = datetime.now()
    stt = datetime.strptime(batch_data['stt'], "%d.%m.%Y")
    kalan_gun = (stt - bugun).days
    gunluk_hiz = satis_hizi_analizi(urun_id)
    
    # Toplam stok (Depo partisi + Reyondaki mevcutlar)
    toplam_stok = batch_data['miktar_mevcut']
    if urun_id in reyon_stok_data:
        toplam_stok += sum(p['miktar_mevcut'] for p in reyon_stok_data[urun_id]['partiler'])
    
    tahmini_tuketim_suresi = toplam_stok / gunluk_hiz
    
    indirim = 0
    neden = "Ürün durumu normal."

    if kalan_gun <= 7:
        indirim = 50
        neden = "⚠️ KRİTİK: SKT/TETT'ye 1 haftadan az kaldı!"
    elif kalan_gun <= 20:
        indirim = 20
        neden = "📅 DİKKAT: Son Tüketim Tarihi yaklaşıyor."
    elif tahmini_tuketim_suresi > kalan_gun:
        indirim = 15
        neden = "📉 RİSK: Satış hızı düşük, ürün STT'den önce bitmeyebilir."
    
    return indirim, neden, gunluk_hiz

# --- MEVCUT DİNAMİK ARAYÜZ FONKSİYONLARI ---
def dinamik_liste_sec(opsiyonlar, baslik):
    if not opsiyonlar: return -1
    secili_index = 0
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*55)
        print(f" {baslik:^53} ")
        print("="*55)
        for i, opt in enumerate(opsiyonlar):
            if i == secili_index:
                print(f" ==> \033[92m{opt:<42}\033[0m")
            else:
                print(f"     {opt:<42}")
        print("="*55)
        print("(↑/↓: Gez | Enter: Seç | ESC: İptal)")
        key = msvcrt.getch()
        if key == b'\x1b': return -1
        elif key == b'\r': return secili_index
        elif key in (b'\x00', b'\xe0'):
            nx_key = msvcrt.getch()
            if nx_key == b'H': secili_index = (secili_index - 1) % len(opsiyonlar)
            elif nx_key == b'P': secili_index = (secili_index + 1) % len(opsiyonlar)

def hareket_logla(urun_id, urun_ad, miktar, islem_tipi, zaman, detay_bilgi, neden="Normal"):
    kayitlar = veri_yukle(LOG_FILE)
    if "log" not in kayitlar: kayitlar["log"] = []
    kayitlar["log"].append({
        "zaman": zaman,
        "urun_id": urun_id,
        "urun_ad": urun_ad,
        "miktar": miktar,
        "islem": islem_tipi,
        "neden": neden,
        "kaynak_lokasyon": detay_bilgi.get("lokasyon", "-"),
        "stt": detay_bilgi.get("stt", "-"),
        "batch_id": detay_bilgi.get("batch_id", "-")
    })
    veri_kaydet(LOG_FILE, kayitlar)

def urun_secme_navigasyonu(stok, kategoriler):
    stoktaki_id_listesi = [k for k in stok.keys() if any(p['miktar_mevcut'] > 0 for p in stok[k]['partiler'])]
    if not stoktaki_id_listesi: 
        print("\n⚠️ Stokta ürün bulunamadı!"); msvcrt.getch(); return None

    m_ids = sorted(list(set(id.split('.')[0] for id in stoktaki_id_listesi)))
    m_idx = dinamik_liste_sec([f"[{i}] {kategoriler['material'].get(i, '??')}" for i in m_ids], "MALZEME SEÇ")
    if m_idx == -1: return None
    sel_m = m_ids[m_idx]

    g_ids = sorted(list(set(id.split('.')[1] for id in stoktaki_id_listesi if id.startswith(f"{sel_m}."))))
    g_idx = dinamik_liste_sec([f"[{i}] {kategoriler['group'].get(sel_m, {}).get(i, '??')}" for i in g_ids], "GRUP SEÇ")
    if g_idx == -1: return None
    sel_g = g_ids[g_idx]

    p_ids = sorted(list(set(id.split('.')[2] for id in stoktaki_id_listesi if id.startswith(f"{sel_m}.{sel_g}."))))
    p_opts = [f"[{i}] {kategoriler['product'].get(sel_m, {}).get(sel_g, {}).get(i, {}).get('ad', '??')}" for i in p_ids]
    p_idx = dinamik_liste_sec(p_opts, "ÜRÜN SEÇ")
    if p_idx == -1: return None
    sel_p = p_ids[p_idx]

    final_ids = [id for id in stoktaki_id_listesi if id.startswith(f"{sel_m}.{sel_g}.{sel_p}.")]
    f_idx = dinamik_liste_sec([f"{stok[id]['urun_ad']}" for id in final_ids], "MARKA/SKU ONAYLA")
    return final_ids[f_idx] if f_idx != -1 else None

def esc_destekli_input(mesaj, varsayilan=""):
    print(mesaj, end="", flush=True)
    input_str = ""
    while True:
        char = msvcrt.getch()
        if char == b'\x1b': return None
        elif char == b'\r': 
            print()
            return input_str if input_str else varsayilan
        elif char == b'\x08': 
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

# --- ANA FONKSİYONLAR ---
def reyon_transfer_yap():
    stok = veri_yukle(CURRENT_STOCK)
    katalog = veri_yukle(KATALOG_FILE)
    kategoriler = veri_yukle(KATEGORI_FILE)
    reyon_stok = veri_yukle(REYON_STOCK_FILE)
    
    full_id = urun_secme_navigasyonu(stok, kategoriler)
    if not full_id: return

    parts = full_id.split('.')
    try:
        urun_detay = katalog[f"{parts[0]}.{parts[1]}.{parts[2]}"][parts[3]][parts[4]]
    except KeyError:
        print("\n❌ Ürün katalogda bulunamadı!"); msvcrt.getch(); return

    tam_urun_adi = urun_detay['tam_ad']
    urun_barkodu = urun_detay['barkod'] 

    toplam_depo_stok = sum(p['miktar_mevcut'] for p in stok[full_id]['partiler'])
    # STT'ye göre sıralı partiler
    partiler = sorted(stok[full_id]['partiler'], key=lambda x: datetime.strptime(x['stt'], "%d.%m.%Y"))
    ilk_parti = partiler[0] # En riskli parti

    # FİYAT ANALİZİ VE ÖNERİ EKRANI
    indirim, neden, hiz = fiyat_onerisi_al(full_id, ilk_parti, reyon_stok)

    os.system('cls')
    print(f"--- REYONA SEVKİYAT VE FİYATLANDIRMA ---")
    print(f"Ürün      : {tam_urun_adi}")
    print(f"Barkod    : {urun_barkodu}")
    print(f"Depo Stok : {toplam_depo_stok}")
    print("-" * 40)
    print(f"📊 Satış Hızı   : Günlük ortalama {hiz:.2f} adet")
    print(f"📅 En Yakın STT : {ilk_parti['stt']}")
    print(f"💡 ANALİZ       : {neden}")
    
    if indirim > 0:
        print(f"\033[93m🔥 ÖNERİ       : Ürüne %{indirim} indirim yapmanız tavsiye edilir!\033[0m")
    else:
        print("✅ ÖNERİ       : Standart fiyattan devam edilebilir.")
    print("-" * 40)

    # Manuel Fiyat Girişi
    maliyet = ilk_parti.get('maliyet', 0)
    print(f"Birim Maliyet: {maliyet} TL")
    fiyat_raw = esc_destekli_input("👉 Reyon Satış Fiyatını Girin: ")
    if fiyat_raw is None: return
    try:
        satis_fiyati = float(fiyat_raw.replace(",", "."))
    except:
        print("\n❌ Geçersiz fiyat!"); msvcrt.getch(); return

    # Sevk Miktarı Girişi
    miktar_raw = esc_destekli_input("👉 Sevk Miktarı: ")
    if not miktar_raw: return

    try:
        istenen = float(miktar_raw.replace(",", "."))
        if istenen <= 0 or istenen > toplam_depo_stok:
            print(f"\n❌ Geçersiz miktar! (Max: {toplam_depo_stok})"); msvcrt.getch(); return

        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        kalan = istenen

        if full_id not in reyon_stok:
            reyon_stok[full_id] = {"urun_ad": tam_urun_adi, "partiler": []}

        for parti in partiler:
            if kalan <= 0: break
            if parti['miktar_mevcut'] <= 0: continue

            alinacak = min(parti['miktar_mevcut'], kalan)
            parti['miktar_mevcut'] -= alinacak
            kalan -= alinacak

            reyon_stok[full_id]["partiler"].append({
                "batch_id": parti['batch_id'],
                "barkod": urun_barkodu, 
                "miktar_mevcut": alinacak,
                "maliyet": parti.get('maliyet', 0),
                "satis_fiyati": satis_fiyati, # Belirlenen fiyat buraya yazılıyor
                "reyona_giris_tarihi": zaman,
                "stt": parti.get('stt', "Belirtilmedi")
            })

            detay = {"lokasyon": parti.get('lokasyon','-'), "stt": parti['stt'], "batch_id": parti['batch_id']}
            hareket_logla(full_id, tam_urun_adi, alinacak, "DEPO_CIKIS_REYON_GIRIS", zaman, detay)

        # Temizlik
        stok[full_id]['partiler'] = [p for p in stok[full_id]['partiler'] if p['miktar_mevcut'] > 0]

        veri_kaydet(CURRENT_STOCK, stok)
        veri_kaydet(REYON_STOCK_FILE, reyon_stok)

        print(f"\n✅ {istenen} Adet ürün {satis_fiyati} TL fiyatla başarıyla sevk edildi."); msvcrt.getch()

    except Exception as e:
        print(f"\n❌ Hata: {e}"); msvcrt.getch()

def stok_dus_yap():
    stok = veri_yukle(CURRENT_STOCK)
    kategoriler = veri_yukle(KATEGORI_FILE)
    full_id = urun_secme_navigasyonu(stok, kategoriler)
    if not full_id: return

    tam_urun_adi = stok[full_id]['urun_ad']
    iade_birimi = ["1- Satıştan Geri İade", "2- Depodan İade"]
    b_idx = dinamik_liste_sec(iade_birimi, "DÜŞÜŞ BİLGİSİ")
    if b_idx == -1: return
    iade_nedeni = ["1- Bozuk Ürün", "2- Uygunsuz Ürün"]
    n_idx = dinamik_liste_sec(iade_nedeni, "DÜŞÜŞ NEDENİ")
    if n_idx == -1: return

    os.system('cls')
    try:
        miktar = float(input(f"Stoktan Düşülecek Miktar ({tam_urun_adi}): ").replace(",", "."))
        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        parti = next((p for p in sorted(stok[full_id]['partiler'], key=lambda x: datetime.strptime(x['stt'], "%d.%m.%Y")) if p['miktar_mevcut'] > 0), None)

        if miktar <= parti['miktar_mevcut']:
            detay = {"lokasyon": parti['lokasyon'], "stt": parti['stt'], "batch_id": parti['batch_id']}
            
            if b_idx == 0: # Satıştan Geri İade
                parti['miktar_mevcut'] -= miktar
                islem = "STOK_ANORMAL_DUSUS (Müşteri Geri İade)"
            else: # Depodan İade
                parti['miktar_mevcut'] -= miktar
                islem = "STOK_ANORMAL_DUSUS (Depodan İade)"

            hareket_logla(full_id, tam_urun_adi, miktar, islem, zaman, detay, iade_birimi[b_idx] + " - " + iade_nedeni[n_idx])
            veri_kaydet(CURRENT_STOCK, stok)
            print(f"\n✅ İşlem başarıyla kaydedildi."); msvcrt.getch()
        else:
            print("\n❌ Stok yetersiz!"); msvcrt.getch()
    except:
        print("\n❌ Hata!"); msvcrt.getch()

def boss():
    while True:
        menu_opts = ["1- Reyona Sevk (Fiyat Önerisiyle)", "2- Stoktan Düş (Hata/İade)", "3- Çıkış"]
        secim = dinamik_liste_sec(menu_opts, "REYON DURUM VE KONTROL")
        
        if secim == 0:
            reyon_transfer_yap() 
        elif secim == 1:
            stok_dus_yap()
        elif secim == 2 or secim == -1:
            print("\nSistemden çıkıldı."); break

if __name__ == "__main__":
    boss()