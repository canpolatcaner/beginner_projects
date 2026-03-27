import json
import os
from datetime import datetime

# Path Ayarları
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(current_path)
MASTER_DATA = os.path.join(project_path, "kategoriler.json")
LOG_DATA = os.path.join(project_path, "stok_hareketleri.json")

def veri_yukle(dosya):
    if not os.path.exists(dosya): return {}
    with open(dosya, "r", encoding="utf-8") as f:
        return json.load(f)

def boss():
    print("\n" + "🏭"*3 + " DEPO STOK GİRİŞ VE LOKASYON KAYDI " + "🏭"*3)
    master = veri_yukle(MASTER_DATA)
    
    full_id = input("\nİşlem yapılacak Ürün ID (m.g.p): ").strip()
    
    # Hiyerarşik Kontrol (Parçalayarak doğrulama)
    try:
        m, g, p = full_id.split(".")
        if p in master.get("product", {}).get(m, {}).get(g, {}):
            urun = master["product"][m][g][p]
            print(f"--- Ürün: {urun['ad']} ({urun['birim']}) ---")
            
            # 1. Miktar ve Fiyat
            miktar = float(input(f"Gelen Miktar ({urun['birim']}): "))
            maliyet = float(input("Birim Maliyet (TL): "))
            etiket = float(input("Satış Etiket Fiyatı (TL): "))
            
            # 2. Lokasyon Bilgisi
            depo_no = input("Depo Bölge No: ").upper()
            raf_no = input("Raf/Göz No: ").upper()
            
            # 3. STT / TETT Ayrımı (Senin kategorizasyonuna göre)
            # Material 1: Sarf (STT), Material 2: Tüketim (TETT) demiştik
            kritik_tip = "STT" if m == "1" else "TETT"
            kritik_tarih = input(f"{kritik_tip} Tarihi (GG-AA-YYYY): ")

            # 4. JSON Kaydı (Zaman Damgalı)
            hareketler = veri_yukle(LOG_DATA)
            bugun = datetime.now().strftime("%Y-%m-%d")
            if bugun not in hareketler: hareketler[bugun] = []

            yeni_hareket = {
                "urun_id": full_id,
                "islem": "DEPO_GIRIS",
                "miktar": miktar,
                "birim": urun["birim"],
                "maliyet": maliyet,
                "etiket": etiket,
                "lokasyon": {"bolge": depo_no, "raf": raf_no},
                "kritik_veri": {"tip": kritik_tip, "tarih": kritik_tarih},
                "saat": datetime.now().strftime("%H:%M:%S")
            }

            hareketler[bugun].append(yeni_hareket)
            with open(LOG_DATA, "w", encoding="utf-8") as f:
                json.dump(hareketler, f, indent=4, ensure_ascii=False)

            print(f"\n✅ Kayıt Başarılı! {full_id} artık {depo_no}-{raf_no} konumunda.")
            
        else:
            print("(!) Bu ürün Master Data'da tanımlı değil.")
    except Exception as e:
        print(f"(!) Hata: {e}")

if __name__ == "__main__":
    boss()