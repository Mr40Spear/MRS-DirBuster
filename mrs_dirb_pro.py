#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
+==================================================================+
|     MRS DIRB PRO - Gelismis Dizin Kesif Araci v2.0              |
|     Asenkron, coklu protokol, akilli tarama                      |
+==================================================================+
"""

import argparse
import asyncio
import aiohttp
import json
import re
import sys
import time
import hashlib
import random
import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Set
from enum import Enum
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor

# Windows konsol encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
except ImportError:
    print("[!] 'rich' kutuphanesi yukleyin: pip install rich")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════
#                         YAPILANDIRMA
# ═══════════════════════════════════════════════════════════════════

class ScanMode(Enum):
    """Tarama modları"""
    NORMAL = "normal"
    STEALTH = "stealth"
    AGGRESSIVE = "aggressive"
    RECURSIVE = "recursive"


@dataclass
class ScanConfig:
    """Tarama yapılandırması"""
    base_url: str
    wordlist: str = "robots.txt"
    threads: int = 50
    timeout: int = 10
    delay: float = 0.0
    mode: ScanMode = ScanMode.NORMAL
    user_agent: Optional[str] = None
    cookie: Optional[str] = None
    follow_redirects: bool = False
    extensions: List[str] = field(default_factory=list)
    exclude_codes: List[int] = field(default_factory=lambda: [404])
    output_file: Optional[str] = None
    recursive: bool = False
    max_depth: int = 3
    proxy: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    verify_ssl: bool = True
    verbose: bool = False  # Sadece 200'ler mi yoksa tüm sonuçlar mı


@dataclass
class ScanResult:
    """Tarama sonucu"""
    url: str
    status_code: int
    content_length: int
    response_time: float
    content_type: str = ""
    redirect_url: str = ""
    title: str = ""
    is_directory: bool = False
    findings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ===================================================================
#                         SABITLER
# ===================================================================

console = Console(force_terminal=True)

STATUS_INFO = {
    200: ("[+]", "OK", "green"),
    201: ("[+]", "Created", "green"),
    204: ("[!]", "No Content", "yellow"),
    301: ("[>]", "Moved Permanently", "cyan"),
    302: ("[>]", "Found", "cyan"),
    307: ("[>]", "Temporary Redirect", "cyan"),
    308: ("[>]", "Permanent Redirect", "cyan"),
    400: ("[X]", "Bad Request", "red"),
    401: ("[L]", "Unauthorized", "magenta"),
    403: ("[!]", "Forbidden", "red"),
    404: ("[?]", "Not Found", "dim"),
    405: ("[!]", "Method Not Allowed", "yellow"),
    429: ("[W]", "Too Many Requests", "yellow"),
    500: ("[X]", "Internal Server Error", "red"),
    502: ("[X]", "Bad Gateway", "red"),
    503: ("[!]", "Service Unavailable", "yellow"),
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
]

SENSITIVE_PATTERNS = {
    r'password\s*[:=]': '[KEY] Parola bulundu',
    r'api[_-]?key\s*[:=]': '[KEY] API anahtari bulundu',
    r'secret\s*[:=]': '[KEY] Gizli anahtar bulundu',
    r'AWS_ACCESS_KEY': '[AWS] AWS anahtari bulundu',
    r'mongodb://': '[DB] MongoDB baglanti stringi',
    r'mysql://': '[DB] MySQL baglanti stringi',
    r'postgresql://': '[DB] PostgreSQL baglanti stringi',
    r'-----BEGIN.*PRIVATE KEY-----': '[PRIV] Private key bulundu',
    r'Bearer\s+[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+': '[JWT] JWT token bulundu',
}


# ===================================================================
#                         YARDIMCI FONKSIYONLAR
# ===================================================================

def print_banner():
    """ASCII banner goster - renkli ve animasyonlu"""
    import random
    
    banners = [
        """[bold magenta]
    __  _______  _____    ____  ________  ____ 
   /  |/  / __ \/ ___/   / __ \/  _/ __ \/ __ )
  / /|_/ / /_/ /\__ \   / / / // // /_/ / __  |
 / /  / / _, _/___/ /  / /_/ // // _, _/ /_/ / 
/_/  /_/_/ |_|/____/  /_____/___/_/ |_/_____/  
                                    [PRO v2.0]
