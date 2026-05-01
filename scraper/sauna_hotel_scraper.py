"""
客室サウナ付き宿泊施設 データ収集スクレイパー
対象: トマレルサウナ（都道府県別ページ）+ じゃらん・旅色
出力: scraper/data/sauna_hotels.csv
"""

import asyncio
import csv
import re
from collections import Counter
from playwright.async_api import async_playwright

OUTPUT_FILE = "scraper/data/sauna_hotels.csv"
HEADERS = ["施設名", "都道府県", "施設タイプ", "価格_目安", "評点", "サウナタイプ", "ソース", "URL"]

PREFECTURES = [
    ("北海道", "hokkaido"), ("青森", "aomori"), ("岩手", "iwate"), ("宮城", "miyagi"),
    ("秋田", "akita"), ("山形", "yamagata"), ("福島", "fukushima"), ("茨城", "ibaraki"),
    ("栃木", "tochigi"), ("群馬", "gunma"), ("埼玉", "saitama"), ("千葉", "chiba"),
    ("東京", "tokyo"), ("神奈川", "kanagawa"), ("新潟", "niigata"), ("富山", "toyama"),
    ("石川", "ishikawa"), ("福井", "fukui"), ("山梨", "yamanashi"), ("長野", "nagano"),
    ("岐阜", "gifu"), ("静岡", "shizuoka"), ("愛知", "aichi"), ("三重", "mie"),
    ("滋賀", "shiga"), ("京都", "kyoto"), ("大阪", "osaka"), ("兵庫", "hyogo"),
    ("奈良", "nara"), ("和歌山", "wakayama"), ("鳥取", "tottori"), ("島根", "shimane"),
    ("岡山", "okayama"), ("広島", "hiroshima"), ("山口", "yamaguchi"), ("徳島", "tokushima"),
    ("香川", "kagawa"), ("愛媛", "ehime"), ("高知", "kochi"), ("福岡", "fukuoka"),
    ("佐賀", "saga"), ("長崎", "nagasaki"), ("熊本", "kumamoto"), ("大分", "oita"),
    ("宮崎", "miyazaki"), ("鹿児島", "kagoshima"), ("沖縄", "okinawa"),
]

# 施設名として除外するキーワード
SKIP_KEYWORDS = ["一覧", "特徴", "施設情報", "おすすめ", "まとめ", "について", "とは", "アクセス", "料金", "プラン", "客室", "お問い合わせ"]


def is_facility_name(text):
    text = text.strip()
    if len(text) < 2 or len(text) > 60:
        return False
    if any(k in text for k in SKIP_KEYWORDS):
        return False
    return True


def guess_type(name):
    if any(k in name for k in ["グランピング", "Glamping", "GLAMPING"]):
        return "グランピング"
    if any(k in name for k in ["ヴィラ", "Villa", "VILLA", "ビラ"]):
        return "ヴィラ"
    if any(k in name for k in ["旅館", "温泉", "の宿", "Ryokan", "別邸", "別荘"]):
        return "旅館"
    if any(k in name for k in ["ホテル", "Hotel", "HOTEL", "Inn", "INN", "リゾート", "Resort"]):
        return "ホテル"
    if any(k in name for k in ["コテージ", "Cabin", "CABIN", "キャビン", "古民家", "一棟", "貸"]):
        return "一棟貸し"
    return "その他"


async def scrape_tomarerusauna(page):
    """トマレルサウナ: 全都道府県の施設名を収集"""
    results = []
    print("[トマレルサウナ] 全都道府県ページを収集中...")

    for pref_ja, pref_en in PREFECTURES:
        url = f"https://tomarerusauna.com/private-{pref_en}/"
        try:
            resp = await page.goto(url, timeout=20000, wait_until="domcontentloaded")
            await page.wait_for_timeout(1000)

            # 404チェック
            if resp and resp.status == 404:
                print(f"  {pref_ja}: ページなし（スキップ）")
                continue

            article = await page.query_selector("article")
            if not article:
                print(f"  {pref_ja}: article要素なし")
                continue

            headers = await article.query_selector_all("h2, h3")
            pref_count = 0
            for h in headers:
                text = (await h.inner_text()).strip()
                if is_facility_name(text):
                    # 価格情報を次の要素から探す
                    price = ""
                    try:
                        sibling_text = await h.evaluate("""
                            el => {
                                let next = el.nextElementSibling;
                                let texts = [];
                                for (let i = 0; i < 5 && next; i++) {
                                    texts.push(next.innerText);
                                    next = next.nextElementSibling;
                                }
                                return texts.join(' ');
                            }
                        """)
                        price_match = re.search(r'[¥￥]?([\d,]+)円', sibling_text)
                        if price_match:
                            price = price_match.group(1).replace(',', '')
                    except Exception:
                        pass

                    results.append({
                        "施設名": text,
                        "都道府県": pref_ja,
                        "施設タイプ": guess_type(text),
                        "価格_目安": price,
                        "評点": "",
                        "サウナタイプ": "プライベートサウナ",
                        "ソース": "トマレルサウナ",
                        "URL": url,
                    })
                    pref_count += 1

            print(f"  {pref_ja}: {pref_count}施設")

        except Exception as e:
            print(f"  {pref_ja}: エラー {e}")

        await page.wait_for_timeout(500)

    return results


