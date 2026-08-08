#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║     MRS Wordlist Optimizer Pro v2.0                              ║
║     Akıllı wordlist temizleme ve optimizasyon                    ║
╚══════════════════════════════════════════════════════════════════╝
"""

import re
import argparse
import json
from pathlib import Path
from collections import Counter
from datetime import datetime
from typing import List, Set, Dict, Optional, Tuple
from dataclasses import dataclass, field


# ═══════════════════════════════════════════════════════════════════
#                         YAPILANDIRMA
# ═══════════════════════════════════════════════════════════════════

@dataclass
class OptimizationConfig:
    """Optimizasyon yapılandırması"""
    input_file: str
    output_file: str = "optimized_wordlist.txt"
    min_length: int = 1
    max_length: int = 100
    remove_duplicates: bool = True
    lowercase: bool = True
    remove_extensions: bool = False
    add_extensions: List[str] = field(default_factory=list)
    remove_patterns: List[str] = field(default_factory=list)
    keep_patterns: List[str] = field(default_factory=list)
    sort_output: bool = True
    generate_variants: bool = False


@dataclass
class OptimizationStats:
    """İstatistikler"""
    original_count: int = 0
    cleaned_count: int = 0
    duplicates_removed: int = 0
    trash_removed: int = 0
    too_short: int = 0
    too_long: int = 0
    pattern_removed: int = 0
    variants_added: int = 0


# ═══════════════════════════════════════════════════════════════════
#                         ÇÖPLER VE DESENLER
# ═══════════════════════════════════════════════════════════════════

# Saçmalık kelimeleri
TRASH_KEYWORDS = [
    'asdf', 'qwerty', 'zxcvbnm', 'xxx', 'zzz', 'test123', 'temp123',
    'aaa', 'bbb', 'ccc', 'abc123', 'password123', '123456', 'qazwsx',
    'sample', 'example', 'testfile', 'newfile', 'untitled', 'copy',
    'backup_old', 'backup_backup', 'temp_temp', 'new_new'
]

# Kaldırılacak önekler
TRASH_PREFIXES = [
    '~', '..', '._', '.~', '#', '@', '%', '$temp', '_backup',
]

# Kaldırılacak sonekler
TRASH_SUFFIXES = [
    '.swp', '.swo', '.tmp~', '.bak~', '~', '.old.old', 
    '.backup.backup', '.orig.orig'
]

# Çöp desenleri (regex)
TRASH_PATTERNS = [
    r'^\.{2,}',           # Birden fazla nokta ile başlayanlar
    r'^_{2,}',            # Birden fazla alt çizgi ile başlayanlar
    r'\d{10,}',           # 10+ haneli sayılar
    r'^[a-z]{1,2}$',      # 1-2 karakterli anlamsızlar
    r'^[0-9]+$',          # Sadece sayılardan oluşanlar
    r'\.{3,}',            # 3+ nokta içerenler
    r'[^\x00-\x7F]+',     # ASCII olmayan karakterler
    r'\s{2,}',            # Birden fazla boşluk
    r'^\-+$',             # Sadece tire
    r'^_+$',              # Sadece alt çizgi
]

# Önemli / korunması gereken desenler
IMPORTANT_PATTERNS = [
    r'admin', r'login', r'dashboard', r'api', r'config', r'backup',
    r'database', r'db', r'sql', r'php', r'asp', r'jsp', r'cgi',
    r'upload', r'file', r'download', r'user', r'pass', r'secret',
    r'\.git', r'\.env', r'\.htaccess', r'\.htpasswd', r'wp-',
    r'phpmyadmin', r'mysql', r'postgres', r'oracle', r'mssql',
    r'shell', r'cmd', r'exec', r'eval', r'system', r'root',
    r'ftp', r'ssh', r'sftp', r'telnet', r'vnc', r'rdp',
    r'jenkins', r'gitlab', r'jira', r'confluence', r'bitbucket',
]

# Yaygın web yolları - bunlar korunmalı
COMMON_WEB_PATHS = {
    'admin', 'administrator', 'login', 'dashboard', 'panel',
    'api', 'v1', 'v2', 'v3', 'rest', 'graphql', 'swagger',
    'config', 'configuration', 'settings', 'setup', 'install',
    'backup', 'backups', 'bak', 'old', 'archive', 'archives',
    'upload', 'uploads', 'file', 'files', 'download', 'downloads',
    'user', 'users', 'account', 'accounts', 'profile', 'profiles',
    'image', 'images', 'img', 'photo', 'photos', 'media',
    'js', 'javascript', 'css', 'style', 'styles', 'font', 'fonts',
    'lib', 'libs', 'library', 'vendor', 'vendors', 'node_modules',
    'include', 'includes', 'inc', 'common', 'shared', 'assets',
    'public', 'static', 'resource', 'resources', 'res',
    'template', 'templates', 'theme', 'themes', 'layout', 'layouts',
    'plugin', 'plugins', 'module', 'modules', 'component', 'components',
    'test', 'tests', 'testing', 'debug', 'dev', 'development',
    'doc', 'docs', 'documentation', 'help', 'faq', 'support',
    'log', 'logs', 'logging', 'error', 'errors', 'report', 'reports',
    'tmp', 'temp', 'cache', 'caches', 'session', 'sessions',
    'data', 'database', 'db', 'sql', 'mysql', 'postgres',
    'app', 'application', 'apps', 'webapp', 'webapps',
    'service', 'services', 'srv', 'server', 'servers',
    'bin', 'cgi', 'cgi-bin', 'scripts', 'script', 'cmd',
    'private', 'secure', 'secret', 'hidden', 'internal',
    'portal', 'intranet', 'extranet', 'webmail', 'mail',
    '.git', '.svn', '.hg', '.env', '.htaccess', '.htpasswd',
    'robots.txt', 'sitemap.xml', 'crossdomain.xml', 'security.txt',
    'wp-admin', 'wp-content', 'wp-includes', 'wp-login',
    'phpmyadmin', 'pma', 'adminer', 'phpinfo',
    'jenkins', 'gitlab', 'jira', 'confluence', 'bitbucket',
    'console', 'manager', 'status', 'health', 'info', 'version',
}


# ═══════════════════════════════════════════════════════════════════
#                         ANA SINIF
# ═══════════════════════════════════════════════════════════════════

class WordlistOptimizer:
    """Gelişmiş wordlist optimizer"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.stats = OptimizationStats()
        self.words: Set[str] = set()
        self.removed_words: List[Tuple[str, str]] = []  # (word, reason)
    
    def _is_important(self, word: str) -> bool:
        """Önemli kelime mi kontrol et"""
        word_lower = word.lower()
        
        # Yaygın web yolları kontrolü
        base_word = word_lower.rstrip('/').split('/')[-1].split('.')[0]
        if base_word in COMMON_WEB_PATHS:
            return True
        
        # Önemli desen kontrolü
        for pattern in IMPORTANT_PATTERNS:
            if re.search(pattern, word_lower):
                return True
        
        return False
    
    def _is_trash(self, word: str) -> Tuple[bool, str]:
        """Çöp kelime mi kontrol et"""
        word_lower = word.lower()
        original = word.strip()
        
        # Boş satır veya yorum
        if not original or original.startswith('#'):
            return True, "boş veya yorum"
        
        # Önemli kelime ise atla
        if self._is_important(original):
            return False, ""
        
        # Uzunluk kontrolü
        if len(original) < self.config.min_length:
            self.stats.too_short += 1
            return True, f"çok kısa ({len(original)} < {self.config.min_length})"
        
        if len(original) > self.config.max_length:
            self.stats.too_long += 1
            return True, f"çok uzun ({len(original)} > {self.config.max_length})"
        
        # Çöp anahtar kelimeler
        for trash in TRASH_KEYWORDS:
            if trash in word_lower:
                return True, f"çöp kelime: {trash}"
        
        # Çöp önekler
        for prefix in TRASH_PREFIXES:
            if original.startswith(prefix):
                return True, f"çöp önek: {prefix}"
        
        # Çöp sonekler
        for suffix in TRASH_SUFFIXES:
            if original.endswith(suffix):
                return True, f"çöp sonek: {suffix}"
        
        # Çöp desenleri
        for pattern in TRASH_PATTERNS:
            if re.search(pattern, original):
                return True, f"çöp desen: {pattern}"
        
        # Kullanıcı tanımlı kaldırma desenleri
        for pattern in self.config.remove_patterns:
            if re.search(pattern, original, re.IGNORECASE):
                self.stats.pattern_removed += 1
                return True, f"kullanıcı deseni: {pattern}"
        
        # Kullanıcı tanımlı koruma desenleri
        for pattern in self.config.keep_patterns:
            if re.search(pattern, original, re.IGNORECASE):
                return False, ""
        
        # Çok fazla özel karakter
        special_chars = len(re.findall(r'[^a-zA-Z0-9_\-/\.]', original))
        if special_chars > 3:
            return True, f"çok fazla özel karakter ({special_chars})"
        
        # Çok fazla nokta
        if original.count('.') > 3:
            return True, f"çok fazla nokta ({original.count('.')})"
        
        return False, ""
    
    def _normalize(self, word: str) -> str:
        """Kelimeyi normalize et"""
        word = word.strip()
        
        # Lowercase
        if self.config.lowercase:
            word = word.lower()
        
        # Sondaki slash'ları temizle
        word = word.rstrip('/')
        
        # Baştaki slash'ları temizle (opsiyonel)
        word = word.lstrip('/')
        
        return word
    
    def _generate_variants(self, word: str) -> List[str]:
        """Kelime varyantları oluştur"""
        variants = [word]
        
        # Uzantısız ve uzantılı versiyonlar
        if '.' in word:
            base = word.rsplit('.', 1)[0]
            variants.append(base)
        
        # Slash ile ve slash'sız
        if not word.endswith('/'):
            variants.append(word + '/')
        
        # Büyük/küçük harf varyantları
        variants.append(word.upper())
        variants.append(word.capitalize())
        
        # Alt çizgi ve tire dönüşümleri
        if '_' in word:
            variants.append(word.replace('_', '-'))
        if '-' in word:
            variants.append(word.replace('-', '_'))
        
        return variants
    
    def load(self) -> None:
        """Wordlist'i yükle"""
        try:
            with open(self.config.input_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            self.stats.original_count = len(lines)
            print(f"📥 Yüklendi: {self.config.input_file} ({len(lines)} satır)")
            
            for line in lines:
                word = self._normalize(line)
                
                if not word:
                    continue
                
                is_trash, reason = self._is_trash(word)
                
                if is_trash:
                    self.stats.trash_removed += 1
                    self.removed_words.append((word, reason))
                else:
                    if word in self.words:
                        self.stats.duplicates_removed += 1
                    else:
                        self.words.add(word)
                        
                        # Varyant oluştur
                        if self.config.generate_variants:
                            for variant in self._generate_variants(word):
                                if variant not in self.words:
                                    self.words.add(variant)
                                    self.stats.variants_added += 1
            
            # Uzantı ekle
            if self.config.add_extensions:
                extended = set()
                for word in self.words:
                    extended.add(word)
                    for ext in self.config.add_extensions:
                        if not word.endswith(ext):
                            ext = ext if ext.startswith('.') else f'.{ext}'
                            extended.add(f"{word}{ext}")
                self.words = extended
            
            self.stats.cleaned_count = len(self.words)
            
        except FileNotFoundError:
            print(f"❌ Dosya bulunamadı: {self.config.input_file}")
            raise
    
    def save(self) -> None:
        """Optimize edilmiş wordlist'i kaydet"""
        words_list = list(self.words)
        
        if self.config.sort_output:
            words_list.sort()
        
        with open(self.config.output_file, 'w', encoding='utf-8') as f:
            for word in words_list:
                f.write(word + '\n')
        
        print(f"💾 Kaydedildi: {self.config.output_file}")
    
    def print_stats(self) -> None:
        """İstatistikleri yazdır"""
        print("\n" + "="*60)
        print("📊 OPTİMİZASYON İSTATİSTİKLERİ")
        print("="*60)
        print(f"📄 Orijinal satır sayısı    : {self.stats.original_count:,}")
        print(f"✅ Temizlenmiş satır sayısı : {self.stats.cleaned_count:,}")
        print(f"🗑️  Çöp kaldırılan          : {self.stats.trash_removed:,}")
        print(f"🔄 Tekrar kaldırılan        : {self.stats.duplicates_removed:,}")
        print(f"📏 Çok kısa                 : {self.stats.too_short:,}")
        print(f"📏 Çok uzun                 : {self.stats.too_long:,}")
        print(f"🔍 Desen ile kaldırılan     : {self.stats.pattern_removed:,}")
        print(f"➕ Varyant eklenen          : {self.stats.variants_added:,}")
        
        reduction = ((self.stats.original_count - self.stats.cleaned_count) / 
                    self.stats.original_count * 100) if self.stats.original_count > 0 else 0
        print(f"\n📉 Boyut azaltma: %{reduction:.1f}")
        print("="*60)
    
    def save_removed_report(self, filepath: str = "removed_words.txt") -> None:
        """Kaldırılan kelimelerin raporunu kaydet"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"MRS Wordlist Optimizer - Kaldırılan Kelimeler Raporu\n")
            f.write(f"Tarih: {datetime.now().isoformat()}\n")
            f.write(f"Kaynak: {self.config.input_file}\n")
            f.write(f"Toplam kaldırılan: {len(self.removed_words)}\n")
            f.write("="*60 + "\n\n")
            
            # Sebeplere göre grupla
            by_reason: Dict[str, List[str]] = {}
            for word, reason in self.removed_words:
                if reason not in by_reason:
                    by_reason[reason] = []
                by_reason[reason].append(word)
            
            for reason, words in sorted(by_reason.items(), key=lambda x: -len(x[1])):
                f.write(f"\n[{reason}] ({len(words)} adet)\n")
                f.write("-"*40 + "\n")
                for word in words[:50]:  # İlk 50'yi göster
                    f.write(f"  {word}\n")
                if len(words) > 50:
                    f.write(f"  ... ve {len(words) - 50} tane daha\n")
        
        print(f"📋 Kaldırılan kelimeler raporu: {filepath}")
    
    def analyze(self) -> Dict:
        """Wordlist analizi yap"""
        analysis = {
            'total_words': len(self.words),
            'avg_length': 0,
            'min_length': 0,
            'max_length': 0,
            'extension_counts': Counter(),
            'prefix_counts': Counter(),
            'depth_distribution': Counter(),
        }
        
        if not self.words:
            return analysis
        
        lengths = [len(w) for w in self.words]
        analysis['avg_length'] = sum(lengths) / len(lengths)
        analysis['min_length'] = min(lengths)
        analysis['max_length'] = max(lengths)
        
        for word in self.words:
            # Uzantı analizi
            if '.' in word:
                ext = '.' + word.rsplit('.', 1)[1]
                analysis['extension_counts'][ext] += 1
            else:
                analysis['extension_counts']['[no extension]'] += 1
            
            # Önek analizi (ilk klasör)
            parts = word.strip('/').split('/')
            if parts:
                analysis['prefix_counts'][parts[0]] += 1
            
            # Derinlik dağılımı
            depth = word.count('/')
            analysis['depth_distribution'][depth] += 1
        
        return analysis
    
    def print_analysis(self) -> None:
        """Analiz sonuçlarını yazdır"""
        analysis = self.analyze()
        
        print("\n" + "="*60)
        print("🔍 WORDLIST ANALİZİ")
        print("="*60)
        print(f"📊 Toplam kelime: {analysis['total_words']:,}")
        print(f"📏 Ortalama uzunluk: {analysis['avg_length']:.1f}")
        print(f"📏 Min/Max uzunluk: {analysis['min_length']}/{analysis['max_length']}")
        
        print("\n🗂️ En yaygın uzantılar:")
        for ext, count in analysis['extension_counts'].most_common(10):
            print(f"    {ext}: {count:,}")
        
        print("\n📁 En yaygın önekler:")
        for prefix, count in analysis['prefix_counts'].most_common(10):
            print(f"    /{prefix}: {count:,}")
        
        print("\n📊 Derinlik dağılımı:")
        for depth, count in sorted(analysis['depth_distribution'].items()):
            bar = "█" * min(count // 100, 30)
            print(f"    Seviye {depth}: {count:,} {bar}")
        
        print("="*60)


# ═══════════════════════════════════════════════════════════════════
#                         ÖZEL LİSTELER
# ═══════════════════════════════════════════════════════════════════

def generate_common_wordlist(output_path: str = "common_paths.txt") -> None:
    """Yaygın web yollarından wordlist oluştur"""
    paths = set()
    
    # Temel yollar
    paths.update(COMMON_WEB_PATHS)
    
    # Uzantılı versiyonlar
    extensions = ['.php', '.asp', '.aspx', '.jsp', '.html', '.htm', '.txt', 
                  '.xml', '.json', '.yml', '.yaml', '.cfg', '.conf', '.bak',
                  '.old', '.backup', '.orig', '.sql', '.db', '.log']
    
    for path in list(COMMON_WEB_PATHS):
        for ext in extensions:
            paths.add(f"{path}{ext}")
    
    # Yaygın kombinasyonlar
    prefixes = ['', 'admin/', 'api/', 'v1/', 'v2/', 'app/', 'web/', 'public/']
    for prefix in prefixes:
        for path in ['config', 'settings', 'database', 'backup', 'upload', 'files']:
            paths.add(f"{prefix}{path}")
    
    # Sırala ve kaydet
    sorted_paths = sorted(paths)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted_paths))
    
    print(f"✅ Yaygın yollar listesi oluşturuldu: {output_path} ({len(sorted_paths)} yol)")


def merge_wordlists(files: List[str], output: str = "merged_wordlist.txt") -> None:
    """Birden fazla wordlist'i birleştir"""
    all_words = set()
    
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                words = {line.strip().lower() for line in f if line.strip() and not line.startswith('#')}
                print(f"📥 {filepath}: {len(words):,} kelime")
                all_words.update(words)
        except FileNotFoundError:
            print(f"⚠️ Dosya bulunamadı: {filepath}")
    
    sorted_words = sorted(all_words)
    
    with open(output, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted_words))
    
    print(f"✅ Birleştirildi: {output} ({len(sorted_words):,} benzersiz kelime)")


