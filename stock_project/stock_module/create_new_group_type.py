import json
import os

# PATH: Ana dizindeki JSON'a ulaşmak için (sys kullanmadan, direkt adresle)
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(current_path)
DATA_FILE = os.path.join(project_path, "kategoriler.json")

def verileri_yukle():
    if not os.path.exists(DATA_FILE):
        return {"material": {}, "group": {}, "last_material_id": 0}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def boss():
    print("\n" + "="*40)
    print("GRUP YÖNETİMİ")
    print("="*40)

    veri = verileri_yukle()
    
    # 1. Mevcut Material'ları listele (Seçim yaptır)
    if not veri["material"]:
        print("Önce bir Malzeme Türü oluşturmalısınız!")
        return

    print("\nMevcut Malzeme Türleri:")
    for m_id, m_ad in veri["material"].items():
        print(f"{m_id} - {m_ad}")

    m_secim = input("\nHangi Malzeme Türü altına Grup ekleyeceksiniz? (ID girin): ").strip()

    if m_secim not in veri["material"]:
        print("Geçersiz Malzeme Türü numarası (ID Error)!")
        return

    # 2. O Material'a özel grup sayacını yönet
    # Eğer bu material için hiç grup alanı açılmamışsa (tamir amaçlı)
    if m_secim not in veri["group"]:
        veri["group"][m_secim] = {"last_group_id": 0}

    last_g_id = veri["group"][m_secim].get("last_group_id", 0)
    yeni_g_id = str(last_g_id + 1)

    # 3. Kullanıcıdan isim al
    g_ad = input(f"Material {m_secim} için Yeni Grup ({yeni_g_id}) İsmi: ").strip().capitalize()
    
    if not g_ad:
        return

    # 4. Kayıt (Hiyerarşik saklama)
    # Yapı: veri["group"]["2"]["1"] = "Otomobil"
    veri["group"][m_secim][yeni_g_id] = g_ad
    veri["group"][m_secim]["last_group_id"] = int(yeni_g_id)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=4, ensure_ascii=False)

    print(f"\n[BAŞARILI] {m_secim}.{yeni_g_id} - {g_ad} hiyerarşiye işlendi.")

if __name__ == "__main__":
    boss()