# WordPress 發佈規則

## 平台設定

| 項目 | 值 |
|------|---|
| 站台 | https://blog.codefarm.com.tw |
| 帳號 | weiyun |
| 認證方式 | WordPress Application Password（存於 `publish_to_wordpress.py`） |
| 發佈 API | WordPress REST API `/wp-json/wp/v2/posts` |

---

## 發佈前檢查清單

每篇文章發佈前，先確認以下項目：

1. **Frontmatter 齊全**：`title`、`description`、`keywords` 三欄都有填
2. **步驟教學存在**：文章包含至少一個「步驟教學」段落，用編號清單呈現（前言 00 篇豁免）
3. **FAQ 存在**：文章末尾有 `## 常見問題（FAQ）` 區塊，含 5～8 題（前言 00 篇豁免）
4. **內部連結**：有連到系列中至少 1～2 篇其他文章
5. **字數**：正文至少 1,200 字（前言 00 篇豁免）
6. **內容真實**：沒有捏造的指令或截圖素材

---

## 發佈流程

### 步驟一：先發佈為草稿確認

把 `publish_to_wordpress.py` 裡的 `POST_STATUS` 改為 `"draft"`，執行腳本：

```
跟 AI agent 說：「把 POST_STATUS 改成 draft，然後幫我執行 publish_to_wordpress.py」
```

進入 WordPress 後台確認文章格式、段落、連結是否正常。

### 步驟二：確認格式後正式發佈

確認草稿沒問題後，把 `POST_STATUS` 改回 `"publish"`，再次執行腳本：

```
跟 AI agent 說：「POST_STATUS 改回 publish，再執行一次發佈腳本」
```

或直接在 WordPress 後台把草稿狀態改為「發佈」。

### 步驟三：發佈後核對

發佈完成後確認：
- 文章連結能正常開啟
- 標題、摘要在頁面上顯示正確
- 圖片（如有）載入正常
- 系列內文章間的連結可以點通

---

## 腳本使用說明

```bash
# 安裝依賴（第一次使用）
pip install markdown requests

# 執行（從 blog repo 根目錄）
python publish_to_wordpress.py
```

腳本會自動：
- 掃描 `posts/01-*.md` 到 `posts/06-*.md`
- 讀取 frontmatter 取出 `title` 和 `description`
- 把 Markdown 轉成 HTML
- 透過 REST API 發佈到 WordPress

---

## 注意事項

- **不要把帳密寫進 git commit**：`publish_to_wordpress.py` 內有帳密，若有多人協作請改用 `.env` 檔搭配 `python-dotenv`
- 腳本預設發佈第 01 到 06 篇（前言 00 篇不在範圍內，因為是感性文章，建議手動貼上）
- 若某篇已發佈想更新，需在 WordPress 後台找到文章 ID 改用 PUT 請求，或手動編輯
