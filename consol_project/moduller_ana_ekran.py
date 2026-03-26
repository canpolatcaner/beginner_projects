#main_menu
import moduller1.hesap_makinesi
import moduller1.sekil_cizdirme2
import moduller1.oyunlar3
import moduller1.tel_rehberi4

while True:
    print("-"*30)
    print("╔═══════════════════════╗")
    print("║    İşlemler           ║")
    print("║                       ║")
    print("║  1-Hesaplamalar       ║")
    print("║  2-Şekil Çizdirme     ║")
    print("║  3-Oyunlar            ║")
    print("║  4-Telefon Rehberi    ║")
    print("║                       ║")
    print("║  0-Çıkış              ║")
    print("║                       ║")
    print("║    Seçiminiz nedir?   ║")
    print("╚═══════════════════════╝")

    try:
        a = int(input("Lütfen bir işlem seçiniz:\t"))
        if a == 1:
            print(f"{a}'e bastınız; Hesaplamalar bölümüne yönlendiriliyorsunuz.\n\n")
            moduller1.hesap_makinesi.calistir()
        elif a == 2:
            print(f"{a}'ye bastınız; Şekil Çizdirme bölümüne yönlendiriliyorsunuz.\n\n")
            moduller1.sekil_cizdirme2.calistir()
        elif a == 3:
            print(f"{a}'e bastınız; Oyunlar bölümüne yönlendiriliyorsunuz.\n\n")
            moduller1.oyunlar3.calistir()
        elif a == 4:
            print(f"{a}'e bastınız; Telefon Rehberi bölümüne yönlendiriliyorsunuz.\n\n")
            moduller1.tel_rehberi4.calistir()
        elif a == 0:
            print('Programdan çıkılıyor...')
            break
        else:
            print("Lütfen Hesap Makinesinde belirtilen işlemlerden birini seçiniz!\n"*3)
    except ValueError:
        print("Hata: Lütfen sayı giriniz!")