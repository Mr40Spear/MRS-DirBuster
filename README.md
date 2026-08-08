# MRS DIRB PRO v2.0

> 🔍 Advanced Asynchronous Directory Discovery Tool

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

## ✨ Features

| Feature | Description |
|---------|----------|
| 🚀 **Async Scanning** | High-performance parallel requests powered by `aiohttp` |
| 🎭 **Multi-Mode** | Normal, Stealth, and Aggressive scanning modes |
| 🔄 **Recursive** | Automatic discovery of subdirectories |
| 🛡️ **WAF Bypass** | Random User-Agents, custom delays, and stealth features |
| 🔐 **Sensitive Data Detection** | Automatic detection of API keys, passwords, and tokens |
| 📊 **Detailed Reporting** | Output results in JSON and TXT formats |
| 🎯 **Soft 404 Detection** | Smart filtering of fake 404 responses |
| 🌐 **Proxy Support** | Easy integration with tools like Burp Suite or ZAP |

## 📦 Installation

### Windows
```powershell
.\install.ps1
```

### Linux/Mac
```bash
chmod +x Id.bash
./Id.bash
```

### Manual
```bash
pip install aiohttp rich
```

## 🚀 Usage

### Basic Usage
```bash
python mrs_dirb_pro.py https://target.com
```

### Advanced Examples

```bash
# Using a custom wordlist
python mrs_dirb_pro.py https://target.com -w custom.txt

# High-speed scanning (100 threads)
python mrs_dirb_pro.py https://target.com -t 100

# Stealth mode (WAF bypass)
python mrs_dirb_pro.py https://target.com -m stealth

# Adding extensions
python mrs_dirb_pro.py https://target.com -x .php,.html,.bak,.old

# Recursive scanning (Depth 3)
python mrs_dirb_pro.py https://target.com -r -d 3

# Using a proxy
python mrs_dirb_pro.py https://target.com -p http://127.0.0.1:8080

# Scanning with Cookies
python mrs_dirb_pro.py https://target.com -c "session=abc123; auth=xyz"

# Save results to a folder
python mrs_dirb_pro.py https://target.com -o results_folder
```

## 📋 Parameters

| Parameter | Short | Description | Default |
|-----------|------|----------|------------|
| `--wordlist` | `-w` | Path to wordlist file | robots.txt |
| `--threads` | `-t` | Number of concurrent requests | 50 |
| `--timeout` | `-T` | Request timeout (seconds) | 10 |
| `--delay` | `-D` | Delay between requests | 0 |
| `--mode` | `-m` | Scan mode (normal/stealth/aggressive) | normal |
| `--user-agent` | `-u` | Custom User-Agent string | Random |
| `--cookie` | `-c` | Cookie value | - |
| `--header` | `-H` | Custom header (Key:Value) | - |
| `--extensions` | `-x` | Extensions to append (.php,.html) | - |
| `--exclude` | `-e` | HTTP codes to exclude | 404 |
| `--follow` | `-f` | Follow HTTP redirects | False |
| `--recursive` | `-r` | Enable recursive scanning | False |
| `--depth` | `-d` | Maximum recursion depth | 3 |
| `--proxy` | `-p` | Proxy URL | - |
| `--insecure` | `-k` | Skip SSL verification | False |
| `--output` | `-o` | Output filename/folder | - |

## 🛠️ Wordlist Optimizer

Optimize your wordlists for better performance:

```bash
# Basic optimization
python wordlist_optimizer.py robots.txt

# Append extensions
python wordlist_optimizer.py wordlist.txt -x .php,.html,.bak

# Filter by Min/Max length
python wordlist_optimizer.py wordlist.txt --min 3 --max 50

# Analyze wordlist
python wordlist_optimizer.py wordlist.txt --analyze

# Generate common paths list
python wordlist_optimizer.py --generate-common

# Merge multiple lists
python wordlist_optimizer.py --merge list1.txt list2.txt -o merged.txt
```

## 📊 Output Example

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

## 📁 Project Structure

```
mrs_dirbuster/
├── mrs_dirb_pro.py        # Main scanning engine (ENHANCED)
├── mrs_dirb.py            # Legacy version
├── wordlist_optimizer.py  # Wordlist optimization tool (NEW)
├── install.ps1            # Windows installation script (NEW)
├── Id.bash                # Linux installation script
├── mrs_dirb.txt           # ASCII banner collection
├── robots.txt             # Default wordlist (4750+ paths)
└── README.md              # Documentation
```

## ⚠️ Legal Disclaimer

This tool is designed for legal and authorized security testing purposes only. Attempting to access systems without prior permission is illegal.

- ✅ Test your own systems
- ✅ Test systems you have explicit written permission for
- ✅ Use for Bug Bounty programs
- ❌ Do not use for unauthorized attacks

## 📜 License

MIT License - For educational and research purposes.

---

**MRS DIRB PRO v2.0** | Developed with ❤️ by Cemal Kanaç
