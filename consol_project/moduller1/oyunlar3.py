import turtle
import random
import time

# --- YARDIMCI FONKSİYONLAR ---
def ekran_temizle():
    try:
        turtle.resetscreen() # Mevcut ekranı temizlemeyi dene
    except turtle.Terminator:
        # Eğer ekran kapandıysa, turtle modülünü tazeleyip devam et
        turtle.TurtleScreen._RUNNING = True 
    except Exception:
        pass

# --- TETRİS OYUNU ---
def tetris_oyunu():
    ekran_temizle()
    window = turtle.Screen()
    window.title("Mini Tetris")
    window.bgcolor("black")
    window.setup(width=400, height=600)
    window.tracer(0)

    genislik, yukseklik, hucre_boyutu = 10, 20, 20
    sekiller = [
        [[1, 1, 1], [0, 1, 0]], [[0, 2, 2], [2, 2, 0]], [[3, 3, 0], [0, 3, 3]],
        [[4, 0, 0], [4, 4, 4]], [[0, 0, 5], [5, 5, 5]], [[6, 6, 6, 6]], [[7, 7], [7, 7]]
    ]

    renkler = ["black", "purple", "green", "red", "blue", "orange", "cyan", "yellow"]

    # Oyun Alanı (Grid) Oluşturma
    grid = [[0 for _ in range(genislik)] for _ in range(yukseklik)]

    # Çizim kalemi
    pen = turtle.Turtle()
    pen.penup()
    pen.speed(0)
    pen.hideturtle()

    def hucre_ciz(x, y, renk_indeksi):
        x_pos = -100 + (x * hucre_boyutu)
        y_pos = 200 - (y * hucre_boyutu)
        pen.goto(x_pos, y_pos)
        pen.color("white", renkler[renk_indeksi])
        pen.begin_fill()
        for _ in range(4):
            pen.forward(hucre_boyutu - 1)
            pen.right(90)
        pen.end_fill()

    def ekrani_guncelle(grid, parca, px, py):
        pen.clear()
        # Izgarayı ve yerleşmiş parçaları çiz
        for y in range(yukseklik):
            for x in range(genislik):
                hucre_ciz(x, y, grid[y][x])
        
        # Hareket eden parçayı çiz
        if parca:
            for y, satir in enumerate(parca):
                for x, deger in enumerate(satir):
                    if deger:
                        hucre_ciz(px + x, py + y, deger)
        window.update()

    
    # Tetris mantığı (Çarpışma Kontrolü)
    def carpisma_var_mi(grid, parca, px, py):
        for y, satir in enumerate(parca):
            for x, deger in enumerate(satir):
                if deger:
                    if (px + x < 0 or px + x >= genislik or 
                        py + y >= yukseklik or grid[py + y][px + x]):
                        return True
        return False

    durum = {"px": 3, "py": 0, "parca": random.choice(sekiller), "oyun_devam": True}

    def sola(): 
        if not carpisma_var_mi(grid, durum["parca"], durum["px"] - 1, durum["py"]): durum["px"] -= 1
    def saga(): 
        if not carpisma_var_mi(grid, durum["parca"], durum["px"] + 1, durum["py"]): durum["px"] += 1
    def dondur():
        yeni_parca = list(zip(*durum["parca"][::-1]))
        if not carpisma_var_mi(grid, yeni_parca, durum["px"], durum["py"]): 
            durum["parca"] = yeni_parca
    def hizlandir():
        if not carpisma_var_mi(grid, durum["parca"], durum["px"], durum["py"] + 1):
            durum["py"] += 1
    def tam_asagi():
        while not carpisma_var_mi(grid, durum["parca"], durum["px"], durum["py"] + 1):
            durum["py"] += 1

    window.listen()
    window.onkeypress(sola, "Left")
    window.onkeypress(saga, "Right")
    window.onkeypress(dondur, "Up")
    window.onkeypress(hizlandir, "Down") 
    window.onkeypress(tam_asagi, "space")

    # Ana Döngü
    sayac = 0
    try:
        while durum["oyun_devam"]:
            pen.clear()
            for y in range(yukseklik):
                for x in range(genislik): hucre_ciz(x, y, grid[y][x])
            for y, satir in enumerate(durum["parca"]):
                for x, deger in enumerate(satir):
                    if deger: hucre_ciz(durum["px"] + x, durum["py"] + y, deger)
            window.update()
            sayac += 1
            if sayac % 10 == 0:
                if not carpisma_var_mi(grid, durum["parca"], durum["px"], durum["py"] + 1):
                    durum["py"] += 1
                else:
                    for y, satir in enumerate(durum["parca"]):
                        for x, deger in enumerate(satir):
                            if deger: grid[durum["py"] + y][durum["px"] + x] = deger
                    grid = [s for s in grid if 0 in s]
                    while len(grid) < yukseklik: grid.insert(0, [0]*genislik)
                    durum["px"], durum["py"], durum["parca"] = 3, 0, random.choice(sekiller)
                    if carpisma_var_mi(grid, durum["parca"], durum["px"], durum["py"]): durum["oyun_devam"] = False
            time.sleep(0.05)
    except: pass
    print("Tetris Bitti!")

