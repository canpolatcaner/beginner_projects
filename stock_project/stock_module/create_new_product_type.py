import json
import os

# Veri merkezimize giden yol
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(current_path)
DATA_FILE = os.path.join(project_path, "kategoriler.json")

def verileri_yukle():
    if not os.path.exists(DATA_FILE):
        return {"material": {}, "group": {}, "product": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def boss():
    print("\n" + "="*45)
    print("YENİ ÜRÜN TÜRÜ OLUŞTURMA")
    print("="*45)

    veri = verileri_yukle()
    
    if not veri["material"]:
        print("Önce Malzeme ve Grup Türü oluşturmalısınız!")
        return

    # 1. Material Seçimi
    print("\n[1] Malzeme Seçiniz:")
    m_list = list(veri["material"].keys())
    for m_id, m_ad in veri["material"].items():
        print(f"{m_id} - {m_ad}")
    
    m_secim = input("Seçim (ID): ").strip()
    if m_secim not in m_list: return print("Geçersiz seçim.")

    # 2. Group Seçimi
    if m_secim not in veri["group"] or len(veri["group"][m_secim]) <= 1:
        return print("Bu Malzeme Türü altında henüz Grup Türü tanımlanmamıştır!")

    print(f"\n[2] {veri['material'][m_secim]} Altındaki Gruplar:")
    for g_id, g_ad in veri["group"][m_secim].items():
        if g_id != "last_group_id":
            print(f"{g_id} - {g_ad}")
    
    g_secim = input("Seçim (ID): ").strip()
    if g_secim not in veri["group"][m_secim]: return print("Geçersiz seçim.")

    # 3. Otomatik Product ID Üretimi
    if "product" not in veri: veri["product"] = {}
    if m_secim not in veri["product"]: veri["product"][m_secim] = {}
    if g_secim not in veri["product"][m_secim]:
        veri["product"][m_secim][g_secim] = {"last_product_id": 0}

    last_p_id = veri["product"][m_secim][g_secim].get("last_product_id", 0)
    yeni_p_id = str(last_p_id + 1)

    # 4. Ürün İsmi ve Birim Girişi
    p_ad = input(f"\nYeni Ürün İsmi (ID {yeni_p_id}): ").strip().capitalize()
    print("Birim Seçiniz: 1-Adet, 2-Kilogram, 3-Litre, 4-Metre")
    birimler = {"1": "Adet", "2": "Kilogram", "3": "Litre", "4": "Metre"}
    b_secim = input("Birim No: ").strip()
    birim = birimler.get(b_secim, "Adet")

    if p_ad:
        # Ürünü birimiyle birlikte sözlük olarak kaydediyoruz
        veri["product"][m_secim][g_secim][yeni_p_id] = {
            "ad": p_ad,
            "birim": birim
        }
        veri["product"][m_secim][g_secim]["last_product_id"] = int(yeni_p_id)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(veri, f, indent=4, ensure_ascii=False)
        
        full_id = f"{m_secim}.{g_secim}.{yeni_p_id}"
        print(f"\n[KAYIT BAŞARILI]")
        print(f"ID: {full_id} | İsim: {p_ad} | Birim: {birim}")

if __name__ == "__main__":
    boss()