[/bold magenta]""",
        
        """[bold cyan]
 ███╗   ███╗██████╗ ███████╗    ██████╗ ██╗██████╗ ██████╗ 
 ████╗ ████║██╔══██╗██╔════╝    ██╔══██╗██║██╔══██╗██╔══██╗
 ██╔████╔██║██████╔╝███████╗    ██║  ██║██║██████╔╝██████╔╝
 ██║╚██╔╝██║██╔══██╗╚════██║    ██║  ██║██║██╔══██╗██╔══██╗
 ██║ ╚═╝ ██║██║  ██║███████║    ██████╔╝██║██║  ██║██████╔╝
 ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝    ╚═════╝ ╚═╝╚═╝  ╚═╝╚═════╝ 
                                              [bold yellow][PRO v2.0][/bold yellow]
[/bold cyan]""",

        """[bold green]
  __  __ ____  ____    ____ ___ ____  ____  
 |  \/  |  _ \/ ___|  |  _ \_ _|  _ \| __ ) 
 | |\/| | |_) \___ \  | | | | || |_) |  _ \ 
 | |  | |  _ < ___) | | |_| | ||  _ <| |_) |
 |_|  |_|_| \_\____/  |____/___|_| \_\____/ 
                              [bold red][PRO v2.0][/bold red]
[/bold green]""",

        """[bold red]
 ╔╦╗╦═╗╔═╗  ╔╦╗╦╦═╗╔╗ 
 ║║║╠╦╝╚═╗   ║║║╠╦╝╠╩╗
 ╩ ╩╩╚═╚═╝  ═╩╝╩╩╚═╚═╝
       [bold yellow][ Directory Buster PRO v2.0 ][/bold yellow]
[/bold red]"""
    ]
    
    banner = random.choice(banners)
    console.print(banner)
    
    # Alt bilgi kutusu
    console.print("[bold white on blue]" + "="*60 + "[/bold white on blue]")
    console.print("[bold white on blue]   [*] Asenkron Tarama    [*] WAF Bypass    [*] Recursive   [/bold white on blue]")
    console.print("[bold white on blue]   [*] Hassas Veri Tespit [*] Proxy Support [*] Multi-Mode  [/bold white on blue]")
    console.print("[bold white on blue]" + "="*60 + "[/bold white on blue]")
    console.print()


def load_wordlist(path: str, extensions: List[str] = None) -> List[str]:
    """Wordlist yukle ve uzantilari ekle"""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Benzersiz yap
        words = list(set(words))
        
        # Uzantilari ekle
        if extensions:
            extended = []
            for word in words:
                extended.append(word)
                for ext in extensions:
                    if not word.endswith(ext):
                        extended.append(f"{word}{ext}")
            words = list(set(extended))
        
        console.print(f"[cyan][*] {len(words)} kelime yuklendi: {path}[/cyan]")
        return words
    
    except FileNotFoundError:
        console.print(f"[bold red][X] Wordlist bulunamadi: {path}[/bold red]")
        sys.exit(1)


def extract_title(html: str) -> str:
    """HTML'den sayfa basligini cikar"""
    match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def detect_sensitive_data(content: str) -> List[str]:
    """İçerikte hassas veri ara"""
    findings = []
    for pattern, description in SENSITIVE_PATTERNS.items():
        if re.search(pattern, content, re.IGNORECASE):
            findings.append(description)
    return findings


def get_random_user_agent() -> str:
    """Rastgele User-Agent döndür"""
    return random.choice(USER_AGENTS)


def normalize_url(url: str) -> str:
    """URL'yi normalize et - protokol yoksa ekle"""
    url = url.strip()
    
    # Boşsa hata
    if not url:
        return url
    
    # Zaten protokol varsa döndür
    if url.startswith(('http://', 'https://')):
        return url
    
    # :// varsa ama http/https değilse düzelt
    if '://' in url:
        return url
    
    # Protokol yoksa https ekle
    # www ile başlıyorsa veya nokta içeriyorsa domain olarak kabul et
    if url.startswith('www.') or '.' in url.split('/')[0]:
        return f'https://{url}'
    
    # Sadece domain adı girilmişse (örn: youtube)
    # TLD olmadan girilmiş olabilir, yine de https ekle
    return f'https://{url}'


def calculate_hash(content: str) -> str:
    """İçerik hash'i hesapla"""
    return hashlib.md5(content.encode()).hexdigest()[:8]


# ═══════════════════════════════════════════════════════════════════
#                         TARAMA MOTORU
# ═══════════════════════════════════════════════════════════════════

