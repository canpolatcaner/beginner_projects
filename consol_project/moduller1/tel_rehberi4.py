import sqlite3
import os
import sys



# --- VERİTABANI VE DOSYA YOLU AYARLARI ---
if getattr(sys, 'frozen', False):
    # Eğer program .exe olarak çalışıyorsa (frozen ise)
    DIZIN = os.path.dirname(sys.executable)
else:
    # Eğer program normal .py olarak çalışıyorsa
    DIZIN = os.path.dirname(os.path.abspath(__file__))

DB_YOLU = os.path.join(DIZIN, "rehber_final.db")

def db_hazirla():
    baglanti = sqlite3.connect(DB_YOLU)
    kursor = baglanti.cursor()
    kursor.execute("""
        CREATE TABLE IF NOT EXISTS rehber (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            soyisim TEXT NOT NULL,
            tel1 TEXT NOT NULL UNIQUE,
            tel2 TEXT,
            eposta TEXT,
            is_adresi TEXT,
            ev_adresi TEXT
        )
    """)
    baglanti.commit()
    baglanti.close()

def listele():
    baglanti = sqlite3.connect(DB_YOLU)
    kursor = baglanti.cursor()
    kursor.execute("SELECT * FROM rehber")
    veriler = kursor.fetchall()
    baglanti.close()
    
    print("\n" + "═"*60)
    print(f"{'📋 TÜM REHBER LİSTESİ':^60}")
    print("═"*60)

    if not veriler:
        print(f"{'Rehber şu an boş.':^60}")
    else:
        for v in veriler:
            print(f"🆔 ID: {v[0]:<4} | 👤 {v[1]} {v[2]}")
            print(f"📞 Ana Tel: {v[3]:<15} | 📱 Yedek: {v[4] if v[4] else '-'}")
            print(f"📧 E-posta: {v[5] if v[5] else '-'}")
            print("─"*60)

def kisi_ekle():
    print("\n--- 🆕 YENİ KAYIT EKLE ---")
    isim = input("İsim*: ")
    soyisim = input("Soyisim*: ")
    tel1 = input("Telefon 1 (Benzersiz)*: ")
    tel2 = input("Telefon 2: ") or None
    eposta = input("E-posta: ") or None
    is_adres = input("İş Adresi: ") or None
    ev_adres = input("Ev Adresi: ") or None

    if not isim or not tel1:
        print("❌ Hata: İsim ve Telefon 1 zorunludur!")
        return

    try:
        baglanti = sqlite3.connect(DB_YOLU)
        kursor = baglanti.cursor()
        kursor.execute("""INSERT INTO rehber (isim, soyisim, tel1, tel2, eposta, is_adresi, ev_adresi) 
                          VALUES (?,?,?,?,?,?,?)""", (isim, soyisim, tel1, tel2, eposta, is_adres, ev_adres))
        baglanti.commit()
        baglanti.close()
        print(f"✅ {isim} {soyisim} başarıyla kaydedildi.")
    except sqlite3.IntegrityError:
        print("❌ Hata: Bu telefon numarası zaten başka bir kayıtta var!")

