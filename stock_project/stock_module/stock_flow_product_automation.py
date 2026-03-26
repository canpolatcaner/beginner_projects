#flow_product_automation
import stock_module.statistics_of_sales
import stock_module.product_price_operations

def boss():
    while True:
        print("-"*30)
        print("╔═════════════════════════════╗")
        print("║ ***ÜRÜN AKIŞ OTOMASYONU***  ║")
        print("║                             ║")
        print("║  1-Satış İstatistikleri     ║")
        print("║  2-Ürün Fiyat İşlemleri     ║")
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
                print(f"{a}'e bastınız; Satış İstatistikleri kısmına yönlendiriliyorsunuz.\n\n")
                stock_module.statistics_of_sales.boss()
            elif a == 2:
                print(f"{a}'ye bastınız; Ürün Fiyat İşlemleri kısmına yönlendiriliyorsunuz.\n\n")
                stock_module.product_price_operations.boss()
            elif a == 0:
                print('Programdan çıkılıyor...')
                break
            else:
                print("Lütfen ÜRÜN AKIŞ OTOMASYONU'nda belirtilen işlemlerden birini seçiniz!\n"*3)
        except ValueError:
            print("Hata: Lütfen sayı giriniz!")
if __name__ == "__main__":
    boss()