async def scrape_jalan(page):
    """じゃらん: 客室サウナ特集ページ（複数ページ）"""
    results = []
    print("[じゃらん] スクレイピング中...")

    for pg in range(1, 5):
        url = f"https://www.jalan.net/keyword/key0013575/?p={pg}"
        try:
            await page.goto(url, timeout=25000, wait_until="networkidle")
            await page.wait_for_timeout(2000)

            # 施設名の候補セレクター
            items = await page.query_selector_all(".jlnpc-search-result-item__name, .yadList_name, h3.yadName, .searchResultList__item a.name, [class*='hotel-name'], [class*='hotelName']")

            if not items:
                # フォールバック：メインコンテンツ内のリンク
                items = await page.query_selector_all("main a[href*='/yado/'], #main a[href*='/yado/']")

            for item in items:
                text = (await item.inner_text()).strip()
                href = await item.get_attribute("href") or ""
                if text and len(text) > 2 and len(text) < 50 and '/yado/' in href:
                    results.append({
                        "施設名": text,
                        "都道府県": "",
                        "施設タイプ": guess_type(text),
                        "価格_目安": "",
                        "評点": "",
                        "サウナタイプ": "客室サウナ",
                        "ソース": "じゃらん",
                        "URL": f"https://www.jalan.net{href}" if href.startswith("/") else href,
                    })

            print(f"  ページ{pg}: 計{len(results)}件")
            if not items:
                break

        except Exception as e:
            print(f"  ページ{pg}: エラー {e}")

        await page.wait_for_timeout(1500)

    return results


async def scrape_sauna_ikitai(page):
    """サウナイキタイ: プライベートコテージ一覧"""
    results = []
    print("[サウナイキタイ] スクレイピング中...")

    for pg in range(1, 6):
        url = f"https://sauna-ikitai.com/privatecottage?ordering=ikitai_counts_desc&page={pg}"
        try:
            await page.goto(url, timeout=25000, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            items = await page.query_selector_all(".p-facility-card__name, .facility-name, h3, [class*='facility'] a, [class*='card'] h2, [class*='card'] h3")

            for item in items:
                text = (await item.inner_text()).strip()
                href = await item.get_attribute("href") or ""
                if not href:
                    parent_a = await item.query_selector("a")
                    if parent_a:
                        href = await parent_a.get_attribute("href") or ""

                if text and len(text) > 2 and len(text) < 60 and is_facility_name(text):
                    pref = ""
                    # 隣接要素から都道府県を推定
                    try:
                        nearby = await item.evaluate("""
                            el => el.closest('[class*="card"], article, li')?.innerText || ''
                        """)
                        pref = extract_pref(nearby)
                    except Exception:
                        pass

                    results.append({
                        "施設名": text,
                        "都道府県": pref,
                        "施設タイプ": guess_type(text),
                        "価格_目安": "",
                        "評点": "",
                        "サウナタイプ": "プライベートサウナ",
                        "ソース": "サウナイキタイ",
                        "URL": href,
                    })

            print(f"  ページ{pg}: 計{len(results)}件")
            if len(items) < 5:
                break

        except Exception as e:
            print(f"  ページ{pg}: エラー {e}")

        await page.wait_for_timeout(1000)

    return results


def extract_pref(text):
    prefs = ["北海道","青森","岩手","宮城","秋田","山形","福島","茨城","栃木","群馬",
             "埼玉","千葉","東京","神奈川","新潟","富山","石川","福井","山梨","長野",
             "岐阜","静岡","愛知","三重","滋賀","京都","大阪","兵庫","奈良","和歌山",
             "鳥取","島根","岡山","広島","山口","徳島","香川","愛媛","高知","福岡",
             "佐賀","長崎","熊本","大分","宮崎","鹿児島","沖縄"]
    for p in prefs:
        if p in text:
            return p
    return ""


def deduplicate(data):
    seen = set()
    out = []
    for d in data:
        key = d["施設名"].strip()
        if key and key not in seen:
            seen.add(key)
            out.append(d)
    return out


async def main():
    import os
    os.makedirs("scraper/data", exist_ok=True)

    all_results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ja-JP",
            viewport={"width": 1280, "height": 900}
        )
        page = await context.new_page()

        print("=== スクレイピング開始 ===\n")

        r1 = await scrape_tomarerusauna(page)
        all_results.extend(r1)
        print(f"\nトマレルサウナ: {len(r1)}件\n")

        r2 = await scrape_jalan(page)
        all_results.extend(r2)
        print(f"\nじゃらん: {len(r2)}件\n")

        r3 = await scrape_sauna_ikitai(page)
        all_results.extend(r3)
        print(f"\nサウナイキタイ: {len(r3)}件\n")

        await browser.close()

    all_results = deduplicate(all_results)
    print(f"=== 合計: {len(all_results)}件（重複除去後）===\n")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"保存完了: {OUTPUT_FILE}")

    # 集計サマリー
    prefs = Counter(r["都道府県"] for r in all_results if r["都道府県"])
    types = Counter(r["施設タイプ"] for r in all_results)
    sources = Counter(r["ソース"] for r in all_results)

    print("\n--- ソース別件数 ---")
    for k, v in sources.most_common():
        print(f"  {k}: {v}件")

    print("\n--- 都道府県TOP15 ---")
    for k, v in prefs.most_common(15):
        print(f"  {k}: {v}件")

    print("\n--- 施設タイプ ---")
    for k, v in types.most_common():
        print(f"  {k}: {v}件")


if __name__ == "__main__":
    asyncio.run(main())
