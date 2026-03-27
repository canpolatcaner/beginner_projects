#material and group management
import stock_module.create_new_product_type
import stock_module.create_new_group_type       
import stock_module.create_new_material_type  
import stock_module.stock_delete_operations_management   

def boss():
    while True:
        print("-"*30)
        print("╔═════════════════════════════════╗")
        print("║ ***MALZEME VE GRUP YÖNETİMİ***  ║")
        print("║                                 ║")
        print("║  1-Yeni Malzeme Türü Oluştur    ║")
        print("║  2-Yeni Grup Türü Oluştur       ║")
        print("║  3-Yeni Ürün Türü Oluştur       ║")
        print("║                                 ║")
        print("║  4-Silme İşlemleri !!!          ║")
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
                print(f"{a}'e bastınız; Yeni Malzeme Türü Oluştur kısmına yönlendiriliyorsunuz.\n\n")
                stock_module.create_new_material_type.boss()
            elif a == 2:
                print(f"{a}'ye bastınız; Yeni Grup Türü Oluştur kısmına yönlendiriliyorsunuz.\n\n")
                stock_module.create_new_group_type.boss()
            elif a == 3:
                print(f"{a}'ye bastınız; Yeni Ürün Türü Oluştur kısmına yönlendiriliyorsunuz.\n\n")
                stock_module.create_new_product_type.boss()
            elif a == 4:    
                print(f"{a}'ye bastınız; Silme İşlemleri kısmına yönlendiriliyorsunuz.\n\n")
                stock_module.stock_delete_operations_management.boss()
            elif a == 0:
                print('Programdan çıkılıyor...')
                break
            else:
                print("Lütfen MALZEME VE GRUP YÖNETİMİ'nde belirtilen işlemlerden birini seçiniz!\n"*3)
        except ValueError:
            print("Hata: Lütfen işleme ait numarayı girerek işlem yapınız!")
if __name__ == "__main__":
    boss()
def hierarchical_id_create(material, group, product):
    return f"{material}.{group}.{product}"