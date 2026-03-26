#calculator

import math

def math_islemi(islem):
    
        sayilar = []  

        print("\nSayıları giriniz (bitirmek için 'q'):")

        while True:
            giris = input(f"{len(sayilar) + 1}.sayı:")
            
            if giris.lower() == "q":
                break

            giris = giris.replace(",", ".")
            if giris.replace(".", "").isdigit():
                sayilar.append(float(giris)) 
            else:
                print("Geçersiz giriş!")

        if  sayilar:           
            
            sonuc = sayilar[0]
            for s in sayilar[1:]:
                if islem == 1:
                    sonuc += s
                elif islem == 2:
                    sonuc -= s
                elif islem == 3:
                    sonuc *= s
                elif islem == 4:
                    if s != 0:
                        sonuc /= s
                    else:
                        print("Sıfıra bölme hatası!")
                        sonuc = None
                        break
                else:
                    print("Geçersiz işlem!")
                    sonuc = None
                    break

            if sonuc is not None:
                print("-"*30)   
                print("Sonuç:", sonuc)
                
        else:
            print("Hiç sayı girilmedi!")
  
def sicaklik_degisimi():
    try:
        a = int(input(("Fahrenayt'tan Santigrat'a çevirmek için: 1'e basınız\n"
                       + "Santigrat'tan Fahrenayt'a çevirmek için: 2'ye basınız\n")))
        if a == 1:
            print("Fahrenayt'tan Santigrat'a dönüştürmeyi seçtiniz\n")
            c = input("Sıcaklık değerini giriniz:\t")
            
            c = c.replace(",",".")
            if c.replace(".","").isdigit():
                c = float(c)
                f = (c-32)*5/9
                print("-"*30)
                print(f"{f:.2f} Santigrat derece")
            else:
                print("Lütfen sayısal bir değer giriniz.")
            
        elif a == 2:
            print("Santigrat'tan Fahrenayt'a dönüştürmeyi seçtiniz\n")
            f = input("Sıcaklık değerini giriniz:\t")
            f = f.replace(",",".")
            if f.replace(".","").isdigit():
                f = float(f)
                c = (f*9/5)+32
                print("-"*30)
                print(f"{c:.2f} Fahrenayt derece")
            else:
                print("Lütfen sayısal bir değer giriniz.")

        else:
            print("Hata: Lütfen 1 veya 2 seçiniz!")
    except ValueError:
        print("Hata: Lütfen sayı giriniz!")

def hesapla_alan():
    try:
        b = int(input("Kare için: 1'e basınız.\nÜçgen için: 2'ye basınız.\nDaire için: 3'e basınız.\n:")) 
        
        if b == 1:
            kare=input("Karenin kenar uzunluğunu giriniz\t:")
            kare=kare.replace(",",".")
            if kare.replace(".","").isdigit():
                deger=float (kare)
                print("Karenin çevresi\t:", deger*4)
                print("Karenin alanı\t:", deger**2)
                    
            else:
                print("Hatalı giriş yaptınız! Lütfen yalnızca sayısal bir değer giriniz.")
        
        elif b == 2:
            kenarlar=[]

            print("Lütfen üçgenin kenar uzunluklarını giriniz:")

            while len(kenarlar)<3:
                try:
                    sayi= float(input(f"{len(kenarlar) + 1}.kenar:"))
                    if sayi<=0:
                        print("Kenar uzunluğu 0'dan büyük olmalıdır!")
            
                    kenarlar.append(sayi)
                except ValueError:
                    print("Lütfen geçerli bir sayı giriniz.")

            a, b, c= kenarlar

            if (a+b>c) and (a+c>b) and (b+c>a):
                cevre = a + b + c
                s = cevre / 2
                alan = math.sqrt(s * (s-a)*(s-b)*(s-c))
                print("-"*30)
                print(f"Üçgenin çevresi\t: {cevre:.2f}")
                print(f"Üçgenin alanı\t: {alan:.2f}")
                
            else:
                print("\nHata: Girdiğiniz kenarlar bir üçgen oluşturmuyor!")
        
        elif b == 3:
            daire=input("Dairenin yarıçapını giriniz\t:")
            daire=daire.replace(",",".")
            if daire.replace(".","").isdigit():
                r=float (daire)
                pi=math.pi 
                cevre=pi*r*2
                alan=pi*r**2   
                print(f"Dairenin çevresi\t: {cevre:.2f}")
                print(f"Dairenin alanı\t: {alan:.2f}")
        else:
            print("Lütfen sayısal bir değer giriniz.")
    except ValueError:
        print("Hata: Lütfen sayı giriniz!")
        
    
def calistir():
    while True:
        print("-"*30)
        print("╔═══════════════════════╗")
        print("║    HESAP MAKİNESİ     ║")
        print("║                       ║")
        print("║  1-Toplama            ║")
        print("║  2-Çıkarma            ║")
        print("║  3-Çarpma             ║")
        print("║  4-Bölme              ║")
        print("║  5-Sıcaklık dönüştürme║")
        print("║    1. Santigrat'a     ║")
        print("║    2. Fahrenayt'a     ║")
        print("║  6-Çevre ve alan bulma║")
        print("║    1. Kare            ║")
        print("║    2. Üçgen           ║")
        print("║    3. Daire           ║")
        print("║                       ║")
        print("║  0-Ana Menüye Dön     ║")
        print("║                       ║")
        print("║    Seçiminiz nedir?   ║")
        print("╚═══════════════════════╝")
        
        try:
            secim = int(input("Lütfen bir işlem seçiniz:\t"))
            if secim == 1:
                print("Toplama işlemini seçtiniz.\n\n")
                math_islemi(1)
            elif secim == 2:
                print("Çıkarma işlemini seçtiniz.\n\n")
                math_islemi(2)
            elif secim == 3:
                print("Çarpma işlemini seçtiniz.\n\n")
                math_islemi(3)
            elif secim == 4:
                print("Bölme işlemini seçtiniz.\n\n")
                math_islemi(4)
            elif secim == 5:
                print("Sıcaklık dönüştürme işlemini seçtiniz.\n\n")
                sicaklik_degisimi()
            elif secim == 6:
                print("Çevre ve alan hesaplama işlemini seçtiniz.\n\n")
                hesapla_alan()
            elif secim == 0:
                print('Ana menüye dönülüyor...')
                break
            else:
                print("Lütfen Hesap Makinesinde belirtilen işlemlerden birini seçiniz!\n"*3)
        except ValueError:
            print("Hata: Lütfen sayı giriniz!")
if __name__ == "__main__":
    calistir()