# Workflow DSL 規格（Draft v1）

這份文件說明 flyto2 / flytohub 自動化引擎所使用的 YAML Workflow DSL。
所有工作流、子流程、範例都應遵守本規格。

**版本：** 1.0.0
**狀態：** Alpha
**最後更新：** 2025-11-29

---

## 目錄

- [設計目標](#設計目標)
- [Workflow 檔案結構](#workflow-檔案結構)
- [參數定義 (params)](#參數定義-params)
- [Steps（步驟）](#steps步驟)
- [全域錯誤處理](#全域錯誤處理-error-區塊)
- [Workflow 輸出](#workflow-輸出-output)
- [表達式語法](#表達式語法)
- [特殊 engine / 子流程](#特殊-engine--子流程-subflow)
- [命名約定](#命名約定-naming-conventions)
- [範例](#範例)
- [後續擴充方向](#後續擴充方向)

---

## 設計目標（Design Goals）

- **人類可讀**：整個 workflow 用 YAML 表達，而不是藏在資料庫或 UI 裡
- **Git 友善**：適合 git diff / PR review / rollback
- **可組合**：每個 step 是 atomic module，流程可以任意組合
- **可攜帶**：同一份 YAML 可以在本機、Docker、Kubernetes、CI/CD、Server 上執行
- **對開發者友善**：變數、錯誤處理、條件、loop 都靠 DSL 清楚定義

---

## Workflow 檔案結構

一個 workflow 是一個 `.yaml` 檔，基本結構如下：

```yaml
id: google-search-top10
name: "Google Search Top 10"
version: "1.1.0"

description:
  en: "Extract top 10 Google search results for a keyword"
  zh: "提取 Google 搜尋結果的前 10 筆"

author: "Workflow Engine Team"
tags: ["google", "search", "scraping"]

engine: "browser-flow"

config:
  browser:
    headless: false
  timeout_ms: 60000

params:
  # ...
steps:
  # ...
error:
  # ...
output:
  # ...
```

### 頂層欄位（Top-level fields）

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `id` | string | ✅ | Workflow 全域唯一 ID（用來在 CLI / UI / API 中引用） |
| `name` | string | ✅ | 顯示用名稱 |
| `version` | string | ✅ | Semantic version（例如 1.0.0） |
| `description` | string / map | ❌ | 可以是單純字串，或 `{en, zh, ...}` i18n 物件 |
| `author` | string | ❌ | 作者／維護者資訊 |
| `tags` | string[] | ❌ | 標籤，用於 UI 分類、搜尋 |
| `engine` | string | ✅ | 執行引擎類型，例如：`browser-flow`, `http-flow`, `subflow` |
| `config` | object | ❌ | workflow-local 設定，覆蓋全域 config |
| `params` | Param[] | ❌ | 使用者可傳入的參數 |
| `steps` | Step[] | ✅ | 工作流的步驟列表 |
| `error` | ErrorConfig | ❌ | 全域錯誤處理策略 |
| `output` | OutputSpec | ❌ | Workflow 的輸出定義 |

---

## 參數定義（params）

`params` 是一個陣列，每一個 param 描述一個可輸入的參數（CLI、UI、API 皆可用）。

```yaml
params:
  - name: keyword
    type: string
    label:
      en: "Search Keyword"
      zh: "搜尋關鍵字"
    description:
      en: "The keyword to search on Google"
    placeholder: "python tutorial"
    required: true
    default: "python tutorial"
    validation:
      min_length: 1
      max_length: 100

  - name: max_results
    type: number
    label: "Maximum Results"
    description: "Number of results (1–100)"
    default: 10
    min: 1
    max: 100
    required: false
    advanced: true

  - name: output_format
    type: string
    label: "Output Format"
    default: "json"
    enum: ["json", "csv", "markdown"]
```

### Param 欄位

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `name` | string | ✅ | 參數名稱，在 DSL 中透過 `params.<name>` 存取 |
| `type` | "string" \| "number" \| "boolean" \| "array" \| "object" | ✅ | 參數型別 |
| `label` | string / map | ❌ | UI 顯示文字，可支援 i18n |
| `description` | string / map | ❌ | UI / 文件描述 |
| `placeholder` | string | ❌ | UI placeholder |
| `required` | boolean | ❌ | 是否必填（預設 false） |
| `default` | any | ❌ | 預設值（在未提供時使用） |
| `enum` | any[] | ❌ | 限制可選值 |
| `min` / `max` | number | ❌ | 用於 number 類型的範圍驗證 |
| `validation` | object | ❌ | 自訂 validation（例如 min_length, max_length 等） |
| `advanced` | boolean | ❌ | UI 隱藏在「進階設定」中 |
| `show_if` | object | ❌ | 控制此參數是否顯示（依其他參數狀態） |

### show_if 結構

```yaml
show_if:
  field: "save_to_file"
  equals: true
```

在 UI/工具裡，只有當 `params.save_to_file === true` 時才顯示此參數。

---

## Steps（步驟）

`steps` 是一個「從上到下 sequential 執行」的步驟列表。每個 step 一次做一件事（Atomic Module）。

```yaml
steps:
  - id: launch_browser
    module: core.browser.launch
    description: "Launch web browser"
    params:
      headless: "${config.browser.headless}"
    output:
      browser: "${result.browser}"
      page: "${result.page}"
    on_error:
      retry: 1
      backoff_ms: 1000
      fatal: true

  - id: goto_google
    module: core.browser.goto
    description: "Navigate to Google"
    params:
      browser: "${launch_browser.browser}"
      url: "https://www.google.com"
      wait_until: "networkidle"

  - id: wait_search_box
    module: core.browser.wait
    description: "Wait for search input"
    params:
      browser: "${launch_browser.browser}"
      selector: 'input[name="q"], textarea[name="q"]'
      timeout_ms: 10000
```

### Step 通用欄位

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `id` | string | ✅ | step 的唯一 ID，供後續引用（`<id>.<field>`） |
| `module` | string | ✅ | 要呼叫的模組 ID，如 `core.browser.launch` |
| `description` | string | ❌ | 文字描述，顯示於 UI 或 log |
| `params` | object | ❌ | 傳給 module 的參數（可含表達式） |
| `output` | object | ❌ | 定義哪些資料要暴露給後續 step 使用 |
| `when` | string | ❌ | 條件表達式，結果為 false 時跳過此 step |
| `always` | boolean | ❌ | 若為 true，無論前方是否失敗都會執行（類似 finally） |
| `on_error` | object | ❌ | step 層級的錯誤處理設定 |

### params 中可以使用的變數（Context）

在 `params`（以及 `when`、`output`）裡可以使用 `${ ... }` 表達式。
可用的變數：

| 名稱 | 說明 |
|------|------|
| `params` | 使用者輸入參數物件，例如 `params.keyword` |
| `config` | workflow 的 config 物件 |
| `env` | 環境變數，例如 `env.OPENAI_API_KEY` |
| `steps` | 所有已執行步驟的 output，例如 `steps.launch_browser.output.browser` |
| `<stepId>` | 便捷別名，相當於 `steps.<stepId>.output`，例如 `launch_browser.browser` |
| `utils` | 系統提供的工具函式，例如 `utils.slug()`, `utils.clean_url()` 等 |
| `timestamp` | 執行當下時間戳（例如 ISO 字串） |
| `error` | 在錯誤處理中可用的錯誤物件 |
| `result` | 當前 module 回傳的原始結果（只在 step 執行完做 output mapping 時可用） |

### output 欄位

`output` 用來把 module 執行結果的一部分取出，命名並暴露給後續 step 使用。

```yaml
- id: extract_results
  module: core.browser.extract
  params:
    browser: "${launch_browser.browser}"
    selector: "#search .g"
    limit: "${params.max_results || 10}"
    fields:
      title: { selector: "h3", type: "text" }
      url:   { selector: "a", type: "attribute", attribute: "href" }
  output:
    items: "${result.items}"
    count: "${result.items.length}"
```

後續 step 中可以這樣使用：

```yaml
params:
  input: "${extract_results.items}"
  limit: "${extract_results.count}"
```

等價於：

```yaml
params:
  input: "${steps.extract_results.output.items}"
```

### when 條件執行

若 `when` 存在，會先 evaluate；如果結果為 falsy（false / 0 / '' / null / undefined）則**跳過此 step**。

```yaml
- id: save_to_file_step
  module: core.fs.write
  description: "Save results to file if enabled"
  when: "${params.save_to_file === true}"
  params:
    dir: "${params.output_dir || './results'}"
    filename: "google_search_${utils.slug(params.keyword)}_${timestamp}.txt"
    content: "${format_results.payload}"
```

### always（類似 finally）

若 `always: true`，即使前面有 step 失敗、workflow 中途丟錯，此 step 仍會執行（通常用來清理資源，例如關閉瀏覽器）。

```yaml
- id: close_browser
  module: core.browser.close
  description: "Close browser"
  params:
    browser: "${launch_browser.browser}"
  always: true
```

### Step 級錯誤處理 on_error

`on_error` 是每個 step 都可以設定的 retry / backoff / fatal 行為。

```yaml
- id: launch_browser
  module: core.browser.launch
  params:
    headless: "${config.browser.headless}"
  output:
    browser: "${result.browser}"
  on_error:
    retry: 1           # 失敗重試次數
    backoff_ms: 1000   # 每次重試前等待時間
    fatal: true        # 若重試後仍失敗 → 拋出錯誤，中止 workflow
```

欄位說明：

| 欄位 | 類型 | 說明 |
|------|------|------|
| `retry` | number | 最大重試次數 |
| `backoff_ms` | number | 每次重試之間等待毫秒數 |
| `fatal` | boolean | 若 true，這個 step 無法完成時會終止 workflow（丟出錯誤） |

---

## 全域錯誤處理（error 區塊）

除了 step-level 的 `on_error`，workflow 可以設定全域的錯誤處理策略。

```yaml
error:
  on_error:
    - module: core.log.error
      params:
        message: "Google Search Top 10 workflow failed"
        error: "${error}"
    - module: core.browser.safe_close
      params:
        browser: "${launch_browser.browser}"

  strategy:
    stop_on_error: true
```

### 結構說明

| 欄位 | 類型 | 說明 |
|------|------|------|
| `on_error` | StepLike[] | 當 workflow 內任意 step 拋出「未處理錯誤」時，依序執行這些錯誤 handler |
| `strategy` | object | 控制錯誤後是否繼續執行等 |

`on_error` 內的每個項目跟一般 step 類似（但通常不需要 id / output），例如：

```yaml
error:
  on_error:
    - module: core.log.error
      params:
        message: "Workflow failed"
        error: "${error}"
```

`strategy` 可以包含：

```yaml
strategy:
  stop_on_error: true   # 預設 true，遇錯誤就中止 workflow
  # 未來可擴充: continue_on_non_fatal, max_error_steps, 等等
```

---

## Workflow 輸出（output）

`output` 定義整個 workflow 執行成功後要回傳的 payload 結構。
執行 engine 時，會 evaluate 其中所有表達式，組成一個最後回傳的 JSON。

```yaml
output:
  fields:
    keyword:       "${params.keyword}"
    results:       "${normalize_results.items}"
    count:         "${normalize_results.count}"
    format:        "${params.output_format || 'json'}"
    saved_to_file: "${params.save_to_file === true}"
    file_path:     "${save_to_file_step.file_path || null}"
    timestamp:     "${timestamp}"
```

最終返回的 JSON 會是：

```json
{
  "keyword": "...",
  "results": [ ... ],
  "count": 10,
  "format": "json",
  "saved_to_file": true,
  "file_path": "./results/xxx.txt",
  "timestamp": "2025-11-29T..."
}
```

**約定：**
- 在 `output` 中可以使用與 step params 相同的表達式語法與變數來源
- 引擎可自由決定是否要包裝成 `{ ok: true, data: <output.fields> }` 之類的外層格式（但 DSL 層先定義 fields 就好）

---

## 表達式語法（`${ ... }`）

### 基本規則

任何 string，如果是 `${...}` 開頭 + 結尾，會被當作「表達式」，透過安全執行器 evaluate。

其它類型（number / boolean / array / object）則原封不動。

```yaml
params:
  url: "https://google.com"                        # 純字串
  query: "${params.keyword}"                       # 變數取值
  limit: "${params.max_results || 10}"             # 有邏輯運算
  filename: "google_${utils.slug(params.keyword)}_${timestamp}.json" # ❌ 這裡目前視為純字串（若要混合，需引擎支援 template）
```

**建議 DSL v1：** 只支援整個欄位是 `${...}` 的情況，
混合字串 + 表達式的 template 先由 module 自己實作，或未來擴充。

### 可用變數一覽

| 變數名 | 說明 |
|--------|------|
| `params` | Workflow 參數物件 |
| `config` | Workflow config |
| `env` | 環境變數 |
| `steps` | 所有已執行 step 的輸出，`steps.<id>.output.<field>` |
| `<stepId>` | 便捷 alias：`<stepId>.<field>` = `steps.<stepId>.output.<field>` |
| `result` | 當前 step module 回傳值（只在 output mapping 時存在） |
| `utils` | 工具函式（slug, clean_url,...） |
| `timestamp` | 當前執行時間戳 |
| `error` | 在 error handler 中的錯誤物件 |

### Expression Engine

實作上可以是：

```javascript
new Function("scope", "with (scope) { return (EXPRESSION); }")
scope = { params, config, env, steps, utils, timestamp, error, result, <stepId aliases> }
```

DSL 規格只規定「什麼可以用」，不詳述 engine 實作。

---

## 特殊 engine / 子流程（subflow）

### Subflow 定義

用於抽成可重用的子流程：

```yaml
id: common-normalize-search-results
name: "Normalize Search Results"
engine: "subflow"

params:
  - name: items
    type: array
    required: true

steps:
  - id: normalize
    module: core.data.transform
    params:
      input: "${params.items}"
      operations:
        - type: "add_index"
          field: "position"
          start_from: 1
    output:
      items: "${result.items}"

output:
  fields:
    items: "${normalize.items}"
```

### 在 workflow 中呼叫 subflow

透過一個 module，例如 `core.flow.call`：

```yaml
- id: normalize_results
  module: core.flow.call
  params:
    flow_id: "common-normalize-search-results"
    inputs:
      items: "${extract_results.items}"
  output:
    items: "${result.items}"
```

**規定：** subflow 的 `output.fields` 視為 `result` 回傳的頂層。

---

## 命名約定（Naming Conventions）

### Workflow / Subflow ID

- 使用 `kebab-case`：`google-search-top10`, `daily-admin-report`, `seo-rank-tracker`
- 要全專案唯一

### Module ID

- 使用 namespace + 功能：`core.browser.launch`, `core.fs.write`, `ai.openai.chat`
- 保持 atomic：一個 module 做一件事

### Step ID

- `snake_case` 或 `kebab-case` 都可以，但建議用 `snake_case`：
  - `launch_browser`, `extract_results`, `normalize_results`, `save_to_file_step`

---

## 範例

### 範例 1：最小化 Workflow

```yaml
id: extract-page-title
name: "Extract Page Title"
version: "1.0.0"

description: "Extract the title from any webpage"

params:
  - name: url
    type: string
    required: true
    label: "Target URL"
    placeholder: "https://example.com"

steps:
  - id: launch_browser
    module: core.browser.launch
    params:
      headless: true

  - id: navigate
    module: core.browser.goto
    params:
      browser: "${launch_browser.browser}"
      url: "${params.url}"

  - id: extract_title
    module: core.browser.extract
    params:
      browser: "${launch_browser.browser}"
      selector: "title"
    output:
      title: "${result.data[0].text}"

  - id: close_browser
    module: core.browser.close
    params:
      browser: "${launch_browser.browser}"
    always: true

output:
  fields:
    url: "${params.url}"
    title: "${extract_title.title}"
    timestamp: "${timestamp}"
```

### 範例 2：條件執行與錯誤處理

```yaml
id: resilient-api-call
name: "Resilient API Call"
version: "1.0.0"

description: "Call API with automatic retry and fallback"

params:
  - name: api_url
    type: string
    required: true

steps:
  - id: primary_api
    module: core.api.http_get
    params:
      url: "${params.api_url}"
    on_error:
      retry: 3
      backoff_ms: 2000
      fatal: false

  - id: fallback_api
    module: core.api.http_get
    params:
      url: "${env.FALLBACK_API_URL}"
    when: "${primary_api.status != 'success'}"

  - id: process_data
    module: core.data.transform
    params:
      input: "${primary_api.status == 'success' ? primary_api.data : fallback_api.data}"

output:
  fields:
    source: "${primary_api.status == 'success' ? 'primary' : 'fallback'}"
    data: "${process_data.result}"
```

### 範例 3：Loop 與 Parallel

```yaml
id: multi-page-scraper
name: "Multi-Page Scraper"
version: "1.0.0"

params:
  - name: page_urls
    type: array
    required: true

steps:
  - id: launch_browser
    module: core.browser.launch

  - id: scrape_pages
    module: core.flow.loop
    params:
      items: "${params.page_urls}"
      item_var: "page_url"
      output_mode: collect
      steps:
        - id: navigate
          module: core.browser.goto
          params:
            browser: "${launch_browser.browser}"
            url: "${page_url}"

        - id: extract
          module: core.browser.extract
          params:
            browser: "${launch_browser.browser}"
            selector: ".content"

  - id: cleanup
    module: core.browser.close
    params:
      browser: "${launch_browser.browser}"
    always: true

output:
  fields:
    pages_scraped: "${scrape_pages.count}"
    data: "${scrape_pages.results}"
```

---

## 後續擴充方向

這不是 v1 規格的一部分，但可以先列在文件最後：

- **flow.loop**：在 DSL 層支援 loop step（對 array 逐項處理）
- **flow.switch**：多分支條件
- **parallel**：平行執行 step 組
- **triggers**：在 DSL 內定義 schedule / webhook / queue（目前你是放 JSON / README 裡）
- **Template string**：支援 `"hello ${params.name}"` 這種混合型字串

---

## TL;DR（簡短版）

1. **Workflow 是一個 YAML 檔**，包含 `id`, `engine`, `params`, `steps`, `error`, `output`
2. **每個 step 指向一個 module**，用 `params` 傳入資料，`output` 取出結果
3. **表達式用 `${ ... }`**，scope 包含：`params`, `config`, `env`, `steps`, `utils`, `timestamp`
4. **`when` 控制條件執行**，`always` 做 cleanup，`on_error` 控制 step retry/fatal
5. **`output.fields` 決定整個 workflow 的返回結果**
6. **子流程用 `engine: subflow` 定義**，透過 `core.flow.call` 呼叫

---

## 貢獻

這份 DSL 規格與引擎一起版本控制。若要提議修改：

1. 開 issue 描述使用情境
2. 討論語法與語義
3. 更新此文件
4. 在引擎中實作
5. 加入測試與範例

詳見 [CONTRIBUTING.md](../CONTRIBUTING.md)。

---

**最後更新：** 2025-11-29
**版本：** 1.0.0-alpha