# --- YILAN OYUNU ---
def yilan_oyunu():
    ekran_temizle()
    screen = turtle.Screen()
    screen.title("YILAN OYUNU")
    screen.setup(width=700, height=700)
    screen.tracer(0)
    screen.bgcolor("#1d1d1d")

    # Çerçeve Çizimi
    border = turtle.Turtle()
    border.speed(0)
    border.pensize(4)
    border.penup()
    border.goto(-310, 250)
    border.pendown()
    border.color("red")
    for _ in range(2):
        border.forward(600)
        border.right(90)
        border.forward(500)
        border.right(90)
    border.hideturtle()

    score = 0
    delay = 0.1
    game_running = True

    snake = turtle.Turtle("square")
    snake.color("green")
    snake.penup()
    snake.goto(0,0)
    snake.direction = 'stop'

    fruit = turtle.Turtle("square")
    fruit.color("white")
    fruit.penup()
    fruit.goto(30,30)

    old_fruit = []

    scoring = turtle.Turtle()
    scoring.color("white")
    scoring.penup()
    scoring.hideturtle()
    scoring.goto(0, 260)
    scoring.write("Score: 0", align="center", font=("Courier", 24, "bold"))

    def go_up():
        if snake.direction != "down": snake.direction = "up"
    def go_down():
        if snake.direction != "up": snake.direction = "down"
    def go_left():
        if snake.direction != "right": snake.direction = "left"
    def go_right():
        if snake.direction != "left": snake.direction = "right"

    screen.listen()
    screen.onkeypress(go_up, "Up")
    screen.onkeypress(go_down, "Down")
    screen.onkeypress(go_left, "Left")
    screen.onkeypress(go_right, "Right")

    try:
        while game_running:
            screen.update()

            if snake.distance(fruit) < 20:
                fruit.goto(random.randint(-290, 270), random.randint(-240, 240))
                score += 1
                scoring.clear()
                scoring.write("Score: {}".format(score), align="center", font=("Courier", 24, "bold"))
                delay = max(0.05, delay - 0.002)
                
                new_segment = turtle.Turtle("square")
                new_segment.color("red")
                new_segment.penup()
                old_fruit.append(new_segment)

            for index in range(len(old_fruit)-1, 0, -1):
                old_fruit[index].goto(old_fruit[index-1].pos())

            if len(old_fruit) > 0:
                old_fruit[0].goto(snake.pos())

            if snake.direction == "up": snake.sety(snake.ycor() + 20)
            if snake.direction == "down": snake.sety(snake.ycor() - 20)
            if snake.direction == "left": snake.setx(snake.xcor() - 20)
            if snake.direction == "right": snake.setx(snake.xcor() + 20)

            # Çarpışma Kontrolleri
            if snake.xcor() > 280 or snake.xcor() < -300 or snake.ycor() > 240 or snake.ycor() < -240:
                game_running = False

            for segment in old_fruit:
                if segment.distance(snake) < 20:
                    game_running = False

            time.sleep(delay)
        
        scoring.goto(0, 0)
        scoring.write("GAME OVER\nScore: {}".format(score), align="center", font=("Courier", 30, "bold"))
        screen.update()
        time.sleep(2)
    except: pass
    print("Yılan Oyunu Bitti!")

