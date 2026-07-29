import re
import urllib.request
from urllib.parse import urlparse
import json

domains = set()

def clean_domain(url_str):
    url_str = url_str.strip()
    if not url_str:
        return None
    if not url_str.startswith(('http://', 'https://')):
        url_str = 'http://' + url_str
    try:
        parsed = urlparse(url_str)
        domain = parsed.netloc or parsed.path.split('/')[0]
        domain = domain.split(':')[0].lower() # odstranění portu a převod na malá písmena
        if domain.startswith('www.'):
            domain = domain[4:]
        # Základní validace domény
        if '.' in domain and not domain.startswith('.') and not domain.endswith('.'):
            return domain
    except Exception:
        pass
    return None

# 1. SÚKL (Stahování ze seznamu nelegálních nabídek)
print("Stahuji SÚKL...")
try:
    req = urllib.request.Request(
        'https://sukl.gov.cz/prumysl/leciva/dozor-nad-reklamou/seznam-stranek-s-nelegalni-nabidkou-lecivych-pripravku/',
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8', errors='ignore')
        # Vyhledá všechny odkazu/URL v HTML
        found_urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', html)
        for u in found_urls:
            d = clean_domain(u)
            if d and 'sukl.gov.cz' not in d and 'sukl.cz' not in d:
                domains.add(d)
except Exception as e:
    print(f"Chyba při stahování SÚKL: {e}")

# 2. ČOI (Stahování rizikových e-shopů přes jejich API/JSON feed)
print("Stahuji ČOI...")
try:
    req = urllib.request.Request(
        'https://coi.gov.cz/api/eshops',
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        # ČOI API vrací seznam objektů s položkou 'url' nebo 'domain'
        for item in data:
            target_url = item.get('url') or item.get('domain') or ''
            d = clean_domain(target_url)
            if d:
                domains.add(d)
except Exception as e:
    print(f"Chyba při stahování ČOI: {e}")

# Uložení do souboru
sorted_domains = sorted(list(domains))
with open('blocklist.txt', 'w', encoding='utf-8') as f:
    for domain in sorted_domains:
        f.write(f"{domain}\n")

print(f"Hotovo. Uloženo {len(sorted_domains)} unikátních domén.")
