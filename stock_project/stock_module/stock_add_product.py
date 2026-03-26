#add_product
def boss():
    while True:
        print("-"*30)
        print("╔═════════════════════════════╗")
        print("║ ***ÜRÜN EKLEME İŞLEMLERİ*** ║")
        print("║                             ║")
        print("║  1-Sarf Malzemesi Ekle      ║")
        print("║  2-Tüketim Malzemesi Ekle   ║")
        print("║                             ║")
        print("║  0-Çıkış                    ║")
        print("║                             ║")
        print("║ Yapmak istediğiniz          ║")
        print("║         işlemi seçiniz:     ║")
        print("║                             ║")
        print("╚═════════════════════════════╝")

        try:
            a = int(input("Lütfen bir işlem seçiniz:\t"))
            if a == 1:
                print(f"{a}'e bastınız; Sarf Malzemesi Ekle kısmına yönlendiriliyorsunuz.\n\n")
                pass
            elif a == 2:
                print(f"{a}'ye bastınız; Tüketim Malzemesi Ekle kısmına yönlendiriliyorsunuz.\n\n")
                pass
            elif a == 0:
                print('Programdan çıkılıyor...')
                break
            else:
                print("Lütfen ÜRÜN EKLEME İŞLEMLERİ'nde belirtilen işlemlerden birini seçiniz!\n"*3)
        except ValueError:
            print("Hata: Lütfen sayı giriniz!")
if __name__ == "__main__":
    boss()