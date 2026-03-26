#delete_operations_management
def boss():
    while True:
        print("-"*30)
        print("╔═════════════════════════════════╗")
        print("║ ***SİLME İŞLEMLERİ YÖNETİMİ***  ║")
        print("║                                 ║")
        print("║    !!! Silme İşlemleri !!!      ║")
        print("║                                 ║")
        print("║    1-Ürün Sil                   ║")
        print("║    2-Grup Sil                   ║")
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
                print(f"{a}'e bastınız; Ürün Sil kısmına yönlendiriliyorsunuz.\n\n")
                pass
            elif a == 2:
                print(f"{a}'ye bastınız; Grup Sil kısmına yönlendiriliyorsunuz.\n\n")
                pass
            elif a == 3:
                print(f"{a}'ye bastınız; Malzeme Türü Sil kısmına yönlendiriliyorsunuz.\n\n")
                pass
            elif a == 0:
                print('Programdan çıkılıyor...')
                break
            else:
                print("Lütfen SİLME İŞLEMLERİ YÖNETİMİ'nde belirtilen işlemlerden birini seçiniz!\n"*3)
        except ValueError:
            print("Hata: Lütfen sayı giriniz!")
if __name__ == "__main__":
    boss()