# --- UÇAK OYUNU ---
def ucak_oyunu():
    turtle.resetscreen()
    win = turtle.Screen()
    win.title("Klasik Uçak Savaşı")
    win.bgcolor("navy") # Gökyüzü rengi
    win.setup(width=600, height=800)
    win.tracer(0)

    # 1. BİZİM UÇAĞIMIZ
    player = turtle.Turtle()
    player.shape("triangle") # Basit uçak şekli
    player.color("white")
    player.penup()
    player.setheading(90) # Yukarı baksın
    player.goto(0, -350)

    # 2. ATEŞ SİSTEMİ (Mermiler)
    bullets = []
    def ates_et():
        bullet = turtle.Turtle()
        bullet.shape("square")
        bullet.color("yellow")
        bullet.shapesize(0.5, 0.2)
        bullet.penup()
        bullet.speed(0)
        bullet.goto(player.xcor(), player.ycor() + 20)
        bullets.append(bullet)

    # 3. DÜŞMAN UÇAKLARI
    enemies = []
    for _ in range(5): # Ekranda aynı anda 5 düşman olsun
        enemy = turtle.Turtle()
        enemy.shape("triangle")
        enemy.color("red")
        enemy.penup()
        enemy.setheading(270) # Aşağı baksın
        enemy.goto(random.randint(-280, 280), random.randint(200, 400))
        enemies.append(enemy)

    # Hareketler
    def sola(): 
        if player.xcor() > -280: player.setx(player.xcor() - 20)
    def saga(): 
        if player.xcor() < 280: player.setx(player.xcor() + 20)

    win.listen()
    win.onkeypress(sola, "Left")
    win.onkeypress(saga, "Right")
    win.onkeypress(ates_et, "space") # Boşlukla ateş et

    # OYUN DÖNGÜSÜ
    score = 0
    running = True
    while running:
        try:
            win.update()
            time.sleep(0.10)

            # Mermileri hareket ettir
            for bullet in bullets[:]:
                bullet.sety(bullet.ycor() + 15)
                if bullet.ycor() > 400: # Ekrandan çıktıysa sil
                    bullet.hideturtle()
                    bullets.remove(bullet)

            # Düşmanları hareket ettir ve Çarpışma Kontrolü
            for enemy in enemies:
                enemy.sety(enemy.ycor() - 5) # Düşman hızı
                
                # Düşman en alta indiyse başa dönsün
                if enemy.ycor() < -400:
                    enemy.goto(random.randint(-280, 280), random.randint(200, 400))

                # Mermi düşmanı vurdu mu?
                for bullet in bullets[:]:
                    if bullet.distance(enemy) < 25:
                        score += 10
                        enemy.goto(random.randint(-280, 280), random.randint(200, 400))
                        bullet.hideturtle()
                        if bullet in bullets: bullets.remove(bullet)
                        #print(f"Puan: {score}")

                # Düşman bize çarptı mı?
                if enemy.distance(player) < 30:
                    print("EYVAH! VURULDUN!")
                    running = False

        except:
            break

    print(f"Oyun Bitti! Toplam Puanın: {score}")
    win.clear()


def calistir():
    while True:
        print("-"*30)
        print("╔═══════════════════════╗")
        print("║                       ║")
        print("║        OYUNLAR        ║")
        print("║                       ║")
        print("║  1-Tetris             ║")
        print("║  2-Yılan              ║")
        print("║  3-Savaş Uçağı        ║")
        print("║                       ║")
        print("║  0-Çıkış              ║")
        print("║                       ║")
        print("║    Seçiminiz nedir?   ║")
        print("╚═══════════════════════╝")

        try:
            secim = input("Lütfen bir oyun seçiniz: ")
            if secim == "1": 
                print("Tetris oyununu seçtiniz. Tuşlar: Yön tuşları + hızlı indirmek için space tuşu.")
                tetris_oyunu()
            elif secim == "2": 
                print("Yılan oyununu seçtiniz. Tuşlar: Yön tuşları.")
                yilan_oyunu()
            elif secim == "3":
                print("Savaş uçağı oyununu seçtiniz. Tuşlar: Yön tuşları + ateş etmek için space tuşu.")
                ucak_oyunu()
            elif secim == "0":
                print("Ana menüye yönlendiriliyorsunuz...")
                break
            else:
                print("Lütfen menüdeki oyunlardan birini seçiniz")
        except ValueError:
            print("Geçersiz seçim yaptınız.")    

if __name__ == "__main__":
    calistir()