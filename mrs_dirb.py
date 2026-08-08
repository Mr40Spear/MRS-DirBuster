import argparse
import asyncio
import aiohttp
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
import random
import sys
import time
import re


console = Console()

STATUS_DESCRIPTIONS = {
    200: "✅ Erişilebilir (200)",
    204: "⚠️ İçerik yok (204)",
    301: "🔁 Yönlendirme (301)",
    302: "🔁 Yönlendirme (302)",
    401: "🔒 Yetki gerekli (401)",
    403: "⛔ Erişim engellenmiş (403)",
    429: "⚠️ Rate Limit (429)",
    503: "⚠️ Servis Kapalı (503)"
}

ACCEPTED_STATUS_CODES = set(STATUS_DESCRIPTIONS.keys())

def print_ascii_art():
    try:
        with open('mrs_dirb.txt', 'r', encoding='utf-8') as file:
            banners = file.read().strip().split('**********HACK ASCİİ**********')
            art = random.choice(banners)
            console.print(art, style="bold purple")
    except FileNotFoundError:
        console.print("[bold red]mrs_dirb.txt bulunamadı! ASCII gösterilemiyor.[/bold red]")

def clean_wordlist(lines):
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]

def print_index_of(url, items):
    header = Text(f"Dizin listesi bulundu (Index of): {url}", style="bold bright_cyan")
    if not items:
        content = "[dim]İçerik bulunamadı.[/dim]"
    else:
        content = "\n".join(f"• {item}" for item in items)
    panel = Panel(content, title=header, border_style="cyan", expand=False)
    console.print(panel)

async def check_url(session, base_url, endpoint, found_urls, waf_tracker):
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    try:
        start_time = time.monotonic()
        async with session.get(url, timeout=5) as response:
            elapsed = time.monotonic() - start_time
            text = await response.text()

            if response.status in [429, 503]:
                waf_tracker['count'] += 1
                console.print(f"[yellow]WAF/Rate limit uyarısı [{response.status}]: {url}[/yellow]")
            if elapsed > 5:
                waf_tracker['slow_responses'] += 1
                console.print(f"[yellow]Yavaş yanıt uyarısı ({elapsed:.2f}s): {url}[/yellow]")

            if "Index of" in text:
                links = re.findall(r'href="([^"]+)"', text, re.IGNORECASE)
                filtered_links = [link for link in links if link not in ['../', './']]
                full_links = [f"{url.rstrip('/')}/{link.lstrip('/')}" for link in filtered_links]

                print_index_of(url, full_links)

                found_urls.append(f"{url} [Index of detected]")
                found_urls.extend(f"{link} [Index of content]" for link in full_links)
                return

            if response.status in ACCEPTED_STATUS_CODES:
                explanation = STATUS_DESCRIPTIONS.get(response.status, f"{response.status}")
                console.print(f"[bold green]{explanation}[/bold green] → {url}")
                found_urls.append(f"{url} [{response.status} {explanation}]")

    except asyncio.TimeoutError:
        console.print(f"[yellow]Zaman aşımı:[/yellow] {url}")
    except Exception as e:
        console.print(f"[yellow]Hata: {url} - {e}[/yellow]")

async def run_scan(base_url, wordlist_file, user_agent, save_file, cookie):
    print_ascii_art()

    try:
        with open(wordlist_file, 'r', encoding='utf-8') as file:
            endpoints = clean_wordlist(file.readlines())
    except FileNotFoundError:
        console.print(f"[bold red]Wordlist bulunamadı: {wordlist_file}[/bold red]")
        sys.exit(1)

    headers = {"User-Agent": user_agent or "Mozilla/5.0"}
    if cookie:
        headers["Cookie"] = cookie

    found_urls = []
    waf_tracker = {'count': 0, 'slow_responses': 0}

    connector = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[cyan]{task.completed}/{task.total}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Taranıyor...", total=len(endpoints))
            tasks = [
                check_url(session, base_url, endpoint, found_urls, waf_tracker)
                for endpoint in endpoints
            ]
            for coro in asyncio.as_completed(tasks):
                await coro
                progress.advance(task)

    if found_urls and save_file:
        with open(save_file, "w", encoding="utf-8") as f:
            f.write("\n".join(found_urls))
        console.print(f"\n[bold green]Bulunan URL'ler kaydedildi: {save_file}[/bold green]")
    elif not found_urls:
        console.print(f"\n[bold red]Hiçbir uygun sonuç bulunamadı.[/bold red]")

    if waf_tracker['count'] > 3:
        console.print(f"\n[bold yellow]Uyarı: Çok sayıda WAF/Rate limit yanıtı algılandı! ({waf_tracker['count']} adet)[/bold yellow]")
    if waf_tracker['slow_responses'] > 3:
        console.print(f"\n[bold yellow]Uyarı: Çok sayıda yavaş yanıt tespit edildi! ({waf_tracker['slow_responses']} adet)[/bold yellow]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MRS DIRB async gelişmiş - gerçek dizin tespiti, cookie ve WAF algılama")
    parser.add_argument("-a", "--alternate", help="Kelime listesi yolu", default="robots.txt")
    parser.add_argument("-u", "--useragent", help="Özel User-Agent belirt")
    parser.add_argument("-c", "--cookie", help="Cookie bilgisini belirt (isteğe bağlı)")
    parser.add_argument("-f", "--file", nargs="?", const="found_urls.txt", help="Bulunan URL'leri dosyaya kaydet. Dosya adı belirtilmezse 'found_urls.txt' kullanılır.")
    parser.add_argument("base_url", nargs="?", help="Hedef URL")

    args = parser.parse_args()

    if not args.base_url:
        parser.print_help()
        sys.exit(1)

    asyncio.run(run_scan(args.base_url, args.alternate, args.useragent, args.file, args.cookie))
