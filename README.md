# books-scraper

books.toscrape.com saytından bütün kitabları (1000) çəkir, CSV-yə yazır, təmizləyir, analiz edir.

## İşə salma

```bash
pip install -r requirements.txt
python scraper.py   # ~20 dəq, kitaplar.csv yaradır (log: scraper.log)
python verify.py    # CSV-ni saytın yazdığı say ilə müqayisə edir
python analyze.py   # təmizləmə, nəticə cədvəlləri, charts/*.png
```

## Fayllar

| Fayl | Məzmun |
|---|---|
| `scraper.py` | crawler (requests + BeautifulSoup), retry, 0.5–1 s gözləmə, logging |
| `kitaplar.csv` | xam nəticə: `kitap_adi, fiyat, puan, stok_durumu, stok_adedi, kategori, url` |
| `verify.py` | yoxlama: ümumi say + 50 kateqoriyanın hər biri |
| `analyze.py` | təmizləmə + 3 sual + qrafiklər |
| `clean_export.py` | xam CSV → `kitaplar_temiz.csv` (adlı sütunlar) + `kitaplar.xlsx` (rəngli başlıq, Excel Table, düsturlu xülasə vərəqləri) |
| `shorten_links.py` | İSTƏYƏ BAĞLI: bit.ly qısa linklər (öz tokeninlə, `BITLY_TOKEN`) |
| `recheck_detail.py`, `recheck_categories.py` | iki müstəqil yoxlama (kitab səhifələri və kateqoriya səhifələri üzərindən) |
| `.mcp.json`, `mcp_verify.py`, `mcp_client.py` | bonus: Playwright MCP serveri və onunla real Chrome-da 62 kitabın yoxlanması (`python mcp_verify.py`, Node.js və Chrome lazımdır) |
| `charts/` | 3 PNG qrafik |
| `sonuc_*.csv`, `kitaplar_temiz.csv` | analiz nəticələri |
| `.claude/skills/scraping-rules/SKILL.md` | bonus: layihə qaydaları (skill) |
| `PROMPT_GUNLUYU.md`, `YANSIMA_RAPORU.md` | təslim sənədləri |

## Necə işləyir

1. Kataloqun 50 səhifəsi "next" linki ilə gəzilir: ad, qiymət, puan (class `Three` → 3).
2. Kateqoriya (breadcrumb) və stok (`In stock (22 available)`) yalnız kitabın öz səhifəsindədir, buna görə 1000 kitab səhifəsi də açılır.
3. Səhifə açılmasa 3 dəfə təkrar olunur, sonra log-lanıb keçilir; boş sahə boş (NaN) qalır.

## Doğrulama nəticəsi

Saytda 1000 nəticə, CSV-də 1000 sətir, 1000 unikal URL; 50 kateqoriyanın hamısında say saytla eynidir (mismatch = 0). Boş dəyər yoxdur.

## Analiz nəticələri

**1. Ən bahalı 10 kateqoriya (orta qiymət, £):** Suspense 58.33 (1 kitab), Novels 54.81 (1), Politics 53.61 (3), Health 51.45 (4), New Adult 46.38 (6), Christian 42.50 (3), Sports and Games 41.17 (5), Self Help 40.62 (5), Travel 39.79 (11), Fantasy 39.59 (48).
Diqqət: ilk iki kateqoriyada cəmi 1 kitab var, buna görə onların "ortalaması" etibarlı deyil. Qrafikdə hər sütunun yanında `n` yazılıb.

**2. Puan paylanması:** 1 ulduz 226, 2 ulduz 196, 3 ulduz 203, 4 ulduz 179, 5 ulduz 196. Paylanma təxminən bərabərdir, heç bir puan qabarıq üstünlük təşkil etmir.

**3. Puanı yüksək kitablar daha bahadır?** Xeyr. Orta qiymət puana görə 34.56–36.09 £ arasındadır (1 ulduz: 34.56, 5 ulduz: 35.37). Korrelyasiya demək olar ki, sıfırdır (Pearson r = 0.028, Spearman ρ = 0.029). Deməli bu sayt üçün puan qiymətin proqnozlaşdırıcısı deyil. Qeyd: saytın puanları və qiymətləri real deyil, təlim üçün yaradılıb; real kitab bazarı haqqında nəticə çıxarmaq olmaz.
