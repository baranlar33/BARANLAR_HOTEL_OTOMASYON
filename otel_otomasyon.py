import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import os
import base64

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="BARANLAR HOTEL | MODERN MANAGEMENT", layout="wide", initial_sidebar_state="expanded")

# --- TÜRKÇE BÜYÜK HARF ÇEVİRİCİ FONKSİYON ---
def buyuk_harf_turkce(metin):
    if not metin or pd.isna(metin): return ""
    metin = str(metin).replace('i', 'İ').replace('ı', 'I').replace('ş', 'Ş').replace('ç', 'Ç').replace('ğ', 'Ğ').replace('ü', 'Ü').replace('ö', 'Ö')
    return metin.upper().strip()

# --- GECE SAYISI HESAPLAMA FONKSİYONU ---
def gece_sayisi_hesapla(giris_tarihi_str):
    try:
        giris_tarihi = datetime.strptime(giris_tarihi_str, "%Y-%m-%d").date()
        bugun = datetime.now().date()
        gece = (bugun - giris_tarihi).days
        return max(1, gece) 
    except:
        return 1

# --- CSS TASARIMI (BEYAZ TEMA VE TAM SARAN PARLAK ÇİZGİLER) ---
st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #f1f5f9 !important;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
            max-width: 96% !important;
        }
        .header-banner {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 15px 25px;
            border-radius: 12px;
            color: #0f172a;
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            border: 2px solid #e2e8f0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        }
        .header-logo {
            width: 55px; height: 55px;
            background: white;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            margin-right: 15px;
            border: 2px solid #b45309;
            overflow: hidden;
        }
        .metric-card {
            background: white;
            border-radius: 10px;
            padding: 12px;
            text-align: center;
            border: 2px solid #e2e8f0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        }
        div[data-testid="stForm"] {
            max-width: 800px !important;
            margin: 0 auto !important;
            background: white !important;
            padding: 20px 25px !important;
            border-radius: 12px !important;
            border: 2px solid #cbd5e1 !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04) !important;
        }
        .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stDateInput input {
            border-radius: 8px !important;
            border: 1px solid #cbd5e1 !important;
            padding: 6px 10px !important;
            font-size: 14px !important;
            background-color: #f8fafc !important;
            height: 38px !important;
        }
        div[data-testid="stForm"] button {
            background: linear-gradient(90deg, #0f172a 0%, #1e3a8a 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 8px !important;
            height: 40px !important;
        }
        .room-box {
            border-radius: 10px;
            padding: 12px;
            height: 95px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
            margin-bottom: 12px;
        }
        .room-dolu { background: #ffffff !important; border: 3px solid #ef4444 !important; box-shadow: 0 0 8px rgba(239, 68, 68, 0.2); }
        .room-bos { background: #ffffff !important; border: 3px solid #10b981 !important; box-shadow: 0 0 8px rgba(16, 185, 129, 0.2); }
        .room-kirli { background: #ffffff !important; border: 3px solid #f59e0b !important; box-shadow: 0 0 8px rgba(245, 158, 11, 0.2); }
        .room-tadilat { background: #ffffff !important; border: 3px solid #6366f1 !important; box-shadow: 0 0 8px rgba(99, 102, 241, 0.2); }
        
        [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 2px solid #e2e8f0; }
        [data-testid="stSidebar"] button {
            color: #334155 !important;
            background-color: #f8fafc !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            margin-bottom: 5px !important;
        }
        [data-testid="stSidebar"] button:hover { background-color: #e2e8f0 !important; color: #0f172a !important; }
    </style>
""", unsafe_allow_html=True)

# --- BASE64 LOGO GÖRÜNTÜLEME ---
def get_logo_html():
    logo_adlari = ["logo.png.jpg", "logo.png", "logo.jpg"]
    for b_ad in logo_adlari:
        if os.path.exists(b_ad):
            with open(b_ad, "rb") as f:
                data = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{data}" style="width:100%; height:100%; object-fit:cover;">'
    return '<span style="font-size:20px; font-weight:bold; color:#b45309;">B</span>'

# --- VERİ TABANI AYARLARI ---
DB_NAME = "baranlar_otel.db"
def veri_tabani_kur():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS Tbl_Odalar (OdaNo TEXT PRIMARY KEY, OdaTipi TEXT, Fiyat REAL, Durum TEXT DEFAULT "Boş")')
        cursor.execute('CREATE TABLE IF NOT EXISTS Tbl_Kasa (ID INTEGER PRIMARY KEY AUTOINCREMENT, IslemTipi TEXT, Kategori TEXT, Tutar REAL, OdemeYontemi TEXT, Aciklama TEXT, Tarih TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS Tbl_Hareketler (ID INTEGER PRIMARY KEY AUTOINCREMENT, OdaNo TEXT, MusteriAdSoyad TEXT, KimlikNo TEXT, Ulke TEXT, DogumTarihi TEXT, GirisTarihi TEXT, GirisSaati TEXT, CikisTarihi TEXT, ToplamTutar REAL, OdenenTutar REAL, KalanBorc REAL, Durum TEXT, GunlukFiyat REAL, AcikTarih INTEGER)')
        cursor.execute('CREATE TABLE IF NOT EXISTS Tbl_Personel (ID INTEGER PRIMARY KEY AUTOINCREMENT, AdSoyad TEXT, Gorev TEXT, CalismaTuru TEXT, GirisTarihi TEXT, CikisTarihi TEXT, NetMaas REAL, MaasGunu INTEGER)')
        cursor.execute('CREATE TABLE IF NOT EXISTS Tbl_PersonelHareketleri (ID INTEGER PRIMARY KEY AUTOINCREMENT, PersonelID INTEGER, IslemTuru TEXT, Tutar REAL, Aciklama TEXT, Tarih TEXT)')
        conn.commit()
veri_tabani_kur()

def db_sorgu(q, p=()):
    with sqlite3.connect(DB_NAME) as conn: return pd.read_sql_query(q, conn, params=p)
def db_komut(q, p=()):
    with sqlite3.connect(DB_NAME) as conn: cursor = conn.cursor(); cursor.execute(q, p); conn.commit()

# --- ODALARI İLK KURULUMDA OLUŞTURMA ---
try:
    if db_sorgu("SELECT COUNT(*) as c FROM Tbl_Odalar").iloc[0]['c'] == 0:
        odalar = [
            ("105", "Standart", 3000), ("107", "Standart", 1500), ("108", "Standart", 1500), ("109", "Standart", 2500), 
            ("201", "Standart", 1500), ("202", "Standart", 2500), ("203", "Standart", 2500), ("204", "Standart", 1500),
            ("205", "Standart", 3000), ("207", "Standart", 1500), ("208", "Standart", 1500), ("209", "Standart", 2500),
            ("301", "Standart", 1500), ("302", "Standart", 2500), ("303", "Standart", 2500), ("304", "Standart", 1500),
            ("305", "Standart", 3000), ("307", "Standart", 1500), ("308", "Standart", 1500), ("309", "Standart", 2500),
            ("401", "Standart", 1500), ("402", "Standart", 2500), ("403", "Standart", 2500), ("404", "Standart", 1500),
            ("405", "Standart", 2500), ("407", "Standart", 1500), ("408", "Standart", 1500), ("409", "Standart", 2500)
        ]
        for n, t, f in odalar: 
            db_komut("INSERT INTO Tbl_Odalar VALUES (?,?,?,'Boş')", (n, t, f))
except: 
    pass

# --- MENÜ NAVİGASYON ---
st.sidebar.markdown("<h2 style='color:#0f172a; text-align:center; font-size:16px; margin-bottom:20px; font-weight:800;'>💎 BARANLAR HOTEL</h2>", unsafe_allow_html=True)
menu = ["ODA DURUM PANELİ", "GİRİŞ / ÇIKIŞ İŞLEMLERİ", "TAHSİLAT & BORÇ TAKİBİ", "KASA YÖNETİMİ", "PERSONEL & MAAŞ"]
if 'sayfa' not in st.session_state: st.session_state.sayfa = menu[0]
for m in menu:
    if st.sidebar.button(m, use_container_width=True): st.session_state.sayfa = m; st.rerun()

# ==========================================
# SAYFA 1: ODA DURUM PANELİ
# ==========================================
if st.session_state.sayfa == "ODA DURUM PANELİ":
    st.markdown(f'<div class="header-banner"><div class="header-logo">{get_logo_html()}</div><div><h1 style="margin:0; font-size:24px; font-weight:800; color:#0f172a; letter-spacing:0.5px;">BARANLAR HOTEL | GÜNCEL ODALAR</h1><p style="margin:0; color:#64748b; font-weight:600; font-size:13px;">TÜM ODALAR TEK SAYFADA • DIJITAL PANEL GÖRÜNÜMÜ</p></div></div>', unsafe_allow_html=True)
    
    df_s = db_sorgu("SELECT Durum, COUNT(*) as c FROM Tbl_Odalar GROUP BY Durum")
    s_d = {"Dolu":0, "Boş":0, "Kirli":0, "Tadilat":0}
    for _,r in df_s.iterrows(): s_d[r['Durum']] = r['c']
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card" style="border-bottom: 4px solid #ef4444;"><div style="font-size:12px; color:#ef4444; font-weight:700;">🔴 DOLU ODALAR</div><div style="font-size:24px; font-weight:800; color:#0f172a;">{s_d["Dolu"]}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card" style="border-bottom: 4px solid #10b981;"><div style="font-size:12px; color:#10b981; font-weight:700;">🟢 BOŞ / MÜSAİT</div><div style="font-size:24px; font-weight:800; color:#0f172a;">{s_d["Boş"]}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card" style="border-bottom: 4px solid #f59e0b;"><div style="font-size:12px; color:#f59e0b; font-weight:700;">🟡 KİRLİ ODALAR</div><div style="font-size:24px; font-weight:800; color:#0f172a;">{s_d["Kirli"]}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card" style="border-bottom: 4px solid #6366f1;"><div style="font-size:12px; color:#6366f1; font-weight:700;">🛠️ ARIZA / BAKIM</div><div style="font-size:24px; font-weight:800; color:#0f172a;">{s_d["Tadilat"]}</div></div>', unsafe_allow_html=True)
    
    with st.expander("🛠️ Oda Durumunu Manuel Değiştir", expanded=False):
        with st.form("hizli_durum_form"):
            cc1, cc2 = st.columns(2)
            with cc1:
                tüm_odalar = db_sorgu("SELECT OdaNo FROM Tbl_Odalar ORDER BY OdaNo")
                secilen_oda = st.selectbox("Oda No", tüm_odalar['OdaNo'])
            with cc2:
                yeni_durum = st.selectbox("Yeni Durum", ["Boş", "Kirli", "Tadilat"], format_func=lambda x: "Temiz (Boş)" if x=="Boş" else x)
            if st.form_submit_button("🔄 Durumu Güncelle", use_container_width=True):
                db_komut("UPDATE Tbl_Odalar SET Durum=? WHERE OdaNo=?", (yeni_durum, secilen_oda))
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    df_o = db_sorgu("SELECT * FROM Tbl_Odalar ORDER BY OdaNo")
    
    cols = st.columns(7)
    for i, r in df_o.reset_index().iterrows():
        with cols[i % 7]:
            css_sinifi = "room-bos"
            ust_yazi = "BOŞ"
            alt_yazi = "MÜSAİT"
            
            if r['Durum'] == "Dolu":
                css_sinifi = "room-dolu"
                ust_yazi = "DOLU"
                # 🛠️ GÜNCELLEME: Sadece en son girilen AKTİF müşteriyi çek (Tarih ve ID sırasına göre en yeni olanı)
                h = db_sorgu("SELECT MusteriAdSoyad FROM Tbl_Hareketler WHERE OdaNo=? AND Durum='Aktif' ORDER BY ID DESC LIMIT 1", (r['OdaNo'],))
                alt_yazi = h.iloc[0]['MusteriAdSoyad'] if not h.empty else "DOLU"
            elif r['Durum'] == "Kirli":
                css_sinifi = "room-kirli"
                ust_yazi = "KİRLİ"
                alt_yazi = "TEMİZLİK BEKLİYOR"
            elif r['Durum'] == "Tadilat":
                css_sinifi = "room-tadilat"
                ust_yazi = "BAKIMDA"
                alt_yazi = "ARIZALI"
            
            st.markdown(f"""
                <div class="room-box {css_sinifi}">
                    <div>
                        <div style="font-size:11px; font-weight:800; color:#64748b;">{ust_yazi}</div>
                        <div style="font-size:18px; font-weight:800; color:#0f172a;">Oda {r['OdaNo']}</div>
                    </div>
                    <div style="font-size:12px; color:#334155; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                        {alt_yazi}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# ==========================================
# SAYFA 2: GİRİŞ / ÇIKIŞ İŞLEMLERİ
# ==========================================
elif st.session_state.sayfa == "GİRİŞ / ÇIKIŞ İŞLEMLERİ":
    t1, t2 = st.tabs(["📥 YENİ GİRİŞ (CHECK-IN)", "📤 ÇIKIŞ YAP (CHECK-OUT)"])
    
    with t1:
        df_b = db_sorgu("SELECT OdaNo, Fiyat FROM Tbl_Odalar WHERE Durum='Boş'")
        with st.form("modern_checkin_grid"):
            st.markdown("##### 📥 Müşteri Giriş Kaydı")
            
            c_in1, c_in2 = st.columns(2)
            with c_in1: o = st.selectbox("🚪 Oda Seçin", df_b['OdaNo'])
            with c_in2: acik_tarih = st.checkbox("❓ Çıkış Tarihi Belirsiz")
            
            c_in3, c_in4 = st.columns(2)
            with c_in3: ad = st.text_input("👤 Müşteri Adı Soyadı")
            with c_in4: tc = st.text_input("🆔 TC / Kimlik No")
            
            c_in5, c_in6 = st.columns(2)
            with c_in5: ulke = st.text_input("🌐 Ülke", value="Türkiye")
            with c_in6: DT = st.date_input("🎂 Doğum Tarihi", value=datetime(1990, 1, 1))
            
            c_in7, c_in8 = st.columns(2)
            with c_in7: gt = st.date_input("📅 Giriş Tarihi")
            with c_in8: gs = st.text_input("🕒 Giriş Saati", value=datetime.now().strftime("%H:%M"))
                
            c_in9, c_in10 = st.columns(2)
            with c_in9: ct = st.date_input("📅 Planlanan Çıkış Tarihi", value=datetime.now()+timedelta(days=1), disabled=acik_tarih)
            
            varsayilan_fiyat = float(df_b[df_b['OdaNo']==o]['Fiyat'].values[0]) if not df_b.empty else 1500.0
            with c_in10: gunluk_fiyat = st.number_input("💰 Günlük Oda Fiyatı (TL)", min_value=0.0, value=varsayilan_fiyat)
            
            c_in11, c_in12 = st.columns(2)
            with c_in11: pes = st.number_input("💵 Girişte Alınan Peşinat (TL)", min_value=0.0)
            with c_in12: yon = st.selectbox("💳 Ödeme Kanalı", ["Nakit", "Kredi Kartı", "Havale"])
                
            if st.form_submit_button("📥 Giriş Kaydını Tamamla", use_container_width=True):
                if not ad: st.error("Ad alanı boş geçilemez!")
                else:
                    ad, tc, ulke = buyuk_harf_turkce(ad), buyuk_harf_turkce(tc), buyuk_harf_turkce(ulke)
                    tarih_str = str(gt)
                    gece = gece_sayisi_hesapla(tarih_str)
                    
                    hesaplanan_toplam = gece * gunluk_fiyat
                    kalan_borc = hesaplanan_toplam - pes
                    
                    db_komut("""INSERT INTO Tbl_Hareketler 
                             (OdaNo, MusteriAdSoyad, KimlikNo, Ulke, DogumTarihi, GirisTarihi, GirisSaati, CikisTarihi, ToplamTutar, OdenenTutar, KalanBorc, Durum, GunlukFiyat, AcikTarih) 
                             VALUES (?,?,?,?,?,?,?,?,?,?,?,'Aktif',?,?)""", 
                             (o, ad, tc, ulke, str(DT), tarih_str, gs, str(ct) if not acik_tarih else "AÇIK", hesaplanan_toplam, pes, kalan_borc, gunluk_fiyat, 1 if acik_tarih else 0))
                    
                    db_komut("UPDATE Tbl_Odalar SET Durum='Dolu' WHERE OdaNo=?", (o,))
                    if pes > 0: 
                        db_komut("INSERT INTO Tbl_Kasa (IslemTipi, Kategori, Tutar, OdemeYontemi, Aciklama, Tarih) VALUES ('Gelir', 'ODA GELİRİ', ?, ?, ?, ?)", (pes, yon, f"ODA {o} GİRİŞ PEŞİNATI - {ad}", tarih_str))
                    st.success(f"{o} Numaralı Oda Girişi Yapıldı."); st.rerun()

    with t2:
        df_d = db_sorgu("SELECT OdaNo FROM Tbl_Odalar WHERE Durum='Dolu'")
        with st.form("modern_checkout_compact"):
            st.markdown("##### 📤 Müşteri Çıkış / Hesap Kapatma")
            o = st.selectbox("🚪 Çıkış Yapacak Oda", df_d['OdaNo'])
            
            # 🛠️ GÜNCELLEME: Çıkışta da sadece AKTİF olan kaydı getir
            h = db_sorgu("SELECT * FROM Tbl_Hareketler WHERE OdaNo=? AND Durum='Aktif' ORDER BY ID DESC LIMIT 1", (o,))
            if not h.empty:
                r = h.iloc[0]
                gece = gece_sayisi_hesapla(r['GirisTarihi'])
                
                g_fiyat = float(r['GunlukFiyat']) if (r['GunlukFiyat'] is not None and pd.notna(r['GunlukFiyat'])) else 1500.0
                t_tutar = float(r['ToplamTutar']) if (r['ToplamTutar'] is not None and pd.notna(r['ToplamTutar'])) else 0.0
                
                guncel_toplam = t_tutar if t_tutar > (g_fiyat * 1) else (gece * g_fiyat)
                guncel_kalan = guncel_toplam - (float(r['OdenenTutar']) if pd.notna(r['OdenenTutar']) else 0.0)
                
                st.warning(f"📋 Misafir: {r['MusteriAdSoyad']} | Geçen Gece: {gece} | Güncel Borç: {guncel_kalan:,.2f} TL")
                
                cc1, cc2 = st.columns(2)
                with cc1: tah = st.number_input("💵 Alınan Çıkış Ödemesi (TL)", value=float(max(0.0, guncel_kalan)))
                with cc2: yon = st.selectbox("💳 Ödeme Kanalları", ["Nakit", "Kredi Kartı", "Havale"])
                
                if st.form_submit_button("📤 Bakiyeyi Kapat ve Çıkışı Onayla", use_container_width=True):
                    db_komut("UPDATE Tbl_Hareketler SET ToplamTutar=?, OdenenTutar=OdenenTutar+?, KalanBorc=0, Durum='Tamamlandı' WHERE ID=?", (guncel_toplam, tah, r['ID']))
                    db_komut("UPDATE Tbl_Odalar SET Durum='Boş' WHERE OdaNo=?", (o,))
                    
                    if tah > 0: 
                        db_komut("INSERT INTO Tbl_Kasa (IslemTipi, Kategori, Tutar, OdemeYontemi, Aciklama, Tarih) VALUES ('Gelir', 'ODA GELİRİ', ?, ?, ?, ?)", (tah, yon, f"ODA {o} CHECK-OUT TAHSİLAT - {r['MusteriAdSoyad']}", datetime.now().strftime("%Y-%m-%d")))
                    st.success(f"{o} Numaralı oda boşaltıldı ve doğrudan 'Boş (Müsait)' durumuna alındı."); st.rerun()

# ==========================================
# SAYFA 3: TAHSİLAT & BORÇ TAKİBİ
# ==========================================
elif st.session_state.sayfa == "TAHSİLAT & BORÇ TAKİBİ":
    st.markdown("### 💳 Ara Tahsilat ve Hesap Düzenleme Ekranı")
    
    df_aktifler = db_sorgu("SELECT ID, OdaNo, MusteriAdSoyad, GirisTarihi, GunlukFiyat, ToplamTutar, OdenenTutar, KalanBorc FROM Tbl_Hareketler WHERE Durum='Aktif'")
    
    if df_aktifler.empty:
        st.success("🎉 Şu an otelde konaklayan aktif misafir bulunmuyor.")
    else:
        for idx, row in df_aktifler.iterrows():
            gece = gece_sayisi_hesapla(row['GirisTarihi'])
            g_fiyat = float(row['GunlukFiyat']) if (row['GunlukFiyat'] is not None and pd.notna(row['GunlukFiyat'])) else 1500.0
            t_tutar = float(row['ToplamTutar']) if (row['ToplamTutar'] is not None and pd.notna(row['ToplamTutar'])) else 0.0
            o_tutar = float(row['OdenenTutar']) if pd.notna(row['OdenenTutar']) else 0.0
            
            if t_tutar <= (g_fiyat * 1):
                df_aktifler.at[idx, 'ToplamTutar'] = gece * g_fiyat
            df_aktifler.at[idx, 'KalanBorc'] = df_aktifler.at[idx, 'ToplamTutar'] - o_tutar
            
        with st.form("ara_tahsilat_form"):
            st.markdown("##### 💵 Ara Ödeme (Tahsilat) Girişi")
            c_b1, c_b2, c_b3 = st.columns(3)
            with c_b1: secilen_b = st.selectbox("Misafir / Oda", df_aktifler['ID'], format_func=lambda x: f"Oda {df_aktifler[df_aktifler['ID']==x]['OdaNo'].values[0]} - {df_aktifler[df_aktifler['ID']==x]['MusteriAdSoyad'].values[0]}")
            with c_b2: tah_tutar = st.number_input("Alınan Tutar (TL)", min_value=0.0, step=100.0)
            with c_b3: tah_yon = st.selectbox("Ödeme Türü", ["Nakit", "Kredi Kartı", "Havale"])
                
            if st.form_submit_button("⚡ Ara Ödemeyi Kaydet", use_container_width=True):
                satir = df_aktifler[df_aktifler['ID'] == secilen_b].iloc[0]
                yeni_kalan = satir['KalanBorc'] - tah_tutar
                db_komut("UPDATE Tbl_Hareketler SET ToplamTutar=?, OdenenTutar = OdenenTutar + ?, KalanBorc = ? WHERE ID = ?", (satir['ToplamTutar'], tah_tutar, yeni_kalan, secilen_b))
                db_komut("INSERT INTO Tbl_Kasa (IslemTipi, Kategori, Tutar, OdemeYontemi, Aciklama, Tarih) VALUES ('Gelir', 'ODA GELİRİ', ?, ?, ?, ?)", (tah_tutar, tah_yon, f"ODA {satir['OdaNo']} ARA TAHSİLAT - {satir['MusteriAdSoyad']}", datetime.now().strftime("%Y-%m-%d")))
                st.success("Tahsilat girildi."); st.rerun()

        with st.expander("🛠️ ⚙️ Aktif Misafir Günlük Fiyat Düşüklüğü & Bilgi Revizesi", expanded=False):
            with st.form("aktif_yanlis_kayit_duzeltme"):
                st.info("💡 Misafirin günlük fiyatını düşürdüğünüzde, toplam tutar kalış süresiyle (gece sayısıyla) çarpılarak otomatik olarak yeniden hesaplanır.")
                secilen_duzenle_id = st.selectbox("Fiyatı Değişecek Oda / Misafir", df_aktifler['ID'], key="yanlis_tutar_sec", format_func=lambda x: f"Oda {df_aktifler[df_aktifler['ID']==x]['OdaNo'].values[0]} - {df_aktifler[df_aktifler['ID']==x]['MusteriAdSoyad'].values[0]}")
                
                satir_veri = df_aktifler[df_aktifler['ID'] == secilen_duzenle_id].iloc[0]
                gece_s = gece_sayisi_hesapla(satir_veri['GirisTarihi'])
                
                ham_fiyat = satir_veri['GunlukFiyat']
                mevcut_fiyat_float = float(ham_fiyat) if (ham_fiyat is not None and pd.notna(ham_fiyat)) else 1500.0
                
                cd_1, cd_2 = st.columns(2)
                with cd_1: yeni_g_fiyat = st.number_input("Yeni İndirimli/Düşük Günlük Oda Fiyatı (TL)", min_value=0.0, value=mevcut_fiyat_float)
                with cd_2: yeni_o_tutar = st.number_input("Şu Ana Kadar Alınan Toplam Peşinat/Ödeme (TL)", min_value=0.0, value=float(satir_veri['OdenenTutar']) if pd.notna(satir_veri['OdenenTutar']) else 0.0)
                
                st.caption(f"ℹ️ Bilgi: Bu oda şu ana kadar **{gece_s} gece** konakladı. Yeni günlük fiyata göre toplam konaklama tutarı otomatik olarak `{gece_s * yeni_g_fiyat} TL` şeklinde güncellenecektir.")
                
                if st.form_submit_button("💾 Yeni Fiyatı Tanımla ve Alacak Listesini Güncelle", use_container_width=True):
                    yeni_toplam = gece_s * yeni_g_fiyat
                    yeni_kalan_b = yeni_toplam - yeni_o_tutar
                    
                    db_komut("UPDATE Tbl_Hareketler SET GunlukFiyat=?, ToplamTutar=?, OdenenTutar=?, KalanBorc=? WHERE ID=?", 
                             (yeni_g_fiyat, yeni_toplam, yeni_o_tutar, yeni_kalan_b, secilen_duzenle_id))
                    st.success(f"🎉 Oda {satir_veri['OdaNo']} için günlük fiyat düşürüldü ve tüm alacak bakiyesi revize edildi."); st.rerun()

        st.markdown("#### 📋 Güncel Aktif Durum ve Alacak Listesi")
        df_aktifler_guncel = db_sorgu("SELECT ID, OdaNo as [Oda No], MusteriAdSoyad as [Müşteri Ad Soyad], GirisTarihi as [Giriş Tarihi], GunlukFiyat as [Günlük Fiyat], ToplamTutar as [Toplam Tutar], OdenenTutar as [Ödenen Tutar], KalanBorc as [Kalan Borç] FROM Tbl_Hareketler WHERE Durum='Aktif'")
        st.dataframe(df_aktifler_guncel, use_container_width=True)

# ==========================================
# SAYFA 4: KASA YÖNETİMİ
# ==========================================
elif st.session_state.sayfa == "KASA YÖNETİMİ":
    st.markdown("### 💰 Finansal Yönetim & Gelir-Gider")
    ay = datetime.now().strftime("%Y-%m")
    df_k = db_sorgu("SELECT * FROM Tbl_Kasa WHERE Tarih LIKE ?", (f"{ay}%",))
    
    gn = df_k[(df_k['IslemTipi']=='Gelir') & (df_k['OdemeYontemi']=='Nakit')]['Tutar'].sum()
    gk = df_k[(df_k['IslemTipi']=='Gelir') & (df_k['OdemeYontemi']=='Kredi Kartı')]['Tutar'].sum()
    
    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="metric-card" style="border-bottom: 4px solid #1e3a8a;"><div style="font-size:12px; color:#64748b; font-weight:700;">💵 NAKİT MEVCUT</div><div style="font-size:20px; font-weight:800;">{gn - df_k[(df_k["IslemTipi"]=="Gider") & (df_k["OdemeYontemi"]=="Nakit")]["Tutar"].sum():,.2f} TL</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card" style="border-bottom: 4px solid #10b981;"><div style="font-size:12px; color:#64748b; font-weight:700;">💳 KREDİ KARTI</div><div style="font-size:20px; font-weight:800;">{gk:,.2f} TL</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🛠️ GÜNCELLEME: Excel'e aktarma ve indirme butonu eklendi (Hata vermemesi için motor ayarlandı)
    st.markdown("##### 📥 Kasa Raporunu Excel Olarak İndir")
    if not df_k.empty:
        try:
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_k.to_excel(writer, index=False, sheet_name='Kasa_Raporu')
            buffer.seek(0)
            st.download_button(
                label="📥 Excel Dosyasını Bilgisayara Yükle",
                data=buffer,
                file_name=f"kasa_raporu_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Excel motoru eksik veya hata verdi. Lütfen terminalden 'pip install openpyxl' komutunu çalıştırın. Hata: {e}")
    else:
        st.info("Bu ay henüz kasada işlem bulunmuyor.")

    st.markdown("---")

    with st.expander("🗑️ Hatalı / Yanlış Kasa İşlemini Sil", expanded=False):
        with st.form("kasa_silme_form"):
            silinecek_id = st.number_input("Silmek İstediğiniz İşlemin ID Numarası:", min_value=1, step=1)
            if st.form_submit_button("❌ Kaydı Sil", use_container_width=True):
                db_komut("DELETE FROM Tbl_Kasa WHERE ID=?", (silinecek_id,))
                st.success("Kayıt başarıyla silindi."); st.rerun()

    with st.form("kasa_gelir_gider"):
        st.markdown("##### ➕ Yeni Manuel İşlem Girişi")
        rk1, rk2 = st.columns(2)
        with rk1: tip = st.selectbox("İşlem Yönü", ["Gelir", "Gider"])
        with rk2: kat = st.selectbox("Kategori", ["ODA GELİRİ", "MUTFAK", "PERSONEL ÖDEMESİ", "FATURA / GİDER", "DİĞER"])
        rk3, rk4 = st.columns(2)
        with rk3: tut = st.number_input("Tutar (TL)", min_value=0.0)
        with rk4: yon = st.selectbox("Ödeme Kanalı", ["Nakit", "Kredi Kartı", "Havale"])
        ack = st.text_input("Açıklama")
        tar = st.date_input("İşlem Tarihi")
        if st.form_submit_button("💾 Kaydet", use_container_width=True):
            db_komut("INSERT INTO Tbl_Kasa (IslemTipi, Kategori, Tutar, OdemeYontemi, Aciklama, Tarih) VALUES (?,?,?,?,?,?)", (tip, kat, tut, yon, buyuk_harf_turkce(ack), str(tar)))
            st.rerun()

    st.dataframe(df_k.sort_values("ID", ascending=False), use_container_width=True)

# ==========================================
# SAYFA 5: PERSONEL & MAAŞ
# ==========================================
elif st.session_state.sayfa == "PERSONEL & MAAŞ":
    st.markdown("### 👥 Personel Cari ve Ödemeleri")
    
    try:
        df_pl = db_sorgu("SELECT ID, AdSoyad, Gorev, CalismaTuru, GirisTarihi, CikisTarihi, NetMaas FROM Tbl_Personel")
    except Exception as e:
        try: db_komut("ALTER TABLE Tbl_Personel ADD COLUMN CalismaTuru TEXT DEFAULT 'AYLIK ÇALIŞAN'")
        except: pass
        try: db_komut("ALTER TABLE Tbl_Personel ADD COLUMN GirisTarihi TEXT DEFAULT 'DEVAM EDİYOR'")
        except: pass
        try: db_komut("ALTER TABLE Tbl_Personel ADD COLUMN CikisTarihi TEXT DEFAULT 'DEVAM EDİYOR'")
        except: pass
        
        try:
            df_pl = db_sorgu("SELECT ID, AdSoyad, Gorev, CalismaTuru, GirisTarihi, CikisTarihi, NetMaas FROM Tbl_Personel")
        except:
            df_gecici = db_sorgu("SELECT ID, AdSoyad, Gorev, NetMaas FROM Tbl_Personel")
            df_gecici["CalismaTuru"] = "AYLIK ÇALIŞAN"
            df_gecici["GirisTarihi"] = "BİLİNMİYOR"
            df_gecici["CikisTarihi"] = "DEVAM EDİYOR"
            df_pl = df_gecici[["ID", "AdSoyad", "Gorev", "CalismaTuru", "GirisTarihi", "CikisTarihi", "NetMaas"]]
    
    with st.expander("➕ Yeni Personel Tanımla", expanded=False):
        with st.form("hizli_p"):
            p_ad = st.text_input("Personel Adı Soyadı")
            p_gorev = st.text_input("Görevi", value="Otel Personeli")
            p_tur = st.selectbox("Çalışma Türü", ["AYLIK ÇALIŞAN", "GÜNLÜK ÇALIŞAN"])
            p_maas = st.number_input("Maaş Tutarı (TL)", min_value=0.0)
            p_giris = st.date_input("İşe Giriş Tarihi")
            
            if st.form_submit_button("💾 Personeli Ekle", use_container_width=True):
                if p_ad:
                    db_komut("INSERT INTO Tbl_Personel (AdSoyad, Gorev, CalismaTuru, GirisTarihi, CikisTarihi, NetMaas) VALUES (?, ?, ?, ?, 'DEVAM EDİYOR', ?)", 
                             (buyuk_harf_turkce(p_ad), buyuk_harf_turkce(p_gorev), p_tur, str(p_giris), p_maas))
                    st.success("Personel başarıyla eklendi."); st.rerun()

    if not df_pl.empty:
        with st.expander("⚙️ Hatalı Personel Bilgilerini Düzenle / Güncelle", expanded=False):
            with st.form("personel_duzenleme_form"):
                st.info("💡 Bilgilerini veya giriş tarihini yanlış kaydettiğiniz personeli seçip buradan hızlıca düzenleyebilirsiniz.")
                secilen_p_id = st.selectbox("Düzenlenecek Personel", df_pl['ID'], format_func=lambda x: df_pl[df_pl['ID']==x]['AdSoyad'].values[0])
                
                p_satir = df_pl[df_pl['ID'] == secilen_p_id].iloc[0]
                
                try:
                    mevcut_giris_date = datetime.strptime(str(p_satir['GirisTarihi']), "%Y-%m-%d").date()
                except:
                    mevcut_giris_date = datetime.now().date()
                
                c_pduz1, c_pduz2 = st.columns(2)
                with c_pduz1: yeni_p_gorev = st.text_input("Yeni / Düzeltilmiş Görevi", value=str(p_satir['Gorev']))
                with c_pduz2: yeni_p_giris = st.date_input("Doğru İşe Giriş Tarihi", value=mevcut_giris_date)
                
                c_pduz3, c_pduz4 = st.columns(2)
                with c_pduz3: yeni_p_tur = st.selectbox("Çalışma Türü Güncelle", ["AYLIK ÇALIŞAN", "GÜNLÜK ÇALIŞAN"], index=0 if p_satir['CalismaTuru']=="AYLIK ÇALIŞAN" else 1)
                with c_pduz4: yeni_p_maas = st.number_input("Güncel Net Maaş (TL)", min_value=0.0, value=float(p_satir['NetMaas']))
                
                if st.form_submit_button("💾 Personel Kartını Güncelle", use_container_width=True):
                    db_komut("""UPDATE Tbl_Personel 
                             SET Gorev=?, GirisTarihi=?, CalismaTuru=?, NetMaas=? 
                             WHERE ID=?""", 
                             (buyuk_harf_turkce(yeni_p_gorev), str(yeni_p_giris), yeni_p_tur, yeni_p_maas, secilen_p_id))
                    st.success(f"🎉 {p_satir['AdSoyad']} isimli personelin kart bilgileri güncellendi."); st.rerun()

    if not df_pl.empty:
        with st.form("maas_avans_odeme_form"):
            st.markdown("##### 💸 Ödeme Girişi (Maaş / Avans)")
            row_p1, row_p2 = st.columns(2)
            with row_p1: p_id = st.selectbox("Personel Seçin", df_pl['ID'], format_func=lambda x: df_pl[df_pl['ID']==x]['AdSoyad'].values[0])
            with row_p2: tip_p = st.selectbox("İşlem Türü", ["AVANS ÖDEMESİ", "MAAŞ ÖDEMESİ", "YEVMİYE ÖDEMESİ"])
            row_p3, row_p4 = st.columns(2)
            with row_p3: tut_p = st.number_input("Ödenen Tutar (TL)", min_value=0.0)
            with row_p4: yon_p = st.selectbox("Ödeme Kanalı", ["Nakit", "Havale"])
            ack_p = st.text_input("Açıklama Notu")
            
            if st.form_submit_button("💸 Ödemeyi Onayla", use_container_width=True):
                p_ad = df_pl[df_pl['ID']==p_id]['AdSoyad'].values[0]
                db_komut("INSERT INTO Tbl_PersonelHareketleri (PersonelID, IslemTuru, Tutar, Aciklama, Tarih) VALUES (?,?,?,?,?)", (p_id, tip_p, tut_p, buyuk_harf_turkce(ack_p), datetime.now().strftime("%Y-%m-%d")))
                db_komut("INSERT INTO Tbl_Kasa (IslemTipi, Kategori, Tutar, OdemeYontemi, Aciklama, Tarih) VALUES ('Gider', 'PERSONEL ÖDEMESİ', ?, ?, ?, ?)", (tut_p, yon_p, f"{p_ad} - {tip_p} ({ack_p})", datetime.now().strftime("%Y-%m-%d")))
                st.success("Ödeme kaydedildi."); st.rerun()

        st.dataframe(df_pl, use_container_width=True)