def duzenleme_modu():
    print("\n" + "═"*60)
    print(f"{'🔍 KAYIT BUL VE DÜZENLE':^60}")
    print("═"*60)
    
    hedef = input("Düzenlemek istediğiniz kişinin ismi veya telefonu: ")
    
    baglanti = sqlite3.connect(DB_YOLU)
    baglanti.row_factory = sqlite3.Row
    kursor = baglanti.cursor()
    kursor.execute("SELECT * FROM rehber WHERE isim LIKE ? OR tel1 LIKE ?", (f"%{hedef}%", f"%{hedef}%"))
    sonuclar = kursor.fetchall()
    baglanti.close()

    if not sonuclar:
        print(f"❌ '{hedef}' ile eşleşen bir kayıt bulunamadı.")
        return

    print(f"\n🔎 {len(sonuclar)} eşleşme bulundu:")
    for s in sonuclar:
        print(f"ID: {s['id']} | {s['isim']} {s['soyisim']} | Tel: {s['tel1']}")

    secilen_id = input("\nDüzenlenecek ID'yi yazın (İptal için Enter): ")
    if not secilen_id: return

    kayit = next((dict(s) for s in sonuclar if str(s['id']) == secilen_id), None)
    if not kayit:
        print("❌ Geçersiz ID!"); return

    taslak = kayit.copy()
    
    while True:
        print("\n" + "-"*30)
        print("╔═══════════════════════════════════════════╗")
        print("║              KAYIT DÜZENLEME              ║")
        print(f"║ 1-İsim: {taslak['isim'] or""}            ║")
        print(f"║ 2-Soyisim: {taslak['soyisim']or""}       ║")
        print(f"║ 3-Tel 1: {taslak['tel1'][:9]or""}        ║")
        print(f"║ 4-Tel 2: {str(taslak['tel2'])or""}       ║")
        print(f"║ 5-E-posta: {str(taslak['eposta'])or""}   ║")
        print(f"║ 6-İş Adr: {str(taslak['is_adresi'])or""} ║")
        print(f"║ 7-Ev Adr: {str(taslak['ev_adresi'])or""} ║")
        print("║                                           ║")
        print("║       S-Kaydet             0-İptal        ║")
        print("╚═══════════════════════════════════════════╝")

        secim = input("Seçiminiz (1-7, S, 0): ").lower()

        if secim == 's':
            try:
                baglanti = sqlite3.connect(DB_YOLU)
                kursor = baglanti.cursor()
                sorgu = """UPDATE rehber SET isim=?, soyisim=?, tel1=?, tel2=?, eposta=?, is_adresi=?, ev_adresi=? WHERE id=?"""
                kursor.execute(sorgu, (taslak['isim'], taslak['soyisim'], taslak['tel1'], 
                                       taslak['tel2'], taslak['eposta'], taslak['is_adresi'], 
                                       taslak['ev_adresi'], taslak['id']))
                baglanti.commit()
                baglanti.close()
                print("✅ Kayıt başarıyla güncellendi.")
                break
            except sqlite3.IntegrityError:
                print("❌ Hata: Bu telefon numarası zaten kullanımda!")
        elif secim == '0':
            print("Düzenleme iptal edildi."); break
        
        # Alan eşleştirme (1 -> isim, 2 -> soyisim vb.)
        alanlar = {"1":"isim", "2":"soyisim", "3":"tel1", "4":"tel2", "5":"eposta", "6":"is_adresi", "7":"ev_adresi"}
        
        if secim in alanlar:
            alan_adi = alanlar[secim]
            taslak[alan_adi] = input(f"Yeni {alan_adi} değerini girin: ") or None
        else:
            print("Geçersiz seçim!")

def kayit_sil():
    print("\n--- 🗑️ KAYIT SİLME ---")
    listele()
    silinecek_id = input("\nSilmek istediğiniz ID: ")
    if not silinecek_id: return
    
    onay = input(f"⚠️ ID: {silinecek_id} silinecek. Emin misiniz? (E/H): ").lower()
    if onay == 'e':
        baglanti = sqlite3.connect(DB_YOLU)
        kursor = baglanti.cursor()
        kursor.execute("DELETE FROM rehber WHERE id = ?", (silinecek_id,))
        baglanti.commit()
        baglanti.close()
        print("✅ Kayıt silindi.")

    
def calistir():
    db_hazirla()
    while True:
        print("-"*30)
        print("╔═══════════════════════╗")
        print("║  TELEFON REHBERİ      ║")
        print("║                       ║")
        print("║  1-Kişi Ekle          ║")
        print("║  2-Listele            ║")
        print("║  3-Kişi Düzenle       ║")
        print("║  4-Kişi Sil           ║")
        print("║                       ║")
        print("║                       ║")
        print("║  0-Çıkış              ║")
        print("║                       ║")
        print("║    Seçiminiz nedir?   ║")
        print("╚═══════════════════════╝")

        try:
            secim = int(input("Lütfen ne yapmak istediğinizi seçiniz:\t"))
            if secim == 1:
                print("Kişi eklemeyi seçtiniz.\n\n")
                kisi_ekle()
            elif secim == 2:
                print("Rehberi listelemeyi seçtiniz.\n\n")
                listele()
            elif secim == 3:
                print("Kişileri düzenlemeyi seçtiniz.\n\n")
                duzenleme_modu()
            elif secim == 4:
                print("Kişileri silmeyi seçtiniz.\n\n")
                kayit_sil()
            elif secim == 0:
                print('Ana menüye dönülüyor...')
                break
            else:
                print("Lütfen telefon rehberi menüsünde belirtilen seçeneklerden birini seçiniz!")
        except ValueError:
            print("Hata: Lütfen sayı giriniz!")
if __name__ == "__main__":
    calistir()    
