# MRS DIRB PRO v2.0

> 🔍 Gelişmiş Asenkron Dizin Keşif Aracı

```
╔═══════════════════════════════════════════════════════════════════════╗
║   ███╗   ███╗██████╗ ███████╗    ██████╗ ██╗██████╗ ██████╗          ║
║   ████╗ ████║██╔══██╗██╔════╝    ██╔══██╗██║██╔══██╗██╔══██╗         ║
║   ██╔████╔██║██████╔╝███████╗    ██║  ██║██║██████╔╝██████╔╝         ║
║   ██║╚██╔╝██║██╔══██╗╚════██║    ██║  ██║██║██╔══██╗██╔══██╗         ║
║   ██║ ╚═╝ ██║██║  ██║███████║    ██████╔╝██║██║  ██║██████╔╝         ║
║   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝    ╚═════╝ ╚═╝╚═╝  ╚═╝╚═════╝          ║
║                     [PRO v2.0]                                        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## ✨ Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🚀 **Asenkron Tarama** | aiohttp ile yüksek performanslı paralel istekler |
| 🎭 **Çoklu Mod** | Normal, Stealth, Aggressive modları |
| 🔄 **Recursive** | Alt dizinleri otomatik keşfetme |
| 🛡️ **WAF Bypass** | Rastgele User-Agent, gecikme, stealth modu |
| 🔐 **Hassas Veri Tespiti** | API key, password, token otomatik algılama |
| 📊 **Detaylı Raporlama** | JSON ve TXT formatında çıktı |
| 🎯 **Soft 404 Tespiti** | Sahte 404 yanıtlarını filtreleme |
| 🌐 **Proxy Desteği** | Burp, ZAP gibi araçlarla entegrasyon |

## 📦 Kurulum

### Windows
```powershell
.\install.ps1
```

### Linux/Mac
```bash
chmod +x Id.bash
./Id.bash
```

### Manuel
```bash
pip install aiohttp rich
```

## 🚀 Kullanım

### Temel Kullanım
```bash
python mrs_dirb_pro.py https://hedef.com
```

### Gelişmiş Örnekler

```bash
# Özel wordlist ile
python mrs_dirb_pro.py https://hedef.com -w custom.txt

# Yüksek hızda tarama (100 thread)
python mrs_dirb_pro.py https://hedef.com -t 100

# Stealth mod (WAF bypass)
python mrs_dirb_pro.py https://hedef.com -m stealth

# Uzantı ekleme
python mrs_dirb_pro.py https://hedef.com -x .php,.html,.bak,.old

# Recursive tarama
python mrs_dirb_pro.py https://hedef.com -r -d 3

# Proxy kullanımı
python mrs_dirb_pro.py https://hedef.com -p http://127.0.0.1:8080

# Cookie ile
python mrs_dirb_pro.py https://hedef.com -c "session=abc123; auth=xyz"

# Sonuçları kaydet
python mrs_dirb_pro.py https://hedef.com -o sonuclar
```

## 📋 Parametreler

| Parametre | Kısa | Açıklama | Varsayılan |
|-----------|------|----------|------------|
| `--wordlist` | `-w` | Wordlist dosyası | robots.txt |
| `--threads` | `-t` | Eşzamanlı istek sayısı | 50 |
| `--timeout` | `-T` | İstek timeout (saniye) | 10 |
| `--delay` | `-D` | İstekler arası gecikme | 0 |
| `--mode` | `-m` | Tarama modu (normal/stealth/aggressive) | normal |
| `--user-agent` | `-u` | Özel User-Agent | Rastgele |
| `--cookie` | `-c` | Cookie değeri | - |
| `--header` | `-H` | Özel header (Key:Value) | - |
| `--extensions` | `-x` | Uzantılar (.php,.html) | - |
| `--exclude` | `-e` | Hariç tutulacak HTTP kodları | 404 |
| `--follow` | `-f` | Yönlendirmeleri takip et | False |
| `--recursive` | `-r` | Recursive tarama | False |
| `--depth` | `-d` | Recursive derinlik | 3 |
| `--proxy` | `-p` | Proxy URL | - |
| `--insecure` | `-k` | SSL doğrulama | False |
| `--output` | `-o` | Çıktı dosyası adı | - |

## 🛠️ Wordlist Optimizer

Wordlist'lerinizi optimize edin:

```bash
# Temel optimizasyon
python wordlist_optimizer.py robots.txt

# Uzantı ekleme
python wordlist_optimizer.py wordlist.txt -x .php,.html,.bak

# Min/Max uzunluk
python wordlist_optimizer.py wordlist.txt --min 3 --max 50

# Analiz
python wordlist_optimizer.py wordlist.txt --analyze

# Yaygın yollar listesi oluştur
python wordlist_optimizer.py --generate-common

# Birden fazla listeyi birleştir
python wordlist_optimizer.py --merge list1.txt list2.txt -o merged.txt
```

## 📊 Çıktı Örneği

```
╔═══════════════════════════════════════════════════════════════════════╗
║   MRS DIRB PRO - Gelişmiş Dizin Keşif Aracı v2.0                     ║
╚═══════════════════════════════════════════════════════════════════════╝

🎯 Tarama Yapılandırması
┌──────────┬─────────────────────────┐
│ Hedef    │ https://example.com     │
│ Wordlist │ robots.txt              │
│ Mod      │ normal                  │
│ Thread   │ 50                      │
│ Timeout  │ 10s                     │
└──────────┴─────────────────────────┘

📚 4750 kelime yüklendi: robots.txt
🎯 Baseline hash: a1b2c3d4 | Length: 1234

✅ [200] https://example.com/admin │ Admin Panel
🔐 [401] https://example.com/api │ Unauthorized
🔀 [301] https://example.com/old → https://example.com/new
🚫 [403] https://example.com/.git │ Forbidden
✅ [200] https://example.com/backup/ 📁 DIRECTORY
    🔑 Parola bulundu

📊 Tarama Özeti
┌────────────────┬──────────┐
│ Toplam Taranan │ 4,750    │
│ Bulunan        │ 47       │
│ Engellenen     │ 3        │
│ Hata           │ 12       │
│ Süre           │ 45.32s   │
│ Hız            │ 104.8/s  │
└────────────────┴──────────┘

💾 Sonuçlar kaydedildi:
    • JSON: results.json
    • TXT: results.txt
```

## 📁 Proje Yapısı

```
mrs_dirbuster/
├── mrs_dirb_pro.py        # Ana tarama motoru (GELİŞTİRİLMİŞ)
├── mrs_dirb.py            # Eski versiyon (legacy)
├── wordlist_optimizer.py  # Wordlist optimizasyon aracı (YENİ)
├── install.ps1            # Windows kurulum scripti (YENİ)
├── Id.bash                # Linux kurulum scripti
├── mrs_dirb.txt           # ASCII banner koleksiyonu
├── robots.txt             # Varsayılan wordlist (4750+ yol)
└── README.md              # Bu dosya
```

## ⚠️ Yasal Uyarı

Bu araç sadece **yasal ve yetkili** güvenlik testleri için tasarlanmıştır. İzinsiz sistemlere erişim girişimi yasadışıdır.

- ✅ Kendi sistemlerinizi test edin
- ✅ İzin alınmış sistemleri test edin
- ✅ Bug bounty programlarında kullanın
- ❌ İzinsiz sistemlere saldırmayın

## 📜 Lisans

MIT License - Eğitim ve araştırma amaçlıdır.

---

**MRS DIRB PRO v2.0** | Cemal Kanaç Tarafından Geliştirildi ❤️ 
