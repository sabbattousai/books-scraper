# Prompt günlüyü

Bu layihə **bir ətraflı əsas prompt** ilə həll olundu. Qısa və dəqiq təlimat dəstləri işi addımlara bölməkdən daha yaxşı nəticə verdi, çünki AI bütün tələbləri bir yerdə görüb düzgün arxitektura seçdi.

## Əsas prompt (qısaldılmış mətn)

> Sən təcrübəli software engineersən, data crawling və ingest üzrə ekspertsən. `https://books.toscrape.com/` saytından bütün kitablar üçün **ad, qiymət, puan (1–5 rəqəm), stok, kateqoriya** çək; `kitaplar.csv` kimi saxla (qiymət və puan rəqəmli: `51.77`, `3`). Analiz: ən bahalı 10 kateqoriyanın orta qiyməti, puan paylanması, "yüksək puanlı kitablar daha bahadır?". Texniki qaydalar: xəta idarəsi (səhifə açılmasa və ya sahə boş olsa proqram çökməsin), sorğular arasında 0.5–1 s gözləmə, Python (requests + BeautifulSoup, pandas, matplotlib). Bütün səhifələri gəz, əskik olmasın; ümumi sayı saytla müqayisə et. Bəzi məlumatlar kitabın öz səhifəsindədir. Təslim: kod + README, CSV, qrafiklər, prompt günlüyü, yansıma hesabatı. Bonus üçün skill/MCP.

**AI nə istehsal etdi:** `scraper.py` (səhifələmə "next" linki ilə, hər kitabın səhifəsindən kateqoriya və stok, retry və logging), `verify.py` (saytla say müqayisəsi), `analyze.py`, `requirements.txt`, skill faylı.

**Çalışdı?** Bəli. 1000 kitab, 0 boş dəyər, saytın saynı və 50 kateqoriyanın hər birini tutdu. İlk cəhddə düzəliş tələb etmədi.

## Davamı: qısa dəqiqləşdirmələr

| # | Prompt | Nəticə |
|---|---|---|
| 2 | "CSV-ləri səliqəyə sal, sütunlara ad ver, cədvəli rəngli və dinamik et, formatları düzəlt, iki dəfə sıfırdan yoxla" | `clean_export.py` → `kitaplar_temiz.csv` və `kitaplar.xlsx` (Excel Table, düsturlu xülasə vərəqləri); `recheck_detail.py` və `recheck_categories.py` iki müstəqil yoxlama, 0 uyğunsuzluq |
| 3 | "Qrafiklər çox sadədir, daha dizaynlı, estetik, minimalist et" | `analyze.py` yenidən yazıldı: bir rəng ailəsi, çərçivəsiz, birbaşa etiketlər, nəticəni deyən başlıqlar; kiçik nümunəli kateqoriyalar açıq rənglə |
| 4 | "Müəllim demişdi: `51.77`, `£51.77` yox; cədvəldə funt işarəsi olmasın" | Excel rəqəm formatı `0.00`-a çevrildi, CSV artıq rəqəm idi |
| 5 | "Playwright MCP qoş, son dəfə yoxla, MCP istifadəmizi yazılara əlavə et" | `.mcp.json` (pinlənmiş versiya), `mcp_verify.py`: real Chrome-da 62 kitab yoxlandı, 0 uyğunsuzluq; README və yansıma hesabatı yeniləndi |

## Qarşılaşılan xətalar və düzəlişləri

| Xəta | Səbəb | Düzəliş |
|---|---|---|
| `ModuleNotFoundError: No module named 'scipy'` (Spearman korrelyasiyası) | pandas `corr(method="spearman")` scipy tələb edir | `df["puan"].rank().corr(df["fiyat"].rank())` — riyazi olaraq eynidir, əlavə asılılıq yoxdur |
| `UnicodeEncodeError: 'charmap' codec can't encode...` (Windows konsolu) | konsol cp1252, mətndə `ı`, `ə` | Çap edən sətir götürüldü / `PYTHONIOENCODING=utf-8` |
| Qrafikdə rəqəm etiketləri üst-üstə düşürdü | ilk dizayn versiyası | Etiketləri sabit sütuna çəkdim, kənar xətti sildim, baxıb yenidən yoxladım |
