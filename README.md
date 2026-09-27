# ⚽ SAHA İÇİ - Canlı Reel Maç Takip, Derin Analiz & AI Futbol Arkadaşı

Bu platform; tamamen **gerçek (reel) canlı, oynanacak ve oynanmış futbol maçlarını** takip eden, takımların güncel formunu, aralarındaki maçları (H2H), puan durumunu ve bahis oranlarını analiz ederek sanki **yıllardır tribünde ve taktik tahtası başında olan bilgili bir futbol arkadaşı (Taktik Serdar)** gibi konuşan, tahminler ve olasılıklar sunan yeni nesil bir web uygulamasıdır.

---

## 🌟 Öne Çıkan Özellikler

### 1. 🟢 %100 Gerçek & Canlı Maç Akışı (ESPN Global Sports Data)
- **Asla sanal veya sahte veri içermez:** Dünyanın dört bir yanındaki resmi futbol liglerinden gerçek zamanlı canlı skorları, başlama saatlerini, stat ve hakem bilgilerini çeker.
- **Kapsanan Başlıca Ligler:**
  - 🇹🇷 **Trendyol Süper Lig**
  - 🏆 **UEFA Şampiyonlar Ligi**
  - 🇪🇺 **UEFA Uluslar Ligi & Avrupa Ligi**
  - 🏴󠁧󠁢󠁥󠁮󠁧󠁿 **İngiltere Premier League**
  - 🇪🇸 **İspanya La Liga**
  - 🇮🇹 **İtalya Serie A**
  - 🇩🇪 **Almanya Bundesliga**
  - 🇫🇷 **Fransa Ligue 1**
  - 🌍 **Tüm Dünya Maçları** (Her gün yüzlerce canlı maç!)
- **Gelişmiş Tarih Gezgini:** Dünün biten maçları, bugünün canlı/oynanacak maçları, yarın ve takvimden seçtiğiniz herhangi bir gün!

### 2. 🎙️ "Bilgili Futbol Arkadaşın Taktik Serdar"
- Kuru ve yapay zeka klişelerinden uzak; samimi, cesur, futbol mantığına ve jargona hakim bir üslup.
- **Özel Analiz Mektubu:** Her maç için ev sahibi presi, deplasman kontra tehdidi, gol beklentisi, en sıcak skor ve net "Dost Meclisi Tavsiyesi".
- **İnteraktif Sohbet (AI Chat):**
  - İstediğin maçı seçip Serdar'a doğrudan sorabilirsin:
    - *"Bu maçta 2.5 üst patlar mı?"*
    - *"Sürpriz kokusu var mı?"*
    - *"Kupona banko ne yazarsın?"*
    - *"İlk yarı gol bekliyor musun?"*
  - **Sesli Okuma (TTS):** Analizleri ve cevapları Türkçe sesli olarak dinleyebilirsiniz.
- **Çift Motorlu Mimari:**
  - **Dahili Matematik & Taktik Motoru:** Hiçbir API anahtarı gerekmeden, gerçek maç istatistikleri ve Poisson modelini kullanarak anında yanıt verir.
  - **Google Gemini 2.5 Desteği:** İsteğe bağlı olarak ayarlar menüsünden kendi Gemini API anahtarınızı girerek derin LLM sohbetini de aktifleştirebilirsiniz.

### 3. 📊 Matematiksel Tahmin Modeli (Poisson & xG)
- Takımların son 5 maçtaki gol atma/yeme ortalamaları ve ev sahibi avantajını hesaplayan simülasyon.
- **1 - X - 2 Galibiyet Olasılık Barları**
- **2.5 Üst / Alt Olasılık Yüzdeleri**
- **Karşılıklı Gol Var / Yok (KG) Yüzdesi**
- **En Olası 3 Skor Tahmini**
- **Gerçek Bahis Oranları & Handikaplar (DraftKings / ESPN)**
- **Son 5 Maçın Skorları ve W/D/L Form Tablosu**
- **Muhtemel / Resmi 11'ler ve Saha Dizilişleri (Rosters)**

### 4. 🎯 Günün Değerli Kuponları & Günlük Başarı Takibi (YENİ!)
- **Yüksek Oran & Yüksek İhtimal:** Matematiksel olarak tutma şansı yüksek (%70 - %85) olan maçlardan Maç Sonucu, Gol Alt/Üst ve Korner kombinasyonlarıyla oluşturulmuş hazır kuponlar.
- **3 Farklı Kupon Stratejisi:**
  - 💎 **Değer (Value) Kuponu:** Maç Sonucu + Gol + Korner kombinasyonu (~4.00 - 7.50 çarpan).
  - 🛡️ **Altın Banko Kupon:** 1.5 Üst, Çifte Şans ve güçlü favoriler (~2.20 - 3.20 çarpan).
  - 🚀 **Oran Avcısı (Cesur Kupon):** 9.5 Üst Korner ve gollü düellolar (~8.50 - 15.00+ çarpan).
- **📅 Günlük Başarı Takibi & Tarih Arşivi:**
  - Yapılan tüm kuponlar `coupons_history.json` veri tabanında gün gün arşivlenir.
  - Maçlar bittiğinde kupondaki her tercih ve genel kupon durumu (KAZANDI ✅ / KAYBETTİ ❌) otomatik olarak teyit edilir.
  - **Başarı Karnesi:** Genel kazanma yüzdesi (% Başarı Oranı), tutan kupon sayısı, ortalama kazanan oran ve tekil tercih başarı oranı canlı takip edilir.
- **Etkileşimli Kazanç Hesaplayıcı:** Kupon tutarını (TL) girerek anlık olası kazancı hesaplama.

### 5. 🏆 Canlı Puan Durumu
- Süper Lig, Premier League, La Liga, Serie A, Bundesliga ve Ligue 1 puan tabloları (Oynanan, Galibiyet, Beraberlik, Mağlubiyet, Averaj, Puan).

---

## 🚀 Nasıl Çalıştırılır?

### Yöntem 1: Tek Tıkla Başlatma (Windows)
Proje klasöründeki **`baslat.bat`** dosyasına çift tıklayın.
Sunucu otomatik başlayacak ve varsayılan tarayıcınızda `http://localhost:8000` sayfası açılacaktır.

### Yöntem 2: Terminal / Komut Satırı
```bash
python server.py
```
Ardından tarayıcınızda açın:
```
http://localhost:8000
```

---

## 📁 Proje Dosya Yapısı
- `server.py`: FastAPI web sunucusu ve REST API uç noktaları.
- `football_engine.py`: ESPN API veri çekici, Poisson matematik modeli ve Taktik Serdar yorum motoru.
- `static/index.html`: Modern, duyarlı ve stadyum atmosferli ön yüz arayüzü.
- `static/style.css`: Karanlık tema (Dark mode) spor analitiği CSS stilleri.
- `static/app.js`: Gerçek zamanlı arayüz yönetimi, modal, filtreler ve sohbet mantığı.
- `baslat.bat`: Tek tıkla Windows başlatıcı script.
