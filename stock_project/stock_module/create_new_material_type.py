import json
import os
import sys

# PATH TANIMI: Tüm modüllerin aynı dosyaya bakmasını sağlayan 'Adres Kaydı'
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(current_path)
DATA_FILE = os.path.join(project_path, "kategoriler.json")

def verileri_yukle():
    if not os.path.exists(DATA_FILE):
        # Dosya yoksa temiz bir başlangıç (1'den başlar)
        baslangic = {"material": {}, "group": {}, "last_material_id": 0}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(baslangic, f, indent=4)
        return baslangic
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def boss():
    print("\n" + "="*40)
    print("MATERIAL YÖNETİMİ (STRATEJİK KAYIT)")
    print("="*40)

    veri = verileri_yukle()
    
    # Her zaman son ID + 1 (Geriye bakmaz, boşluk doldurmaz)
    last_id = veri.get("last_material_id", 0)
    yeni_id = str(last_id + 1)

    m_ad = input(f"ID: {yeni_id} için Material ismi giriniz (Çıkış: 0): ").strip().capitalize()
    
    if m_ad == "0" or not m_ad:
        return

    # Veriyi mühürle
    veri["material"][yeni_id] = m_ad
    veri["last_material_id"] = int(yeni_id)
    
    if yeni_id not in veri["group"]:
        veri["group"][yeni_id] = {"last_group_id": 0} # Bu material'ın alt grup sayacı

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=4, ensure_ascii=False)

    print(f"\n[SİSTEM]: {yeni_id} numaralı kategori tarihçeye işlendi.")

if __name__ == "__main__":
    boss()