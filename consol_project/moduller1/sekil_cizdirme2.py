#design_menu
import turtle
import time
import random

def selcuklu():   
    try:
        uzunluk = int(input("Lütfen bir uzunluk giriniz:\t"))
        aci = int(input("Lütfen açı değerini giriniz:\t"))
        
        k1=turtle.Turtle()
        k1.pensize(5)
        k1.pencolor("black")
        k2=turtle.Turtle()
        k2.pensize(7)
        k2.pencolor("blue")
        k1.speed(10)
        k2.speed(10)    
        for i in range(8):
            for a in range (4):
                k2.forward(uzunluk)
                k2.right(aci)
            k2.right(45)  
        
        for j in range (11):
            for b in range (4):
                k1.forward (50)
                k1.right (90)
            k1.right (30)     
        
        t = turtle.Turtle()
        t.penup()
        screen = turtle.Screen()

        screen.bgcolor("black")
        t.speed(0)
        t.pensize(1)

        colours = ["red", "purple", "blue", "green", "orange", "yellow"]
        t.pendown()
        for x in range(360):
            t.pencolor(colours[x % 6])
            t.width(x / 100 + 1)
            t.forward(x)
            t.left(59)
        print("Şekil çizildi, işlemler menüsüne geri dönülüyor...")
        time.sleep(6)  
        turtle.clearscreen()   
    except ValueError:
        print("Hata: Lütfen sayı giriniz!")

def tribal_kare():

    try:
        tekrar_sayisi = int(input("Lütfen tekrar sayısı giriniz:\t"))
              
        t = turtle.Pen()
        t.speed(0)
        for x in range(tekrar_sayisi):
            t.forward(x)
            t.left(90)   
        print("Şekil çizildi, işlemler menüsüne geri dönülüyor...")
        time.sleep(6)
        turtle.clearscreen() 
    except ValueError:
        print("Hata: Lütfen sayı giriniz!")

def tribal_spiral():
    try:
        tekrar_sayisi = int(input("Lütfen tekrar sayısı giriniz:\t"))
        sayi_havuzu = list(range(80, 90)) + list(range(91, 96))  
        sayi= random.choice(sayi_havuzu)   
        t = turtle.Pen()
        t.speed(0)
        for x in range(tekrar_sayisi):
            t.forward(x)
            t.left(sayi)
        print("Şekil çizildi, işlemler menüsüne geri dönülüyor...")
        time.sleep(6)
        turtle.clearscreen() 
    except ValueError:
        print("Hata: Lütfen sayı giriniz!")

def virus():
    try:
        frekans = int(input("Lütfen bir frekans değeri giriniz:\t"))
        frekans_havuzu = list(range(210, 300))
        frekans = random.choice(frekans_havuzu)      
        t = turtle.Turtle()
        s = turtle.Screen()

        # Ekran ve kalem ayarları
        s.bgcolor("black")
        t.pencolor("red")
        t.speed(0)

        a = 0
        b = 0

        t.penup()
        t.goto(0, 200)
        t.pendown()

        while True:
            t.forward(a)
            t.right(b)
            a += 3
            b += 1

            if b == frekans:
                break

        t.hideturtle()
        print("Şekil çizildi, işlemler menüsüne geri dönülüyor...")
        time.sleep(6)
        turtle.clearscreen() 
    except ValueError:
        print("Hata: Lütfen sayı giriniz!")

def calistir():
    while True:
        print("-"*30)
        print("╔═══════════════════════╗")
        print("║                       ║")
        print("║    Şekil Çizdirme     ║")
        print("║                       ║")
        print("║  1-Selçuklu Yıldızı   ║")
        print("║  2-Tribal Kare        ║")
        print("║  3-Tribal Spiral      ║")
        print("║  4-Virüs              ║")
        print("║                       ║")
        print("║  0-Çıkış              ║")
        print("║                       ║")
        print("║    Seçiminiz nedir?   ║")
        print("╚═══════════════════════╝")

        try:
            secim = input("Lütfen bir şekil seçiniz: ")
            if secim == "1": 
                print("Selçuklu Yıldızı şeklini seçtiniz.")
                selcuklu()
            elif secim == "2": 
                print("Tribal Kare şeklini seçtiniz.")
                tribal_kare()
            elif secim == "3":
                print("Tribal Spiral şeklini seçtiniz.")
                tribal_spiral()
            elif secim == "4":
                print("Virüs şeklini seçtiniz.")
                virus()
            elif secim == "0":
                print("Ana menüye yönlendiriliyorsunuz...")
                break
            else:
                print("Lütfen menüdeki şekillerden birini seçiniz")
        except ValueError:
            print("Geçersiz seçim yaptınız.")    

if __name__ == "__main__":
    calistir()
    