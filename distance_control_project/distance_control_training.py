import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split

# 1. Veriyi Oku
data = pd.read_csv('el_verileri.csv')
X = data.drop('label', axis=1).values
y = data['label'].values

# Verileri Eğitim ve Test olarak ayır
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. TensorFlow Model Mimarısı Oluştur
model = models.Sequential([
    layers.Input(shape=(42,)),              # 21 nokta x 2 koordinat (x,y)
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(32, activation='relu'),
    layers.Dense(6, activation='softmax')   # 6 farklı sınıf (0,1,2,3,4,5)
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 3. Eğitimi Başlat
print("TensorFlow Modeli Eğitiliyor...")
model.fit(X_train, y_train, epochs=50, batch_size=16, validation_data=(X_test, y_test))

# 4. Modeli Kaydet
model.save('el_hareketleri_modeli.h5')
print("Model Başarıyla Kaydedildi: el_hareketleri_modeli.h5")