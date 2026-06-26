"""
WordPress 批次發佈腳本
用途：把 posts/ 資料夾下的 Markdown 文章發佈到 WordPress

執行前請安裝依賴：
    pip install markdown requests

執行方式：
    python publish_to_wordpress.py           # 依 POST_FILES 設定發佈
"""

import re
import requests
from pathlib import Path

# ── 設定區 ────────────────────────────────────────────────
WP_URL      = "https://blog.codefarm.com.tw"
WP_USER     = "weiyun"
WP_APP_PASS = "LgWn IvQn mkmS JxlK AKVN Wask"

# "publish" 直接發佈；"draft" 存為草稿（建議先用 draft 確認後再改）
POST_STATUS = "publish"

# 要發佈的檔案清單（依序）；改這裡控制要發哪幾篇
POSTS_DIR = Path(__file__).parent / "posts"
POST_FILES = sorted(POSTS_DIR.glob("04-*.md"))
# ─────────────────────────────────────────────────────────

# ── 樣式常數 ──────────────────────────────────────────────
# (1) PM學習小心得 區塊樣式
INSIGHT_DIV_STYLE = (
    "background:#f7f7f7;border:1px solid #e0e0e0;"
    "border-radius:14px;padding:24px 28px;margin:24px 0;"
)

# (2) 標題下方分隔線
HR_STYLE = (
    "border:none;border-top:1px solid #e0e0e0;margin:0.6em 0 1.4em;"
)

# AI 對話 blockquote 樣式
BQ_STYLE = (
    "border-left:3px solid #555555;"
    "background:#f5f5f5;"
    "padding:5px 18px 5px 20px;"
    "margin:1em 0;"
    "border-radius:0 8px 8px 0;"
    "font-style:normal;"
    "color:#2d2d2d;"
)

# (4) 表格樣式
TABLE_STYLE  = "border-collapse:collapse;width:100%;margin:1.2em 0;font-size:0.95em;"
TH_STYLE     = (
    "background:#f0f3ff;color:#1a1a2e;font-weight:600;"
    "padding:10px 14px;border:1px solid #d0d7e8;text-align:left;"
)
TD_STYLE     = "padding:10px 14px;border:1px solid #e0e0e0;vertical-align:top;"
TR_ALT_STYLE = "background:#fafafa;"
# ─────────────────────────────────────────────────────────


def parse_frontmatter(text):
    """取出 YAML frontmatter，回傳 (meta_dict, content_without_frontmatter)"""
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end].strip()
            for line in fm.splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip()
            text = text[end + 4:].lstrip("\n")
    return meta, text


def md_to_html(text):
    """Markdown → HTML"""
    try:
        import markdown
        return markdown.markdown(
            text,
            extensions=["fenced_code", "tables", "nl2br", "sane_lists"],
        )
    except ImportError:
        print("⚠️  找不到 markdown 套件，請先執行：pip install markdown")
        raise


# ── 後處理：四條發佈樣式規則 ──────────────────────────────

def fix_insight_block(html):
    """(1) 修正 <div> 心得區塊：補正確 style + 把殘留的 **粗體** 轉成 <strong>"""
    # 確保 div 有正確 style（不管原本寫了什麼 style）
    html = re.sub(
        r'<div style="[^"]*">',
        f'<div style="{INSIGHT_DIV_STYLE}">',
        html,
    )
    # 把 div 區塊內未被 markdown 轉換的 **text** 轉成 <strong>
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html, flags=re.DOTALL)
    return html


def add_hr_after_headings(html):
    """(2) 在每個 </h2> 後加分隔線（避免重複加）"""
    return re.sub(
        r'(</h2>)(?!\s*<hr)',
        rf'\1\n<hr style="{HR_STYLE}">',
        html,
    )