class MRSDirbScanner:
    """Gelişmiş dizin tarayıcı"""
    
    def __init__(self, config: ScanConfig):
        self.config = config
        self.results: List[ScanResult] = []
        self.scanned_urls: Set[str] = set()
        self.waf_detected = False
        self.baseline_hash: Optional[str] = None
        self.baseline_length: int = 0
        self.stats = {
            'total': 0,
            'found': 0,
            'errors': 0,
            'blocked': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _get_headers(self) -> Dict[str, str]:
        """İstek başlıklarını oluştur"""
        headers = {
            'User-Agent': self.config.user_agent or get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        if self.config.cookie:
            headers['Cookie'] = self.config.cookie
        
        if self.config.mode == ScanMode.STEALTH:
            headers['Cache-Control'] = 'no-cache'
            headers['Pragma'] = 'no-cache'
        
        headers.update(self.config.headers)
        return headers
    
    async def _get_baseline(self, session: aiohttp.ClientSession) -> None:
        """404 baseline yanıtını al"""
        random_path = f"/{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=16))}"
        url = urljoin(self.config.base_url, random_path)
        
        try:
            async with session.get(url, timeout=self.config.timeout, ssl=self.config.verify_ssl) as response:
                content = await response.text()
                self.baseline_hash = calculate_hash(content)
                self.baseline_length = len(content)
                console.print(f"[dim][*] Baseline hash: {self.baseline_hash} | Length: {self.baseline_length}[/dim]")
        except Exception:
            pass
    
    async def _check_url(
        self, 
        session: aiohttp.ClientSession, 
        endpoint: str,
        depth: int = 0
    ) -> Optional[ScanResult]:
        """Tek URL'yi kontrol et"""
        url = urljoin(self.config.base_url, endpoint)
        
        if url in self.scanned_urls:
            return None
        self.scanned_urls.add(url)
        
        # Stealth modunda rastgele gecikme
        if self.config.mode == ScanMode.STEALTH:
            await asyncio.sleep(random.uniform(0.5, 2.0))
        elif self.config.delay > 0:
            await asyncio.sleep(self.config.delay)
        
        try:
            start_time = time.monotonic()
            
            async with session.get(
                url, 
                timeout=self.config.timeout,
                allow_redirects=self.config.follow_redirects,
                ssl=self.config.verify_ssl
            ) as response:
                elapsed = time.monotonic() - start_time
                content = await response.text()
                content_length = len(content)
                
                # WAF tespiti
                if response.status in [429, 503]:
                    self.stats['blocked'] += 1
                    if self.stats['blocked'] > 5 and not self.waf_detected:
                        self.waf_detected = True
                        console.print("[bold yellow][!] WAF/Rate Limiting tespit edildi![/bold yellow]")
                
                # Soft 404 tespiti (baseline karşılaştırması)
                current_hash = calculate_hash(content)
                if response.status == 200:
                    if self.baseline_hash and current_hash == self.baseline_hash:
                        return None  # Soft 404
                    if self.baseline_length > 0 and abs(content_length - self.baseline_length) < 50:
                        return None  # Muhtemelen soft 404
                
                # Filtreleme
                if response.status in self.config.exclude_codes:
                    return None
                
                # Sonuç oluştur
                result = ScanResult(
                    url=url,
                    status_code=response.status,
                    content_length=content_length,
                    response_time=elapsed,
                    content_type=response.headers.get('Content-Type', ''),
                    redirect_url=str(response.headers.get('Location', '')),
                    title=extract_title(content),
                    is_directory='Index of' in content or response.status == 200 and endpoint.endswith('/'),
                    findings=detect_sensitive_data(content[:5000])  # İlk 5KB'da ara
                )
                
                # Sonucu göster
                self._print_result(result)
                self.results.append(result)
                self.stats['found'] += 1
                
                # Recursive tarama
                if self.config.recursive and result.is_directory and depth < self.config.max_depth:
                    links = re.findall(r'href="([^"]+)"', content, re.IGNORECASE)
                    for link in links:
                        if link not in ['../', './', '#'] and not link.startswith(('http', 'mailto', 'javascript')):
                            await self._check_url(session, urljoin(endpoint + '/', link), depth + 1)
                
                return result
                
        except asyncio.TimeoutError:
            self.stats['errors'] += 1
            return None
        except Exception as e:
            self.stats['errors'] += 1
            return None
    
    def _print_result(self, result: ScanResult) -> None:
        """Sonucu formatli ve renkli sekilde yazdir"""
        status = result.status_code
        
        # Verbose kapaliysa sadece 200, 401, 403 ve hassas veri icerenleri goster
        if not self.config.verbose:
            if status not in [200, 201, 401, 403] and not result.findings:
                return  # Sessiz mod - sadece onemli sonuclari goster
        
        # Status koduna gore renk ve sembol
        if status == 200:
            prefix = "[bold green][+][/bold green]"
            color = "green"
        elif status in [301, 302, 307, 308]:
            prefix = "[bold cyan][>][/bold cyan]"
            color = "cyan"
        elif status in [401, 403]:
            prefix = "[bold magenta][!][/bold magenta]"
            color = "magenta"
        elif status in [429, 503]:
            prefix = "[bold yellow][W][/bold yellow]"
            color = "yellow"
        elif status >= 500:
            prefix = "[bold red][X][/bold red]"
            color = "red"
        else:
            prefix = "[dim][?][/dim]"
            color = "white"
        
        # Ana satir
        line = f"{prefix} [{color}][{status}][/{color}] "
        line += f"[bold white]{result.url}[/bold white] "
        line += f"[dim]({result.content_length}B | {result.response_time:.2f}s)[/dim]"
        
        # Baslik varsa
        if result.title:
            title = result.title[:35] + "..." if len(result.title) > 35 else result.title
            line += f" [italic cyan]{title}[/italic cyan]"
        
        # Yonlendirme varsa (sadece verbose modda goster)
        if result.redirect_url and self.config.verbose:
            line += f"\n    [yellow]-> {result.redirect_url}[/yellow]"
        
        # Dizin ise
        if result.is_directory:
            line += " [bold white on green] DIR [/bold white on green]"
        
        console.print(line)
        
        # Hassas veri bulgulari
        for finding in result.findings:
            console.print(f"    [bold red]{finding}[/bold red]")
    
    async def scan(self) -> None:
        """Taramayi baslat"""
        print_banner()
        
        # Yapilandirma bilgisi - basit format
        console.print("[cyan]" + "="*50 + "[/cyan]")
        console.print(f"[cyan]  Hedef    : [bold]{self.config.base_url}[/bold][/cyan]")
        console.print(f"[cyan]  Wordlist : {self.config.wordlist}[/cyan]")
        console.print(f"[cyan]  Mod      : {self.config.mode.value}[/cyan]")
        console.print(f"[cyan]  Thread   : {self.config.threads}[/cyan]")
        console.print(f"[cyan]  Timeout  : {self.config.timeout}s[/cyan]")
        if self.config.extensions:
            console.print(f"[cyan]  Uzantilar: {', '.join(self.config.extensions)}[/cyan]")
        console.print("[cyan]" + "="*50 + "[/cyan]")
        console.print()
        
        # Wordlist yukle
        endpoints = load_wordlist(self.config.wordlist, self.config.extensions)
        self.stats['total'] = len(endpoints)
        self.stats['start_time'] = datetime.now()
        
        # Connector ayarlari
        connector = aiohttp.TCPConnector(
            limit=self.config.threads,
            limit_per_host=self.config.threads,
            force_close=True
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        async with aiohttp.ClientSession(
            headers=self._get_headers(),
            connector=connector,
            timeout=timeout
        ) as session:
            # Baseline al
            await self._get_baseline(session)
            
            # Progress bar ile tarama
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold cyan]{task.description}[/bold cyan]"),
                BarColumn(complete_style="green", finished_style="bold green"),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("|"),
                TextColumn("[green]{task.completed}/{task.total}[/green]"),
                TextColumn("|"),
                TimeElapsedColumn(),
                TextColumn("|"),
                TimeRemainingColumn(),
                console=console,
                transient=False
            ) as progress:
                task = progress.add_task("Scanning...", total=len(endpoints))
                
                # Semaphore ile eszamanlilik kontrolu
                semaphore = asyncio.Semaphore(self.config.threads)
                
                async def limited_check(endpoint):
                    async with semaphore:
                        result = await self._check_url(session, endpoint)
                        progress.advance(task)
                        return result
                
                tasks = [limited_check(endpoint) for endpoint in endpoints]
                await asyncio.gather(*tasks)
        
        self.stats['end_time'] = datetime.now()
        
        # Sonuç raporu
        self._print_summary()
        
        # Dosyaya kaydet
        if self.config.output_file:
            self._save_results()
    
    def _print_summary(self) -> None:
        """Tarama ozeti - Renkli ve guzel formatli"""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        rate = self.stats['total']/duration if duration > 0 else 0
        
        print("\n")
        # Ust cerceve
        console.print("[bold magenta]" + "=" * 60 + "[/bold magenta]")
        console.print("[bold white on magenta]" + " " * 18 + "TARAMA TAMAMLANDI!" + " " * 18 + "[/bold white on magenta]")
        console.print("[bold magenta]" + "=" * 60 + "[/bold magenta]")
        
        print("")
        # Hedef bilgisi
        console.print("[bold cyan]" + "-" * 60 + "[/bold cyan]")
        console.print(f"[bold cyan]  HEDEF   :[/bold cyan] [bold white]{self.config.base_url}[/bold white]")
        console.print(f"[bold cyan]  SURE    :[/bold cyan] [bold white]{duration:.2f} saniye[/bold white]")
        console.print(f"[bold cyan]  ISTEK   :[/bold cyan] [bold white]{self.stats['total']} toplam[/bold white]")
        console.print(f"[bold cyan]  HIZ     :[/bold cyan] [bold white]{rate:.1f} istek/saniye[/bold white]")
        console.print("[bold cyan]" + "-" * 60 + "[/bold cyan]")
        
        print("")
        # Sonuc istatistikleri
        console.print("[bold green]  [+] BULUNAN     :[/bold green] [bold white]{:>6}[/bold white]".format(self.stats['found']))
        console.print("[bold yellow]  [!] ENGELLENEN  :[/bold yellow] [bold white]{:>6}[/bold white]".format(self.stats['blocked']))
        console.print("[bold red]  [X] HATA        :[/bold red] [bold white]{:>6}[/bold white]".format(self.stats['errors']))
        
        if self.waf_detected:
            print("")
            console.print("[bold red on white]  !!! WAF/FIREWALL TESPIT EDILDI !!!  [/bold red on white]")
        
        print("")
        console.print("[bold magenta]" + "=" * 60 + "[/bold magenta]")
        
        # Bulunan sonuclari kategorize et
        if self.results:
            console.print()
            console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")
            console.print("[bold yellow]           BULUNAN KAYNAKLAR[/bold yellow]")
            console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")
            
            directories = [r for r in self.results if r.is_directory]
            sensitive = [r for r in self.results if r.findings]
            redirects = [r for r in self.results if r.status_code in [301, 302, 307, 308]]
            auth_required = [r for r in self.results if r.status_code in [401, 403]]
            
            if directories:
                console.print(f"\n[bold green][DIR] Dizinler ({len(directories)}):[/bold green]")
                for d in directories[:10]:
                    console.print(f"  [green]->[/green] {d.url}")
                if len(directories) > 10:
                    console.print(f"  [dim]... ve {len(directories)-10} tane daha[/dim]")
            
            if sensitive:
                console.print(f"\n[bold red][!] Hassas Veriler ({len(sensitive)}):[/bold red]")
                for s in sensitive[:10]:
                    console.print(f"  [red]->[/red] {s.url}: {', '.join(s.findings)}")
            
            if auth_required:
                console.print(f"\n[bold magenta][L] Yetki Gerektiren ({len(auth_required)}):[/bold magenta]")
                for a in auth_required[:10]:
                    console.print(f"  [magenta]->[/magenta] [{a.status_code}] {a.url}")
    
    def _save_results(self) -> None:
        """Sonuçları dosyaya kaydet"""
        output_data = {
            'scan_info': {
                'target': self.config.base_url,
                'wordlist': self.config.wordlist,
                'mode': self.config.mode.value,
                'start_time': self.stats['start_time'].isoformat(),
                'end_time': self.stats['end_time'].isoformat(),
                'total_scanned': self.stats['total'],
                'found': self.stats['found'],
            },
            'results': [asdict(r) for r in self.results]
        }
        
        # JSON formatında kaydet
        json_file = self.config.output_file
        if not json_file.endswith('.json'):
            json_file += '.json'
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # TXT formatında da kaydet
        txt_file = json_file.replace('.json', '.txt')
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"MRS DIRB PRO - Tarama Raporu\n")
            f.write(f"{'='*50}\n")
            f.write(f"Hedef: {self.config.base_url}\n")
            f.write(f"Tarih: {self.stats['start_time']}\n")
            f.write(f"Bulunan: {self.stats['found']}\n")
            f.write(f"{'='*50}\n\n")
            
            for r in self.results:
                f.write(f"[{r.status_code}] {r.url}\n")
                if r.title:
                    f.write(f"    Title: {r.title}\n")
                if r.findings:
                    f.write(f"    [!] Bulgular: {', '.join(r.findings)}\n")
                f.write("\n")
        
        console.print(f"[bold green][+] Sonuclar kaydedildi:[/bold green]")
        console.print(f"    - JSON: {json_file}")
        console.print(f"    - TXT: {txt_file}")