# ═══════════════════════════════════════════════════════════════════
#                         ANA GİRİŞ NOKTASI
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="MRS Wordlist Optimizer Pro v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım Örnekleri:
  python wordlist_optimizer.py robots.txt
  python wordlist_optimizer.py wordlist.txt -o clean.txt --min 3 --max 50
  python wordlist_optimizer.py wordlist.txt -x .php,.html,.bak
  python wordlist_optimizer.py wordlist.txt --remove "test|sample" --keep "admin|config"
  python wordlist_optimizer.py --generate-common
  python wordlist_optimizer.py --merge list1.txt list2.txt -o merged.txt
        """
    )
    
    parser.add_argument("input", nargs="?", help="Giriş wordlist dosyası")
    parser.add_argument("-o", "--output", default="optimized_wordlist.txt", help="Çıkış dosyası")
    
    parser.add_argument("--min", type=int, default=1, help="Minimum kelime uzunluğu")
    parser.add_argument("--max", type=int, default=100, help="Maximum kelime uzunluğu")
    
    parser.add_argument("-x", "--extensions", help="Eklenecek uzantılar (virgülle ayrılmış)")
    parser.add_argument("--remove", help="Kaldırılacak desen (regex)")
    parser.add_argument("--keep", help="Korunacak desen (regex)")
    
    parser.add_argument("--variants", action="store_true", help="Varyantlar oluştur")
    parser.add_argument("--no-sort", action="store_true", help="Sıralama yapma")
    parser.add_argument("--no-lowercase", action="store_true", help="Küçük harfe çevirme")
    
    parser.add_argument("--report", action="store_true", help="Kaldırılan kelimeler raporu")
    parser.add_argument("--analyze", action="store_true", help="Wordlist analizi yap")
    
    parser.add_argument("--generate-common", action="store_true", help="Yaygın yollar listesi oluştur")
    parser.add_argument("--merge", nargs='+', help="Wordlist'leri birleştir")
    
    args = parser.parse_args()
    
    # Yaygın yollar oluştur
    if args.generate_common:
        generate_common_wordlist()
        return
    
    # Birleştirme
    if args.merge:
        merge_wordlists(args.merge, args.output)
        return
    
    # Normal optimizasyon
    if not args.input:
        parser.print_help()
        return
    
    config = OptimizationConfig(
        input_file=args.input,
        output_file=args.output,
        min_length=args.min,
        max_length=args.max,
        lowercase=not args.no_lowercase,
        sort_output=not args.no_sort,
        generate_variants=args.variants,
    )
    
    if args.extensions:
        config.add_extensions = [ext.strip() for ext in args.extensions.split(',')]
    
    if args.remove:
        config.remove_patterns = args.remove.split('|')
    
    if args.keep:
        config.keep_patterns = args.keep.split('|')
    
    # Optimizasyon
    optimizer = WordlistOptimizer(config)
    optimizer.load()
    optimizer.save()
    optimizer.print_stats()
    
    if args.analyze:
        optimizer.print_analysis()
    
    if args.report:
        optimizer.save_removed_report()


if __name__ == "__main__":
    main()