def style_tables(html):
    """(4) 為 <table>、<th>、<td>、偶數 <tr> 加 inline style"""
    html = re.sub(r'<table>', f'<table style="{TABLE_STYLE}">', html)
    html = re.sub(r'<th>', f'<th style="{TH_STYLE}">', html)
    html = re.sub(r'<td>', f'<td style="{TD_STYLE}">', html)

    # 讓偶數列有淡灰底色（斑馬條紋）
    def stripe_rows(m):
        rows = re.findall(r'<tr>.*?</tr>', m.group(), re.DOTALL)
        result = []
        data_row = 0
        for row in rows:
            if row.startswith('<tr><th') or f'<th style="{TH_STYLE}">' in row:
                result.append(row)  # 標題列不加底色
            else:
                data_row += 1
                if data_row % 2 == 0:
                    row = row.replace('<tr>', f'<tr style="{TR_ALT_STYLE}">', 1)
                result.append(row)
        return m.group()[:m.start('inner') - m.start()] + "".join(result) + "</table>"

    # 簡單版：只對 tbody 內的偶數 tr 加色
    def add_stripe(match):
        tbody = match.group()
        rows = re.split(r'(?=<tr)', tbody)
        out, count = [], 0
        for row in rows:
            if row.startswith('<tr>') and '<th' not in row:
                count += 1
                if count % 2 == 0:
                    row = row.replace('<tr>', f'<tr style="{TR_ALT_STYLE}">', 1)
            out.append(row)
        return "".join(out)

    html = re.sub(r'<tbody>.*?</tbody>', add_stripe, html, flags=re.DOTALL)
    return html


def flatten_faq_headings(html):
    """FAQ 區塊內的 <h3> 轉成同字體大小的粗體段落"""
    faq_marker = re.search(r'<h2[^>]*>.*?常見問題.*?</h2>', html)
    if not faq_marker:
        return html
    before = html[:faq_marker.end()]
    after  = html[faq_marker.end():]
    after  = re.sub(
        r'<h3[^>]*>(.*?)</h3>',
        r'<p><strong>\1</strong></p>',
        after,
        flags=re.DOTALL,
    )
    return before + after


def style_blockquotes(html):
    """AI 對話 blockquote → div（移除佈景主題引號圖示）＋左藍線淺灰底樣式"""
    # 統一清除可能殘留的 style，再整批換成 div
    html = re.sub(r'<blockquote[^>]*>', f'<div style="{BQ_STYLE}">', html)
    html = html.replace('</blockquote>', '</div>')
    return html


def apply_styles(html):
    """依序套用發佈樣式規則"""
    html = fix_insight_block(html)      # (1) 心得區塊
    html = add_hr_after_headings(html)  # (2) 標題底線
    # (3) 圖片：由 generate_image.py 另外處理（需依主題客製）
    html = style_tables(html)           # (4) 表格樣式
    html = flatten_faq_headings(html)   # FAQ 題目轉粗體段落
    html = style_blockquotes(html)      # AI 對話框樣式
    return html

# ─────────────────────────────────────────────────────────


def publish_post(title, html_content, excerpt="", status=POST_STATUS):
    """透過 WordPress REST API 發佈一篇文章"""
    url = f"{WP_URL}/wp-json/wp/v2/posts"
    payload = {
        "title":   title,
        "content": html_content,
        "excerpt": excerpt,
        "status":  status,
        "format":  "standard",
    }
    resp = requests.post(
        url,
        json=payload,
        auth=(WP_USER, WP_APP_PASS),
        headers={"User-Agent": "WordPress-Python-Publisher/1.0"},
        timeout=30,
    )
    return resp


def main():
    print(f"目標站台：{WP_URL}")
    print(f"發佈狀態：{POST_STATUS}")
    print(f"找到 {len(POST_FILES)} 篇文章\n")

    for path in POST_FILES:
        print(f"▶ 處理：{path.name}")
        raw = path.read_text(encoding="utf-8")
        meta, content = parse_frontmatter(raw)

        title   = meta.get("title", path.stem)
        excerpt = meta.get("description", "")

        html = md_to_html(content)
        html = apply_styles(html)
        resp = publish_post(title, html, excerpt)

        if resp.status_code in (200, 201):
            data = resp.json()
            print(f"  ✅ 成功！文章 ID：{data['id']}，連結：{data['link']}")
        else:
            print(f"  ❌ 失敗（HTTP {resp.status_code}）：{resp.text[:200]}")

    print("\n完成。")


if __name__ == "__main__":
    main()