# ═══════════════════════════════════════════════════════════════════
#                         ANA GİRİŞ NOKTASI
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="MRS DIRB PRO - Gelişmiş Dizin Keşif Aracı v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım Örnekleri:
  python mrs_dirb_pro.py example.com
  python mrs_dirb_pro.py youtube.com -w custom.txt -t 100
  python mrs_dirb_pro.py hedef.com -m stealth -x .php,.html,.bak
  python mrs_dirb_pro.py site.com -r -d 3 -o results
  
NOT: https:// yazmak zorunda değilsiniz, otomatik eklenir!
        """
    )
    
    parser.add_argument("url", help="Hedef URL (örn: example.com veya https://example.com)")
    parser.add_argument("-w", "--wordlist", default="robots.txt", help="Wordlist dosyası (default: robots.txt)")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Eşzamanlı istek sayısı (default: 50)")
    parser.add_argument("-T", "--timeout", type=int, default=10, help="İstek timeout süresi (default: 10)")
    parser.add_argument("-D", "--delay", type=float, default=0, help="İstekler arası gecikme (saniye)")
    
    parser.add_argument("-m", "--mode", choices=['normal', 'stealth', 'aggressive'],
                       default='normal', help="Tarama modu (default: normal)")
    
    parser.add_argument("-u", "--user-agent", help="Özel User-Agent")
    parser.add_argument("-c", "--cookie", help="Cookie değeri")
    parser.add_argument("-H", "--header", action='append', help="Özel header (Key:Value formatında)")
    
    parser.add_argument("-x", "--extensions", help="Uzantılar (virgülle ayrılmış: .php,.html,.bak)")
    parser.add_argument("-e", "--exclude", help="Hariç tutulacak HTTP kodları (virgülle ayrılmış)")
    
    parser.add_argument("-f", "--follow", action="store_true", help="Yönlendirmeleri takip et")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursive tarama")
    parser.add_argument("-d", "--depth", type=int, default=3, help="Recursive derinlik (default: 3)")
    
    parser.add_argument("-p", "--proxy", help="Proxy URL (örn: http://127.0.0.1:8080)")
    parser.add_argument("-k", "--insecure", action="store_true", help="SSL sertifikasını doğrulama")
    
    parser.add_argument("-o", "--output", help="Çıktı dosyası adı")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Tüm sonuçları göster (varsayılan: sadece 200, 401, 403)")
    
    args = parser.parse_args()
    
    # URL'yi normalize et (https:// yoksa ekle)
    target_url = normalize_url(args.url)
    console.print(f"\n[bold cyan][>] Hedef: {target_url}[/bold cyan]\n")
    
    # Yapılandırma oluştur
    config = ScanConfig(
        base_url=target_url,
        wordlist=args.wordlist,
        threads=args.threads,
        timeout=args.timeout,
        delay=args.delay,
        mode=ScanMode(args.mode),
        user_agent=args.user_agent,
        cookie=args.cookie,
        follow_redirects=args.follow,
        recursive=args.recursive,
        max_depth=args.depth,
        proxy=args.proxy,
        verify_ssl=not args.insecure,
        output_file=args.output,
        verbose=args.verbose
    )
    
    # Uzantıları ayarla
    if args.extensions:
        config.extensions = [ext.strip() if ext.startswith('.') else f'.{ext.strip()}' 
                           for ext in args.extensions.split(',')]
    
    # Hariç tutulacak kodları ayarla
    if args.exclude:
        config.exclude_codes = [int(code.strip()) for code in args.exclude.split(',')]
    
    # Özel header'ları ayarla
    if args.header:
        for h in args.header:
            if ':' in h:
                key, value = h.split(':', 1)
                config.headers[key.strip()] = value.strip()
    
    # Taramayı başlat
    scanner = MRSDirbScanner(config)
    asyncio.run(scanner.scan())


if __name__ == "__main__":
    main()
