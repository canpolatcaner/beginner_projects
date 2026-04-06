import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import msvcrt
import sys


current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(current_path)
KATEGORI_FILE = os.path.join(project_path, "kategoriler.json")
CURRENT_STOCK = os.path.join(project_path, "mevcut_stok.json")
REYON_STOCK_FILE = os.path.join(project_path, "reyon_stok.json")
SATIS_HAREKETLERI_FILE = os.path.join(project_path, "satis_hareketleri.json")

class analyse:
    def __init__(self):
        self.verileri_yukle()
        self.bugun = datetime.now()

    def verileri_yukle(self):
        def load(p):
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        self.stok = load(CURRENT_STOCK)
        self.reyon = load(REYON_STOCK_FILE)
        self.kategoriler = load(KATEGORI_FILE)
        self.satislar = load(SATIS_HAREKETLERI_FILE).get("satislar", [])

    def veri_hazirla(self, filtre_id=None):
        rapor_listesi = []
        df_satis = pd.DataFrame(self.satislar)
        
        # Filtreleme: Seçilen kategori/grup/ürün ile başlayan tüm ID'leri bulur
        hedef_id_listesi = [id for id in self.stok.keys() if not filtre_id or id.startswith(filtre_id)]

        for fid in hedef_id_listesi:
            p_list = self.stok[fid].get("partiler", [])
            h, a, y = 0, 0, 0
            if not df_satis.empty:
                u_satis = df_satis[df_satis['urun_id'] == fid].copy()
                if not u_satis.empty:
                    u_satis['satis_zamani'] = pd.to_datetime(u_satis['satis_zamani'])
                    h = u_satis[u_satis['satis_zamani'] >= (self.bugun - timedelta(days=7))]['miktar'].sum()
                    a = u_satis[u_satis['satis_zamani'] >= (self.bugun - timedelta(days=30))]['miktar'].sum()
                    y = u_satis[u_satis['satis_zamani'] >= (self.bugun - timedelta(days=365))]['miktar'].sum()

            parts = fid.split('.')
            mat_ad = self.kategoriler.get("material", {}).get(parts[0], "??")
            grp_ad = self.kategoriler.get("group", {}).get(parts[0], {}).get(parts[1], "??")

            for parti in p_list:
                maliyet = parti.get("maliyet", 0)
                try:
                    stt = datetime.strptime(parti['stt'], "%d.%m.%Y")
                    kalan_gun = (stt - self.bugun).days
                except:
                    kalan_gun = 999
                
                rapor_listesi.append({
                    "Malzeme": mat_ad,
                    "Grup": grp_ad,
                    "Urun_Adi": self.stok[fid]["urun_ad"],
                    "ID": fid,
                    "Batch": parti["batch_id"],
                    "Maliyet": maliyet,
                    "Mevcut_Stok": parti["miktar_mevcut"],
                    "STT": parti["stt"],
                    "Haftalik_Satis": h,
                    "Aylik_Satis": a,
                    "Yillik_Satis": y
                })

        df = pd.DataFrame(rapor_listesi)
        if not df.empty:
            # Grup içi yüzde hesaplama
            df['Grup_Ici_Pay_%'] = (df['Yillik_Satis'] / df.groupby('Grup')['Yillik_Satis'].transform('sum') * 100).fillna(0)
        return df

    def dinamik_menu(self, opsiyonlar, baslik):
        idx = 0
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n" + "="*65)
            print(f" {baslik:^63} ")
            print("="*65)
            for i, opt in enumerate(opsiyonlar):
                if i == idx:
                    print(f" ==> \033[92m{opt:<55}\033[0m")
                else:
                    print(f"     {opt:<55}")
            print("="*65)
            print("(↑/↓: Gez | Enter: Seç | E: Excel Al | G: Grafik | ESC: Geri)")
            
            key = msvcrt.getch()
            if key == b'\x1b': return -1, "back"
            if key == b'\r': return idx, "select"
            if key.lower() == b'e': return idx, "excel"
            if key.lower() == b'g': return idx, "grafik"
            if key in (b'\x00', b'\xe0'):
                k2 = msvcrt.getch()
                if k2 == b'H': idx = (idx - 1) % len(opsiyonlar)
                elif k2 == b'P': idx = (idx + 1) % len(opsiyonlar)

    def rapor_islem(self, df, tip, isim):
        if df.empty:
            print("\n⚠️ Bu seçim için stok veya satış verisi bulunamadı!"); msvcrt.getch(); return
        if tip == "excel":
            fname = f"Rapor_{isim.replace(' ', '_')}.xlsx"
            df.to_excel(fname, index=False)
            print(f"\n✅ Excel dosyası oluşturuldu: {fname}"); msvcrt.getch()
        elif tip == "grafik":
            plt.figure(figsize=(10,6))
            top_df = df.groupby('Urun_Adi')['Yillik_Satis'].sum().nlargest(10).reset_index()
            sns.barplot(data=top_df, x="Yillik_Satis", y="Urun_Adi")
            plt.title(f"{isim} - En Çok Satan Ürünler (Yıllık)")
            plt.tight_layout(); plt.show()

    def boss(self):
        # 1. Material
        m_ids = sorted([k for k in self.kategoriler["material"].keys() if k.isdigit()])
        m_opts = [self.kategoriler["material"][k] for k in m_ids]
        m_idx, action = self.dinamik_menu(m_opts, "ANA KATEGORİ")
        if action == "back": return
        sel_m = m_ids[m_idx]
        if action in ["excel", "grafik"]:
            self.rapor_islem(self.veri_hazirla(sel_m), action, m_opts[m_idx]); return self.boss()

        # 2. Group
        g_data = self.kategoriler["group"].get(sel_m, {})
        g_ids = sorted([k for k in g_data.keys() if k.isdigit()])
        g_opts = [g_data[k] for k in g_ids]
        g_idx, action = self.dinamik_menu(g_opts, f"{m_opts[m_idx]} > GRUP")
        if action == "back": return self.boss()
        sel_g = g_ids[g_idx]
        if action in ["excel", "grafik"]:
            self.rapor_islem(self.veri_hazirla(f"{sel_m}.{sel_g}"), action, g_opts[g_idx]); return self.boss()

        
        p_data = self.kategoriler["product"].get(sel_m, {}).get(sel_g, {})
        p_ids = sorted([k for k in p_data.keys() if k.isdigit()])
        p_opts = [p_data[k]["ad"] for k in p_ids]
        p_idx, action = self.dinamik_menu(p_opts, f"{g_opts[g_idx]} > ÜRÜN TÜRÜ")
        if action == "back": return self.boss()
        sel_p = p_ids[p_idx]
        if action in ["excel", "grafik"]:
            self.rapor_islem(self.veri_hazirla(f"{sel_m}.{sel_g}.{sel_p}"), action, p_opts[p_idx]); return self.boss()

        # 4. Marka / SKU
        final_ids = sorted([id for id in self.stok.keys() if id.startswith(f"{sel_m}.{sel_g}.{sel_p}.")])
        f_opts = [self.stok[id]['urun_ad'] for id in final_ids]
        f_idx, action = self.dinamik_menu(f_opts, "MARKA SEÇİMİ / TEKİL ANALİZ")
        if action == "back": return self.boss()
        self.rapor_islem(self.veri_hazirla(final_ids[f_idx]), "excel" if action=="select" else action, f_opts[f_idx])
        return self.boss()

if __name__ == "__main__":
    app = analyse()
    app.boss()