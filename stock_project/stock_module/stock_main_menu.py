#stock_main_menu
import stock_module.stock_add_product
import stock_module.stock_delete_operations_management
import stock_module.stock_flow_product_automation  
import stock_module.stock_material_and_group_management
import stock_module.stock_keeping


while True:
    print("-"*30)
    print("╔═════════════════════════════╗")
    print("║  ***STOK TAKİP PROGRAMI***  ║")
    print("║                             ║")
    print("║  1-Stok Takip İşlemleri     ║")
    print("║  2-Ürün Ekleme İşlemleri    ║")
    print("║  3-Ürün Akış Otomasyonu     ║")
    print("║  4-Malzeme ve Grup Yönetimi ║")
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
            print(f"{a}'e bastınız; Stok Takip İşlemleri bölümüne yönlendiriliyorsunuz.\n\n")
            stock_module.stock_keeping.boss()
        elif a == 2:
            print(f"{a}'ye bastınız; Ürün Ekleme İşlemleri bölümüne yönlendiriliyorsunuz.\n\n")
            stock_module.stock_add_product.boss()
        elif a == 3:
            print(f"{a}'e bastınız; Ürün Akış Otomasyonu bölümüne yönlendiriliyorsunuz.\n\n")
            stock_module.stock_flow_product_automation.boss()
        elif a == 4:
            print(f"{a}'e bastınız; Malzeme ve Grup Yönetimi bölümüne yönlendiriliyorsunuz.\n\n")
            stock_module.stock_material_and_group_management.boss()
        elif a == 0:
            print('Programdan çıkılıyor...')
            break
        else:
            print("Lütfen STOK TAKİP PROGRAMI'nda belirtilen işlemlerden birini seçiniz!\n"*3)
    except ValueError:
        print("Hata: Lütfen sayı giriniz!")