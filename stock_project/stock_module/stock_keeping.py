#stock_keeping
import stock_module.situation_of_stock_in_aisle 
import stock_module.situation_of_stock_in_depo
def boss():
    while True:
        print("-"*30)
        print("╔═════════════════════════════╗")
        print("║  ***STOK TAKİP İŞLEMLERİ*** ║")
        print("║                             ║")
        print("║  1-Reyon Stok Durumu        ║")
        print("║  2-Depo Stok Durumu         ║")
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
                print(f"{a}'e bastınız; Reyon Stok Durumu kısmına yönlendiriliyorsunuz.\n\n")
                stock_module.situation_of_stock_in_aisle.boss()
            elif a == 2:
                print(f"{a}'ye bastınız; Depo Stok Durumu kısmına yönlendiriliyorsunuz.\n\n")
                stock_module.situation_of_stock_in_depo.boss()
            elif a == 0:
                print('Programdan çıkılıyor...')
                break
            else:
                print("Lütfen STOK TAKİP İŞLEMLERİ'nde belirtilen işlemlerden birini seçiniz!\n"*3)
        except ValueError:
            print("Hata: Lütfen işleme ait numarayı girerek işlem yapınız!")
if __name__ == "__main__":
    boss()