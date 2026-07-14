import sys
import os
from narwhals import col
import pandas as pd
import numpy as np
import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, 
    QMessageBox, QCheckBox, QInputDialog, QListWidget, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QDragEnterEvent, QDropEvent
from sklearn.impute import KNNImputer
from tomlkit import datetime


class DragDropLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__("Dosyayı Sürükle ve Bırak\n(.csv, .xlsx, .json)", parent)
        self.parent_win = parent
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            border: 2px dashed #aaaaaa;
            border-radius: 8px;
            padding: 15px;
            background-color: #f9f9f9;
            font-size: 13px;
            color: #555555;
        """)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                border: 2px dashed #0078d7;
                border-radius: 8px;
                padding: 15px;
                background-color: #e1f5fe;
                font-size: 13px;
                color: #0078d7;
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            border: 2px dashed #aaaaaa;
            border-radius: 8px;
            padding: 15px;
            background-color: #f9f9f9;
            font-size: 13px;
            color: #555555;
        """)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.parent_win.load_file(file_path)


class PreprocessingWizard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ÇKKV Karar Destek Sistemi - Akıllı Ön İşleme Sihirbazı")
        self.setGeometry(100, 100, 1150, 750)
        
        self.df = None
        self.headers = []
        self.has_issues = False
        
        # Hataları artık doğrudan DataFrame indekslerine bağlamak yerine dinamik listeliyoruz.
        self.structural_bad_lines = {}  # {orijinal_hatali_satir_metni_sirasi: ham_string}
        self.cell_issue_rows = set()    # {df_index_no}
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title = QLabel("Adım 1: Veri Yükleme, Hata Kurtarma ve Akıllı Ön İşleme")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 5px;")
        main_layout.addWidget(title)

        self.lbl_info = QLabel("Sistem durumu: Dosya bekleniyor...")
        self.lbl_info.setStyleSheet("color: #666666; font-style: italic; margin-bottom: 10px;")
        main_layout.addWidget(self.lbl_info)

        self.drop_area = DragDropLabel(self)
        main_layout.addWidget(self.drop_area)

        self.btn_select_file = QPushButton("Manuel Dosya Seç...")
        self.btn_select_file.clicked.connect(self.select_file_dialog)
        main_layout.addWidget(self.btn_select_file)

        tables_layout = QHBoxLayout()

        self.group_bad_lines = QGroupBox("Onarılması Gereken Sorunlu Satırlar")
        bad_layout = QVBoxLayout(self.group_bad_lines)
        
        self.list_bad_lines = QListWidget()
        bad_layout.addWidget(self.list_bad_lines)

        bad_buttons_layout = QHBoxLayout()
        self.btn_fix_manually = QPushButton("Düzenle")
        self.btn_fix_manually.clicked.connect(self.fix_line_manually)
        self.btn_fix_manually.setEnabled(False)
        bad_buttons_layout.addWidget(self.btn_fix_manually)

        self.btn_fix_ai = QPushButton("AI ile Onar")
        self.btn_fix_ai.clicked.connect(self.fix_line_with_ai)
        self.btn_fix_ai.setEnabled(False)
        bad_buttons_layout.addWidget(self.btn_fix_ai)

        self.btn_delete_bad_line = QPushButton("Satırı Sil")
        self.btn_delete_bad_line.clicked.connect(self.delete_bad_line)
        self.btn_delete_bad_line.setEnabled(False)
        bad_buttons_layout.addWidget(self.btn_delete_bad_line)

        bad_layout.addLayout(bad_buttons_layout)
        tables_layout.addWidget(self.group_bad_lines, 4)

        self.group_main_table = QGroupBox("Veri Seti Önizleme (Düzenlenebilir)")
        main_table_layout = QVBoxLayout(self.group_main_table)
        self.table = QTableWidget()
        self.table.itemChanged.connect(self.on_cell_edited)
        main_table_layout.addWidget(self.table)
        
        self.btn_delete_column = QPushButton("Seçili Sütunu Tamamen Sil 🗑️")
        self.btn_delete_column.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.btn_delete_column.clicked.connect(self.delete_selected_column)
        self.btn_delete_column.setEnabled(False)
        main_table_layout.addWidget(self.btn_delete_column)
        
        tables_layout.addWidget(self.group_main_table, 6)

        main_layout.addLayout(tables_layout)

        self.action_layout = QHBoxLayout()
        self.btn_knn_fill = QPushButton("Hücre Boşluklarını AI / KNN ile Doldur")
        self.btn_knn_fill.clicked.connect(self.apply_knn_imputation)
        self.btn_knn_fill.setEnabled(False)
        self.action_layout.addWidget(self.btn_knn_fill)

        self.btn_drop_nan = QPushButton("Boş Hücreli Satırları Sil")
        self.btn_drop_nan.clicked.connect(self.apply_drop_nan)
        self.btn_drop_nan.setEnabled(False)
        self.action_layout.addWidget(self.btn_drop_nan)
        main_layout.addLayout(self.action_layout)

        self.footer_layout = QHBoxLayout()
        self.chk_ignore = QCheckBox("Hataları görmezden gel ve ÇKKV sayfasına geç (Tavsiye Edilmez)")
        self.chk_ignore.stateChanged.connect(self.toggle_navigation)
        self.footer_layout.addWidget(self.chk_ignore)

        self.btn_next = QPushButton("İleri (ÇKKV Sayfasına Geç) ➔")
        self.btn_next.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e0e0e0;")
        self.btn_next.setEnabled(False)
        self.btn_next.clicked.connect(self.go_to_mcdm_page)
        self.footer_layout.addWidget(self.btn_next)

        main_layout.addLayout(self.footer_layout)

    def select_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Veri Dosyası Seç", "", "Veri Dosyaları (*.csv *.xlsx *.json)"
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        self.structural_bad_lines = {}
        self.cell_issue_rows = set()
        self.list_bad_lines.clear()
        
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.csv':
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                if not lines:
                    raise ValueError("Seçilen dosya boş!")
                
                self.headers = [h.strip() for h in lines[0].split(',')]
                expected_cols = len(self.headers)
                
                all_rows = []
                structural_counter = 0
                for idx, line in enumerate(lines[1:], start=0):
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) == expected_cols:
                        all_rows.append(parts)
                    else:
                        # Bozuk satırlar için placeholder (NaN) ekliyoruz
                        all_rows.append([np.nan] * expected_cols)
                        self.structural_bad_lines[idx] = line.strip()
                
                self.df = pd.DataFrame(all_rows, columns=self.headers)
                
            elif ext in ['.xlsx', '.xls']:
                # 1. Excel dosyasını oku
                self.df = pd.read_excel(file_path)

                # 2. Sütun başlıklarında (kolon isimlerinde) tarih varsa onları string'e çevir
                self.df.columns = [str(col).strip() for col in self.df.columns]

                # 3. DataFrame içindeki tüm hücreleri tara: 
                # Eğer hücre bir datetime veya Timestamp ise onu güvenli bir şekilde string'e dönüştür
                self.df = self.df.applymap(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if hasattr(x, 'strftime') and not pd.isnull(x) else x)
                
                self.df = pd.read_json(file_path)
                self.headers = list(self.df.columns)
            else:
                raise ValueError("Desteklenmeyen dosya formatı!")

            # Metin temizlik adımları
            text_cols = self.df.select_dtypes(include=['object']).columns
            for col in text_cols:
                self.df[col] = self.df[col].replace(r'^\s*$', np.nan, regex=True)
                self.df[col] = self.df[col].replace(['None', 'none', 'NaN', 'nan'], np.nan)             

            self.drop_area.setText(f"Yüklenen Dosya: {os.path.basename(file_path)}")
            self.analyze_and_populate_table()

        except Exception as e:
            QMessageBox.critical(self, "Kritik Dosya Hatası", f"Dosya işlenirken hata oluştu:\n{str(e)}")
            

    def get_actual_numeric_columns(self):
        if self.df is None or self.df.empty:
            return []
        numeric_cols = []
        for col in self.df.columns:
            non_null_vals = self.df[col].dropna()
            if len(non_null_vals) == 0:
                continue
            
            success_count = 0
            for val in non_null_vals:
                try:
                    float(val)
                    success_count += 1
                except (ValueError, TypeError):
                    pass
            
            if (success_count / len(non_null_vals)) >= 0.6:
                numeric_cols.append(col)
        return numeric_cols

    def analyze_and_populate_table(self):
        if self.df is None:
            return

        # Sinyalleri engelliyoruz ki hücre doldurma sırasında döngüye girmeyelim
        self.table.blockSignals(True)
        self.table.setRowCount(self.df.shape[0])
        self.table.setColumnCount(self.df.shape[1])
        self.table.setHorizontalHeaderLabels(list(self.df.columns))

        self.cell_issue_rows.clear()
        actual_numeric_cols = self.get_actual_numeric_columns()

        # Sayısal sütun dönüşümleri
        for col in actual_numeric_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        for row_idx in range(self.df.shape[0]):
            row_has_error = False
            for col_idx in range(self.df.shape[1]):
                col_name = self.df.columns[col_idx]
                val = self.df.iat[row_idx, col_idx]
                
                is_nan = pd.isnull(val) or str(val).strip().lower() in ["nan", "", "none"]
                is_invalid_format = False
                
                if col_name in actual_numeric_cols:
                    if not is_nan:
                        try:
                            float(val)
                        except (ValueError, TypeError):
                            is_invalid_format = True

                item = QTableWidgetItem(str(val) if not is_nan else "")
                
                if is_nan or is_invalid_format:
                    item.setBackground(QColor(255, 204, 204))  # Açık Kırmızı/Pembe
                    row_has_error = True
                else:
                    item.setBackground(QColor(255, 255, 255))
                
                self.table.setItem(row_idx, col_idx, item)
            
            if row_has_error:
                # Eğer bu satır yapısal hata listesinde yoksa hücre hatasıdır
                if row_idx not in self.structural_bad_lines:
                    self.cell_issue_rows.add(row_idx)

        self.table.resizeColumnsToContents()
        self.table.blockSignals(False)

        self.update_bad_lines_list_view()

        # UI Durum Güncellemeleri
        self.has_issues = len(self.structural_bad_lines) > 0 or len(self.cell_issue_rows) > 0
        status_text = f"Veri Durumu: {self.df.shape[0]} Satır | {self.df.shape[1]} Sütun"
        
        self.btn_delete_column.setEnabled(self.df.shape[1] > 0)
        
        if self.has_issues:
            status_text += f" | ❌ {len(self.structural_bad_lines)} Yapısal | {len(self.cell_issue_rows)} Hücre Hatası!"
            self.btn_knn_fill.setEnabled(True)
            self.btn_drop_nan.setEnabled(True)
            self.btn_next.setEnabled(False)
            self.btn_next.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e0e0e0;")
        else:
            status_text += " | Temiz! ✓"
            self.btn_knn_fill.setEnabled(False)
            self.btn_drop_nan.setEnabled(False)
            self.btn_next.setEnabled(True)
            self.btn_next.setStyleSheet("font-weight: bold; padding: 10px; background-color: #4CAF50; color: white;")

        self.lbl_info.setText(status_text)

    def update_bad_lines_list_view(self):
        self.list_bad_lines.clear()
        
        # UI listesindeki indeksler ile DataFrame indekslerini eşleştirmek için bir harita tutacağız
        self.list_index_map = []  # Listedeki her bir satırın tipi ve gerçek df_idx karşılığı

        for df_idx in sorted(self.structural_bad_lines.keys()):
            raw_str = self.structural_bad_lines[df_idx]
            self.list_bad_lines.addItem(f"YAPISAL HATA (Satır {df_idx + 1}): {raw_str}")
            self.list_index_map.append(("structural", df_idx))
            
        for df_idx in sorted(self.cell_issue_rows):
            row_data = self.df.iloc[df_idx].tolist()
            row_preview = ", ".join([str(x) if pd.notnull(x) else "BOŞ" for x in row_data])
            self.list_bad_lines.addItem(f"HÜCRE HATASI (Satır {df_idx + 1}): {row_preview}")
            self.list_index_map.append(("cell", df_idx))

        has_any_error = len(self.list_index_map) > 0
        self.btn_fix_manually.setEnabled(has_any_error)
        self.btn_fix_ai.setEnabled(has_any_error)
        self.btn_delete_bad_line.setEnabled(has_any_error)

    def get_selected_row_details(self):
        current_row_idx = self.list_bad_lines.currentRow()
        if current_row_idx < 0 or current_row_idx >= len(self.list_index_map):
            return None, None
        return self.list_index_map[current_row_idx]

    def fix_line_manually(self):
        error_type, df_idx = self.get_selected_row_details()
        if df_idx is None:
            return
        
        if error_type == "structural":
            raw_str = self.structural_bad_lines[df_idx]
            text, ok = QInputDialog.getText(
                self, "Yapısal Satır Onarımı", 
                f"Beklenen Sütun Sayısı: {len(self.df.columns)}\nLütfen virgülle ayırarak girin:", 
                text=raw_str
            )
            if ok and text:
                parts = [p.strip() for p in text.split(',')]
                if len(parts) == len(self.df.columns):
                    self.df.iloc[df_idx] = parts
                    del self.structural_bad_lines[df_idx]
                    self.analyze_and_populate_table()
                else:
                    QMessageBox.warning(self, "Sütun Hatası", f"Beklenen: {len(self.df.columns)}, Girilen: {len(parts)}")
                    
        elif error_type == "cell":
            current_row_data = self.df.iloc[df_idx].tolist()
            raw_str = ", ".join([str(x) if pd.notnull(x) else "" for x in current_row_data])
            
            text, ok = QInputDialog.getText(
                self, "Hücre Hatası Onarımı", 
                f"Satır {df_idx + 1} Değerlerini Düzenleyin (Virgülle ayrılmış):", 
                text=raw_str
            )
            if ok and text:
                parts = [p.strip() for p in text.split(',')]
                if len(parts) == len(self.df.columns):
                    self.df.iloc[df_idx] = parts
                    self.analyze_and_populate_table()
                else:
                    QMessageBox.warning(self, "Sütun Hatası", f"Beklenen Sütun: {len(self.df.columns)}, Girilen: {len(parts)}")

    def fix_line_with_ai(self):
        error_type, df_idx = self.get_selected_row_details()
        if df_idx is None:
            return
        
        num_cols = len(self.df.columns)
        
        if error_type == "structural":
            raw_str = self.structural_bad_lines[df_idx]
            parts = [p.strip() for p in raw_str.split(',')]
            
            if len(parts) > num_cols:
                reconstructed = parts[:num_cols-1] + [" ".join(parts[num_cols-1:])]
            else:
                reconstructed = parts + [np.nan] * (num_cols - len(parts))
                
            suggested_str = ", ".join([str(x) for x in reconstructed])
            reply = QMessageBox.question(
                self, "AI Yapısal Onarım Önerisi", 
                f"AI satırı şu şekilde düzenledi:\n\n{suggested_str}\n\nTam olarak yerine yazalım mı?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.df.iloc[df_idx] = reconstructed
                del self.structural_bad_lines[df_idx]
                self.analyze_and_populate_table()
                
        elif error_type == "cell":
            row_data = self.df.iloc[df_idx].copy()
            actual_numeric_cols = self.get_actual_numeric_columns()
            
            if len(actual_numeric_cols) > 0:
                try:
                    imputer = KNNImputer(n_neighbors=2)
                    temp_filled = pd.DataFrame(imputer.fit_transform(self.df[actual_numeric_cols]), columns=actual_numeric_cols)
                    for col in actual_numeric_cols:
                        if pd.isnull(row_data[col]):
                            row_data[col] = temp_filled.iat[df_idx, self.df[actual_numeric_cols].columns.get_loc(col)]
                    
                    suggested_str = ", ".join([str(x) if pd.notnull(x) else "BOŞ" for x in row_data])
                    reply = QMessageBox.question(
                        self, "AI Hücre Onarım Önerisi", 
                        f"AI eksik alanları tahmin ederek satırı güncelledi:\n\n{suggested_str}\n\nOnaylıyor musunuz?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        self.df.iloc[df_idx] = row_data
                        self.analyze_and_populate_table()
                except Exception as e:
                    QMessageBox.warning(self, "AI Doldurma Başarısız", f"AI otomatik dolduramadı: {str(e)}")
            else:
                QMessageBox.information(self, "AI Bilgi", "Sayısal boşluk bulunamadı veya tahmin yapılamıyor.")

    def delete_bad_line(self):
        error_type, df_idx = self.get_selected_row_details()
        if df_idx is None:
            return
            
        reply = QMessageBox.question(
            self, "Emin misiniz?", 
            "Bu satırı tamamen silmek istediğinize emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Satır silinmeden önce yapısal hatalardan (varsa) çıkarıyoruz
            if error_type == "structural":
                if df_idx in self.structural_bad_lines:
                    del self.structural_bad_lines[df_idx]
            
            # Kaymayı engellemek için structural_bad_lines anahtarlarını yeniden düzenliyoruz
            new_structural = {}
            for k, v in self.structural_bad_lines.items():
                if k > df_idx:
                    new_structural[k - 1] = v
                else:
                    new_structural[k] = v
            self.structural_bad_lines = new_structural

            self.df = self.df.drop(self.df.index[df_idx]).reset_index(drop=True)
            self.analyze_and_populate_table()

    def delete_selected_column(self):
        current_col_idx = self.table.currentColumn()
        if current_col_idx < 0:
            QMessageBox.warning(self, "Seçim Yok", "Lütfen silmek istediğiniz sütunda herhangi bir hücreye tıklayın.")
            return
            
        col_name = self.df.columns[current_col_idx]
        
        reply = QMessageBox.question(
            self, "Sütun Silme Onayı", 
            f"'{col_name}' sütununu tamamen silmek istediğinize emin misiniz?\nBu işlem geri alınamaz!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.df = self.df.drop(columns=[col_name])
            self.headers = list(self.df.columns)
            QMessageBox.information(self, "Başarılı", f"'{col_name}' sütunu başarıyla silindi.")
            self.analyze_and_populate_table()

    def on_cell_edited(self, item):
        # Sinyalleri geçici olarak kapatıp sadece ilgili DataFrame hücresini güncelliyoruz
        self.table.blockSignals(True)
        row = item.row()
        col = item.column()
        val = item.text()
        
        if val.strip() == "":
            self.df.iat[row, col] = np.nan
            item.setBackground(QColor(255, 204, 204))  # Tekrar boş bırakıldıysa kırmızı yap
        else:
            self.df.iat[row, col] = val
            item.setBackground(QColor(255, 255, 255))  # Dolduysa beyaza çek
            
        # Tüm tabloyu yeniden çizmek yerine sadece hatanın giderilip giderilmediğini arka planda analiz ediyoruz
        self.table.blockSignals(False)
        
        # Arka plan durumunu güncelle ve hata listesini yenile
        self.recheck_errors_and_update_ui()

    def recheck_errors_and_update_ui(self):
        """Tüm tabloyu sıfırdan çizmeden sadece hata listelerini ve buton durumlarını günceller."""
        self.cell_issue_rows.clear()
        actual_numeric_cols = self.get_actual_numeric_columns()
        
        for row_idx in range(self.df.shape[0]):
            row_has_error = False
            for col_idx in range(self.df.shape[1]):
                col_name = self.df.columns[col_idx]
                val = self.df.iat[row_idx, col_idx]
                
                is_nan = pd.isnull(val) or str(val).strip().lower() in ["nan", "", "none"]
                is_invalid_format = False
                
                if col_name in actual_numeric_cols and not is_nan:
                    try:
                        float(val)
                    except ValueError:
                        is_invalid_format = True
                        
                if is_nan or is_invalid_format:
                    row_has_error = True
                    
            if row_has_error and row_idx not in self.structural_bad_lines:
                self.cell_issue_rows.add(row_idx)
                
        self.update_bad_lines_list_view()
        
        self.has_issues = len(self.structural_bad_lines) > 0 or len(self.cell_issue_rows) > 0
        status_text = f"Veri Durumu: {self.df.shape[0]} Satır | {self.df.shape[1]} Sütun"
        
        if self.has_issues:
            status_text += f" | ❌ {len(self.structural_bad_lines)} Yapısal | {len(self.cell_issue_rows)} Hücre Hatası!"
            self.btn_next.setEnabled(False)
            self.btn_next.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e0e0e0;")
        else:
            status_text += " | Temiz! ✓"
            self.btn_next.setEnabled(True)
            self.btn_next.setStyleSheet("font-weight: bold; padding: 10px; background-color: #4CAF50; color: white;")
            
        self.lbl_info.setText(status_text)

    def apply_knn_imputation(self):
        if self.df is None:
            return
        
        actual_numeric_cols = self.get_actual_numeric_columns()
        if len(actual_numeric_cols) == 0:
            QMessageBox.warning(self, "Hata", "Tahminleme için sayısal sütun tespit edilemedi.")
            return
            
        try:
            imputer = KNNImputer(n_neighbors=2)
            self.df[actual_numeric_cols] = imputer.fit_transform(self.df[actual_numeric_cols])
            QMessageBox.information(self, "Başarılı", "Boşluklar KNN algoritması ile tahmin edilerek dolduruldu.")
            self.analyze_and_populate_table()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"AI doldurma başarısız: {str(e)}")

    def apply_drop_nan(self):
        if self.df is None:
            return
        
        initial_len = len(self.df)
        self.df = self.df.dropna().reset_index(drop=True)
        self.structural_bad_lines.clear()
        dropped_count = initial_len - len(self.df)
        
        QMessageBox.information(self, "Başarılı", f"{dropped_count} adet boş hücreli satır başarıyla silindi.")
        self.analyze_and_populate_table()

    def toggle_navigation(self):
        if self.chk_ignore.isChecked():
            self.btn_next.setEnabled(True)
            self.btn_next.setStyleSheet("font-weight: bold; padding: 10px; background-color: #ff9800; color: white;")
        else:
            if self.has_issues:
                self.btn_next.setEnabled(False)
                self.btn_next.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e0e0e0;")
            else:
                self.btn_next.setEnabled(True)
                self.btn_next.setStyleSheet("font-weight: bold; padding: 10px; background-color: #4CAF50; color: white;")

    def go_to_mcdm_page(self):
        QMessageBox.information(self, "Hatalı veriler temizlendi. Şimdi ÇKKV sayfasına geçebilirsiniz!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PreprocessingWizard()
    window.show()
    sys.exit(app.exec())