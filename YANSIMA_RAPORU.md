# Yansıma hesabatı

**AI ən çox harada kömək etdi?** Crawler-in bütün skeletini (səhifələmə, retry, parse funksiyaları, logging) və analiz skriptini bir neçə dəqiqəyə yazdı. Ən faydalısı detal səhifələrinin lazım olduğunu tapşırıqdakı qeydlərdən dərhal çıxarmaq oldu.

**AI harada yanıldı / əskik qaldı?** Analiz skriptində `scipy` asılılığını nəzərə almadı (`Spearman` üçün `ModuleNotFoundError`); `rank()` ilə həll etdim. Həmçinin "ən bahalı 10 kateqoriya" nəticəsində 1 kitablıq kateqoriyalar (Suspense, Novels) birinci çıxdı, bu statistik cəhətdən yanıltıcıdır; qrafikdə `n` göstərdim və README-də xəbərdarlıq yazdım.

**Nəticələrin doğruluğuna necə əmin oldum?** (1) CSV-də 1000 sətir və 1000 unikal URL var, saytın yazdığı 1000 ilə üst-üstə düşür. (2) 50 kateqoriyanın hər birində say saytın kateqoriya səhifəsindəki "N results" ilə eynidir. (3) Boş dəyər yoxdur, qiymət 0–1000 və puan 1–5 aralığında `assert` ilə yoxlanır. (4) Kitab səhifələrini ayrıca iki skriptlə yenidən yoxladım (`recheck_detail.py`: 1000 kitab, `recheck_categories.py`: kateqoriya səhifələri üzərindən), hər ikisi 0 uyğunsuzluq. (5) Son addım kimi Playwright MCP vasitəsilə real Chrome-da 62 kitabı açıb yoxladım (aşağıda).

**Növbəti dəfə nəyi fərqli edərdim?** Detal səhifələrini paralel (məhdud sayda) çəkərdim, çünki ardıcıl crawl ~25 dəqiqə çəkdi. Ara nəticəni (checkpoint) diskə yazardım ki, yarıda kəsilsə baştan başlamayım. Kateqoriya ortalamasında minimum kitab sayı filtri əlavə edərdim.

## Bonus: skill və MCP

- **Nə istifadə etdim:** Claude skill faylı `.claude/skills/scraping-rules/SKILL.md` (layihəyə xas qaydalar: həmişə gözləmə, xətaları logla, retry, encoding, CSV-yə yaz, saytla say müqayisəsi).
- **Necə qurdum:** layihədə `.claude/skills/scraping-rules/` qovluğu yaratdım, içinə `name` və `description` olan frontmatter ilə `SKILL.md` yazdım; Claude Code layihəni açanda avtomatik tapır.
- **Nə qazandırdı:** qaydalar bir yerdə yazılıb, kod həmin qaydalara uyğun yazıldı (gözləmə, retry, log, doğrulama). Skill olmasa bunları hər promptda təkrar yazmalı olardım və `verify.py` kimi yoxlama addımı asanlıqla unudula bilərdi.

### Playwright MCP

- **Nə istifadə etdim:** Microsoft-un Playwright MCP serveri (`@playwright/mcp@0.0.83`), real Chrome-u MCP alətləri (`browser_navigate`, `browser_evaluate`) ilə idarə edir.
- **Necə qurdum:** layihə qovluğunda bir əmr:

  ```bash
  claude mcp add --scope project playwright -- npx -y @playwright/mcp@0.0.83 --browser chrome --headless
  ```

  Bu, layihədəki `.mcp.json` faylına yazılır (fayl təslimə daxildir). Node.js və Chrome lazımdır, ayrıca brauzer yükləməsi yoxdur.
- **Necə işlətdim:** `mcp_verify.py` (köməkçi: `mcp_client.py`) `.mcp.json`-dakı serveri işə salır, saytın "1000 results" yazısını və təsadüfi seçilmiş 60 kitabla birinci və sonuncu kitabı brauzerdə açır. Başlıq, qiymət, puan, kateqoriya və stoku səhifədə göründüyü kimi oxuyub `kitaplar_temiz.csv` ilə müqayisə edir. Qeyd: MCP serverini bu iş sessiyasında Claude-un yerli MCP yükləyicisi yerinə kiçik Python müştərisi ilə çağırdım; server və alətlər eynidir.
- **Nəticə:** 62 kitab, 0 uyğunsuzluq; saytın ümumi sayı 1000. (`mcp_verify_report.csv`)
- **Nə qazandırdı:** əvvəlki yoxlamaların hamısı `requests` ilə eyni texnikadan istifadə edirdi. MCP ilə dəyərləri real brauzerdə (JavaScript icra olunmuş səhifədə) oxudum, yəni scraper-in kodundan müstəqil üçüncü bir yoxlama oldu. Yeni xəta tapmadı, amma əminliyi artırdı. MCP olmasa yoxlamanı ya əl ilə, ya da yenə eyni `requests` yolu ilə edərdim.
