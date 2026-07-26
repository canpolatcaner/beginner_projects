import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # TensorFlow loglarını gizler
os.environ['GLOG_minloglevel'] = '3'

import cv2
import csv
import time
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=1)

# CSV dosyasını oluştur
header = ['label'] + [f'pt_{i}_x' for i in range(21)] + [f'pt_{i}_y' for i in range(21)]
with open('el_verileri.csv', mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)

print("--- VERİ TOPLAMA BAŞLATILDI ---")
print("Klavyeden tuşlara basarak veri kaydedin:")
print("0: Yumruk (Çıkış/ESC)")
print("1: Sadece İşaret (Sonraki)")
print("2: İşaret+Orta (Önceki)")
print("3: 3 Parmak (Kapat)")
print("4: Serçe Parmak (Aç)")
print("5: Açık El (Tam Ekran)")
print("Çıkış için 'q' tuşuna basın.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    hands, img = detector.findHands(frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    # 0-5 arası bir tuşa basılırsa ekrandaki el koordinatlarını CSV'ye yaz
    if hands and chr(key) in ['0', '1', '2', '3', '4', '5']:
        label = int(chr(key))
        lm_list = hands[0]['lmList']
        
        # Koordinatları normalize et (El ekranın neresinde olursa olsun sabit çalışması için)
        base_x, base_y = lm_list[0][0], lm_list[0][1]
        row = [label]
        for lm in lm_list:
            row.append(lm[0] - base_x)
            row.append(lm[1] - base_y)

        with open('el_verileri.csv', mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
            
        print(f"Sınıf {label} için 1 örnek kaydedildi!")

    cv2.imshow("Veri Toplama", frame)

cap.release()
cv2.destroyAllWindows()