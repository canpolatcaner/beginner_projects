#stock_product_operations_management

import stock_module.stock_add_product
import stock_module.stock_del_product
def boss():
    while True:
        print("-"*30)
        print("╔═════════════════════════════╗")
        print("║  ***STOK TAKİP İŞLEMLERİ*** ║")
        print("║                             ║")
        print("║  1-Ürün Ekle                ║")
        print("║  2-Ürün Sil                 ║")
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
                print(f"{a}'e bastınız; Ürün Ekle kısmına yönlendiriliyorsunuz.\n\n")
                stock_module.stock_add_product.boss()
            elif a == 2:
                print(f"{a}'ye bastınız; Ürün Sil kısmına yönlendiriliyorsunuz.\n\n")
                stock_module.stock_del_product.boss()
            elif a == 0:
                print('Programdan çıkılıyor...')
                break
            else:
                print("Lütfen STOK TAKİP İŞLEMLERİ'nde belirtilen işlemlerden birini seçiniz!\n"*3)
        except ValueError:
            print("Hata: Lütfen işleme ait numarayı girerek işlem yapınız!")
if __name__ == "__main__":
    boss()