import cv2
import pyautogui
import time
import numpy as np
import tensorflow as tf
from cvzone.HandTrackingModule import HandDetector

# PyAutoGUI güvenlik önlemi
pyautogui.FAILSAFE = False

# 1. Eğitilmiş TensorFlow Modelini Yükle
model = tf.keras.models.load_model('el_hareketleri_modeli.h5')

# Kamerayı ve El Dedektörünü Başlat
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Durum Değişkenleri
is_presentation_mode = False
last_action_time = 0
COOLDOWN_DELAY = 3.0

# Etiketlerin İsim Karşılıkları
LABEL_NAMES = {
    0: "Yumruk (ESC)",
    1: "Sonraki / Asagi",
    2: "Onceki / Yukari",
    3: "Kapat (Alt+F4)",
    4: "Ac (Enter)",
    5: "Tam Ekran Yap"
}

print("--- TensorFlow Destekli PowerPoint Kontrolü Başlatıldı ---")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    hands, img = detector.findHands(frame)
    
    gesture_text = "Notr"
    current_time = time.time()

    time_diff = current_time - last_action_time
    if time_diff < COOLDOWN_DELAY:
        remaining_time = round(COOLDOWN_DELAY - time_diff, 1)
        gesture_text = f"Bekleniyor... ({remaining_time}s)"
    else:
        if hands:
            lm_list = hands[0]['lmList']
            
            # Koordinatları Hazırla ve Normalize Et
            base_x, base_y = lm_list[0][0], lm_list[0][1]
            input_data = []
            for lm in lm_list:
                input_data.append(lm[0] - base_x)
                input_data.append(lm[1] - base_y)
                
            input_array = np.array([input_data])

            # TensorFlow ile Tahmin Yap
            predictions = model.predict(input_array, verbose=0)
            class_id = np.argmax(predictions[0])
            confidence = predictions[0][class_id]

            # Güven oranı %80 üzerindeyse aksiyon al
            if confidence > 0.8:
                
                # 0: Yumruk -> Sunumdan Çık (ESC)
                if class_id == 0:
                    if is_presentation_mode:
                        pyautogui.press('esc')
                        is_presentation_mode = False
                        gesture_text = "Tam Ekrandan Cikildi"
                        last_action_time = time.time()
                    else:
                        gesture_text = "Zaten Normal Mod"

                # 1: İşaret Parmağı -> Sonraki Slayt / Aşağı
                elif class_id == 1:
                    pyautogui.press('right')
                    pyautogui.press('down')
                    gesture_text = "Sonraki / Asagi"
                    last_action_time = time.time()

                # 2: İşaret + Orta -> Önceki Slayt / Yukarı
                elif class_id == 2:
                    pyautogui.press('left')
                    pyautogui.press('up')
                    gesture_text = "Onceki / Yukari"
                    last_action_time = time.time()

                # 3: 3 Parmak -> Kapat (Alt + F4)
                elif class_id == 3:
                    pyautogui.hotkey('alt', 'f4')
                    is_presentation_mode = False
                    gesture_text = "Kapat (Alt + F4)"
                    last_action_time = time.time()

                # 4: Serçe Parmak -> Aç (Enter)
                elif class_id == 4:
                    pyautogui.hotkey('enter')
                    gesture_text = "Dosya / Slayt Acildi (Enter)"
                    last_action_time = time.time()

                # 5: Açık El -> Tam Ekran Yap (Shift + F5)
                elif class_id == 5:
                    if not is_presentation_mode:
                        pyautogui.hotkey('shift', 'f5')
                        is_presentation_mode = True
                        gesture_text = "TAM EKRAN YAPILDI"
                        last_action_time = time.time()
                    else:
                        gesture_text = "Zaten Tam Ekran"

    # Ekranda durumu ve TensorFlow tahminini göster
    color = (0, 255, 0) if is_presentation_mode else (255, 255, 0)
    mode_status = "TAM EKRAN" if is_presentation_mode else "NORMAL"
    
    cv2.putText(frame, f"Mod: {mode_status}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(frame, f"TF Tahmin: {gesture_text}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('PowerPoint TensorFlow Kontrolu', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()