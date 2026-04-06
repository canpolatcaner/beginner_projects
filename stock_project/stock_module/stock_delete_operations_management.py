import json
import os

# PATH AYARLARI
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(current_path)
DATA_FILE = os.path.join(project_path, "kategoriler.json")

def verileri_yukle():
    if not os.path.exists(DATA_FILE):
        return {"material": {}, "group": {}, "product": {}, "last_material_id": 0}
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        veri = json.load(f)
        for key in ["material", "group", "product"]:
            if key not in veri:
                veri[key] = {}
        if "last_material_id" not in veri:
            veri["last_material_id"] = 0
        return veri

def verileri_kaydet(veri):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=4, ensure_ascii=False)

def listele_ve_onayla(veri, seviye="product"):
    """Silme öncesi mevcut durumu gösterir (Hata payını sıfırlar)"""
    print("\n--- MEVCUT DURUM ---")
    if seviye == "material":
        for k, v in veri["material"].items(): print(f"[{k}] {v}")
    elif seviye == "group":
        # Önce malzemeleri döküyoruz ki kullanıcı grup hangi malzemenin altında bilsin
        for k, v in veri["material"].items(): print(f"[{k}] {v}")
        m_id = input("\nHangi Malzeme Türü altındaki Grup Türünü sileceksiniz? (ID): ")
        if m_id in veri["group"]:
            print(f"\n--- {veri['material'][m_id]} Grubu Seçenekleri ---")
            for k, v in veri["group"][m_id].items():
                if k != "last_group_id": print(f"[{k}] {v}")
            return m_id
    elif seviye == "product_flow":
        # Ürün silme akışı için malzeme listesini dök
        for k, v in veri["material"].items(): print(f"[{k}] {v}")
    return None

def boss():
    while True:
        veri = verileri_yukle()
        print("-" * 30)
        print("╔═════════════════════════════════╗")
        print("║ ***SİLME İŞLEMLERİ YÖNETİMİ***  ║")
        print("║                                 ║")
        print("║    !!! Silme İşlemleri !!!      ║")
        print("║                                 ║")
        print("║    1-Ürün Sil                   ║")
        print("║    2-Grup Türü Sil              ║")
        print("║    3-Malzeme Türü Sil           ║")
        print("║                                 ║")
        print("║  0-Çıkış                        ║")
        print("║                                 ║")
        print("║ Yapmak istediğiniz              ║")
        print("║         işlemi seçiniz:         ║")
        print("║                                 ║")
        print("╚═════════════════════════════════╝")

        try:
            a = int(input("Lütfen bir işlem seçiniz:\t"))
            
            if a == 1:
                print(f"{a}'e bastınız; Ürün Sil kısmına yönlendiriliyorsunuz.\n")
                
                # ADIM 1: Malzemeleri Listele
                listele_ve_onayla(veri, "product_flow")
                m = input("Malzeme numarası (ID): ")
                
                # ADIM 2: Grupları Listele
                if m in veri.get("group", {}):
                    print(f"\n--- {veri['material'][m]} Altındaki Gruplar ---")
                    for k, v in veri["group"][m].items():
                        if k != "last_group_id": print(f"[{k}] {v}")
                    g = input("\nGrup numarası (ID): ")
                    
                    # ADIM 3: Ürünleri Listele
                    if g in veri.get("product", {}).get(m, {}):
                        print(f"\n--- {veri['group'][m][g]} Altındaki Ürünler ---")
                        for k, v in veri["product"][m][g].items():
                            if k != "last_product_id": print(f"[{k}] {v['ad']} ({v['birim']})")
                        p = input("\nSilinecek Ürün numarası (ID): ")
                        
                        if m in veri.get("product", {}) and g in veri["product"][m] and p in veri["product"][m][g]:
                            onay = input(f"'{veri['product'][m][g][p]['ad']}' silinecek. Onay (e/h)? ").lower()
                            if onay == 'e':
                                veri["product"][m][g].pop(p)
                                verileri_kaydet(veri)
                                print("✅ Ürün silindi.")
                        else: print("Ürün bulunamadı!.")
                    else: print("Geçersiz Grup ID!.")
                else: print("Geçersiz Malzeme ID!.")

            elif a == 2:
                print(f"{a}'ye bastınız; Grup Türü Sil kısmına yönlendiriliyorsunuz.\n")
                m_id = listele_ve_onayla(veri, "group")
                if m_id:
                    g_id = input("\nSilinecek Grup Türü numarası (ID): ")
                    if g_id in veri["group"][m_id]:
                        onay = input(f"'{veri['group'][m_id][g_id]}' ve bağlı ürünler silinecek. Onay (e/h)? ").lower()
                        if onay == 'e':
                            veri["group"][m_id].pop(g_id)
                            if m_id in veri["product"] and g_id in veri["product"][m_id]:
                                veri["product"][m_id].pop(g_id)
                            verileri_kaydet(veri)
                            print("✅ Grup Türüne bağlı ürünler silindi.")
                    else: print("Grup bulunamadı!.")

            elif a == 3:
                print(f"{a}'ye bastınız; Malzeme Türü Sil kısmına yönlendiriliyorsunuz.\n")
                listele_ve_onayla(veri, "material")
                m_id = input("\nSilinecek Material ID: ")
                
                if m_id in veri.get("material", {}):
                    onay = input(f"'{veri['material'][m_id]}' tüm alt kategorileriyle birlikte silinecek! Onay (e/h)? ").lower()
                    if onay == 'e':
                        veri["material"].pop(m_id)
                        if "group" in veri and m_id in veri["group"]:
                            veri["group"].pop(m_id)
                        if "product" in veri and m_id in veri["product"]:
                            veri["product"].pop(m_id)
                        
                        verileri_kaydet(veri)
                        print(f"✅ Malzeme Türü {m_id} ve bağlı tüm alt kategorileri temizlendi.")
                else:
                    print("Geçersiz numara (ID).")

            elif a == 0:
                print('Programdan çıkılıyor...')
                break
            else:
                print("Lütfen geçerli bir işlem seçiniz!\n")
        except ValueError:
            print("Hata: Lütfen Silme İşlemleri Yönetiminde belirtilen ilgili numarayı girerek işlem yapınız!")

if __name__ == "__main__":
    boss()