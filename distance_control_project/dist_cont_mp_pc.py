import cv2
import pyautogui
import time
from cvzone.HandTrackingModule import HandDetector

# PyAutoGUI güvenlik önlemi
pyautogui.FAILSAFE = False

# Kamerayı Başlat
cap = cv2.VideoCapture(0)

# El Dedektörü (Güven oranı: 0.8, Max El: 1)
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Durum Değişkenleri
is_presentation_mode = False
last_action_time = 0
COOLDOWN_DELAY = 3.0

print("--- PowerPoint El Kontrolü Başlatıldı (Katı Cooldown) ---")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    
    # Elleri tespit et ve çiz
    hands, img = detector.findHands(frame)
    
    gesture_text = "Notr"
    current_time = time.time()

    # Cooldown kontrolü (Eğer 3 saniye geçmediyse el hareketlerini tamamen yok say)
    time_diff = current_time - last_action_time
    if time_diff < COOLDOWN_DELAY:
        remaining_time = round(COOLDOWN_DELAY - time_diff, 1)
        gesture_text = f"Bekleniyor... ({remaining_time}s)"
    else:
        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            open_count = sum(fingers)
            
            # 1. Tüm Parmaklar Açık -> YALNIZCA Sunum Modunda DEĞİLSEK Tam Ekran Yap
            if open_count == 5:
                if not is_presentation_mode:
                    pyautogui.hotkey('shift', 'f5')
                    is_presentation_mode = True
                    gesture_text = "TAM EKRAN YAPILDI"
                    last_action_time = time.time()  # Süreyi sıfırla
                else:
                    gesture_text = "Zaten Tam Ekran"

            # 2. Yumruk -> Sunumdan Çık
            elif open_count == 0:
                if is_presentation_mode:
                    pyautogui.press('esc')
                    is_presentation_mode = False
                    gesture_text = "Tam Ekrandan Cikildi"
                    last_action_time = time.time()  # Süreyi sıfırla
                else:
                    gesture_text = "Zaten Normal Mod"

            # 3. Sonraki Slayt / Aşağı
            elif fingers == [0, 1, 0, 0, 0] or fingers == [1, 1, 0, 0, 0]:
                pyautogui.press('right')
                pyautogui.press('down')
                gesture_text = "Sonraki / Asagi"
                last_action_time = time.time()  # Süreyi sıfırla

            # 4. Önceki Slayt / Yukarı
            elif fingers == [0, 1, 1, 0, 0]:
                pyautogui.press('left')
                pyautogui.press('up')
                gesture_text = "Onceki / Yukari"
                last_action_time = time.time()  # Süreyi sıfırla

            # 5. Kapat (Alt + F4)
            elif fingers == [0, 1, 1, 1, 0]:
                pyautogui.hotkey('alt', 'f4')
                is_presentation_mode = False
                gesture_text = "Kapat (Alt + F4)"
                last_action_time = time.time()  # Süreyi sıfırla

            # 6. Aç (Alt + F4)
            elif fingers == [0, 0, 0, 0, 1]:
                pyautogui.hotkey('enter')
                gesture_text = "Dosya / Slayt Acildi (Enter)"
                last_action_time = time.time()  # Süreyi sıfırla

    # Ekranda durumu göster
    color = (0, 255, 0) if is_presentation_mode else (255, 255, 0)
    mode_status = "TAM EKRAN" if is_presentation_mode else "NORMAL"
    
    cv2.putText(frame, f"Mod: {mode_status}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(frame, f"Hareket: {gesture_text}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('PowerPoint El Kontrolu', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()