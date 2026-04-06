#stock_main_menu
import sys
import os

# 1. Mevcut dosyanın yolunu al (stock_main_menu.py'nin olduğu yer)
current_path = os.path.dirname(os.path.abspath(__file__))

# 2. Bir üst dizini bul (stock_project klasörü)
project_path = os.path.dirname(current_path)

# 3. Python'ın arama listesine (sys.path) bu yolu ekle
if project_path not in sys.path:
    sys.path.insert(0, project_path)

import stock_module.stock_product_operations_management
import stock_module.stock_flow_product_automation  
import stock_module.stock_material_and_group_management
import stock_module.stock_keeping


while True:
    print("-"*30)
    print("╔═════════════════════════════╗")
    print("║  ***STOK TAKİP PROGRAMI***  ║")
    print("║                             ║")
    print("║  1-Stok Takip İşlemleri     ║")
    print("║  2-Ürün İşlemleri           ║")
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
            print(f"{a}'ye bastınız; Ürün İşlemleri bölümüne yönlendiriliyorsunuz.\n\n")
            stock_module.stock_product_operations_management.boss()
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
        print("Hata: Lütfen işleme ait numarayı girerek işlem yapınız!")