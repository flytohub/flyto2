# UI Builder Integration Guide

## 概述

類似 n8n 的架構，前端可以從 `@register_module` 裝飾器自動獲取模組定義並生成表單。

## 架構流程

```
┌─────────────────┐
│  @register_module │  ← Python 裝飾器定義模組
│   (後端)          │
└────────┬─────────┘
         │
         ↓
┌─────────────────┐
│ ModuleRegistry   │  ← 儲存所有 metadata
│   (Python)       │
└────────┬─────────┘
         │
         ↓
┌─────────────────┐
│  API Endpoints   │  ← FastAPI 提供 REST API
│   (/api/modules) │
└────────┬─────────┘
         │
         ↓ HTTP GET/POST
┌─────────────────┐
│  前端 Vue.js     │  ← 動態生成表單
│ (Template Builder)│
└─────────────────┘
```

## API Endpoints

### 1. 獲取所有模組列表

```http
GET /api/modules/list?lang=zh&category=browser
```

**回應**:
```json
{
  "modules": [
    {
      "module_id": "core.browser.launch",
      "label": "啟動瀏覽器",
      "label_key": "modules.browser.launch.label",
      "description": "使用 Playwright 啟動新的瀏覽器實例",
      "description_key": "modules.browser.launch.description",
      "category": "browser",
      "icon": "Monitor",
      "color": "#4A90E2",
      "params_schema": {
        "headless": {
          "type": "boolean",
          "label": "無頭模式",
          "label_key": "modules.browser.launch.params.headless.label",
          "description": "在無頭模式下運行瀏覽器（無 UI）",
          "default": false,
          "required": false
        }
      },
      "output_schema": {
        "status": {"type": "string"},
        "message": {"type": "string"}
      }
    }
  ],
  "count": 20,
  "categories": ["browser", "api", "ai"]
}
```

### 2. 獲取模組詳細資訊

```http
GET /api/modules/detail/core.browser.launch?lang=zh
```

### 3. 獲取參數 Schema（用於表單生成）

```http
GET /api/modules/schema/core.browser.launch?lang=zh
```

**回應**:
```json
{
  "params_schema": {
    "headless": {
      "type": "boolean",
      "label": "無頭模式",
      "description": "在無頭模式下運行瀏覽器（無 UI）",
      "default": false,
      "required": false
    },
    "viewport": {
      "type": "object",
      "label": "視窗大小",
      "description": "瀏覽器視窗大小",
      "properties": {
        "width": {"type": "number", "default": 1920},
        "height": {"type": "number", "default": 1080}
      }
    }
  }
}
```

### 4. 驗證參數

```http
POST /api/modules/validate
Content-Type: application/json

{
  "module_id": "core.browser.launch",
  "params": {
    "headless": true
  }
}
```

### 5. 搜尋模組

```http
GET /api/modules/search?query=browser&lang=zh
```

## 前端實現範例

### Vue.js Component (Template Builder)

```vue
<template>
  <div class="module-builder">
    <!-- 模組選擇器 -->
    <div class="module-selector">
      <h3>選擇模組</h3>

      <!-- 分類過濾 -->
      <div class="categories">
        <button
          v-for="cat in categories"
          :key="cat.id"
          @click="selectedCategory = cat.id"
          :class="{ active: selectedCategory === cat.id }"
        >
          {{ cat.label }} ({{ cat.count }})
        </button>
      </div>

      <!-- 模組列表 -->
      <div class="module-list">
        <div
          v-for="module in filteredModules"
          :key="module.module_id"
          @click="selectModule(module)"
          class="module-item"
        >
          <div class="module-icon" :style="{ color: module.color }">
            {{ module.icon }}
          </div>
          <div class="module-info">
            <h4>{{ module.label }}</h4>
            <p>{{ module.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 參數表單（動態生成） -->
    <div class="params-form" v-if="selectedModule">
      <h3>{{ selectedModule.label }} - 參數設定</h3>

      <form @submit.prevent="saveStep">
        <!-- 動態生成表單欄位 -->
        <div
          v-for="(paramDef, paramName) in selectedModule.params_schema"
          :key="paramName"
          class="form-field"
        >
          <!-- String 輸入 -->
          <div v-if="paramDef.type === 'string'">
            <label>
              {{ paramDef.label }}
              <span v-if="paramDef.required" class="required">*</span>
            </label>
            <input
              type="text"
              v-model="params[paramName]"
              :placeholder="paramDef.placeholder"
              :required="paramDef.required"
            />
            <small>{{ paramDef.description }}</small>
          </div>

          <!-- Boolean 開關 -->
          <div v-if="paramDef.type === 'boolean'">
            <label>
              <input
                type="checkbox"
                v-model="params[paramName]"
              />
              {{ paramDef.label }}
            </label>
            <small>{{ paramDef.description }}</small>
          </div>

          <!-- Number 輸入 -->
          <div v-if="paramDef.type === 'number'">
            <label>
              {{ paramDef.label }}
              <span v-if="paramDef.required" class="required">*</span>
            </label>
            <input
              type="number"
              v-model.number="params[paramName]"
              :min="paramDef.min"
              :max="paramDef.max"
              :required="paramDef.required"
            />
            <small>{{ paramDef.description }}</small>
          </div>

          <!-- Select 下拉選單 -->
          <div v-if="paramDef.enum">
            <label>
              {{ paramDef.label }}
              <span v-if="paramDef.required" class="required">*</span>
            </label>
            <select v-model="params[paramName]" :required="paramDef.required">
              <option v-for="option in paramDef.enum" :key="option" :value="option">
                {{ option }}
              </option>
            </select>
            <small>{{ paramDef.description }}</small>
          </div>
        </div>

        <button type="submit" class="btn-primary">添加步驟</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      modules: [],
      categories: [],
      selectedCategory: null,
      selectedModule: null,
      params: {}
    }
  },

  computed: {
    filteredModules() {
      if (!this.selectedCategory) return this.modules
      return this.modules.filter(m => m.category === this.selectedCategory)
    }
  },

  async mounted() {
    await this.loadModules()
    await this.loadCategories()
  },

  methods: {
    async loadModules() {
      const lang = this.$i18n.locale // 'zh' or 'en'
      const response = await fetch(`/api/modules/list?lang=${lang}`)
      const data = await response.json()
      this.modules = data.modules
    },

    async loadCategories() {
      const response = await fetch('/api/modules/categories')
      const data = await response.json()
      this.categories = data.categories
    },

    async selectModule(module) {
      this.selectedModule = module

      // 初始化參數（使用默認值）
      this.params = {}
      for (const [paramName, paramDef] of Object.entries(module.params_schema)) {
        if (paramDef.default !== undefined) {
          this.params[paramName] = paramDef.default
        }
      }
    },

    async saveStep() {
      // 驗證參數
      const response = await fetch('/api/modules/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_id: this.selectedModule.module_id,
          params: this.params
        })
      })

      const validation = await response.json()

      if (validation.valid) {
        // 添加步驟到工作流
        this.$emit('add-step', {
          module: this.selectedModule.module_id,
          params: { ...this.params }
        })

        // 重置表單
        this.selectedModule = null
        this.params = {}
      } else {
        // 顯示錯誤
        alert(validation.errors.join('\n'))
      }
    }
  }
}
</script>
```

### JavaScript/Fetch 範例

```javascript
// 1. 獲取所有模組
async function getModules(lang = 'zh', category = null) {
  const params = new URLSearchParams({ lang })
  if (category) params.append('category', category)

  const response = await fetch(`/api/modules/list?${params}`)
  const data = await response.json()
  return data.modules
}

// 2. 動態生成表單欄位
function generateFormField(paramName, paramDef) {
  const field = document.createElement('div')
  field.className = 'form-field'

  // 標籤
  const label = document.createElement('label')
  label.textContent = paramDef.label
  if (paramDef.required) {
    const required = document.createElement('span')
    required.className = 'required'
    required.textContent = ' *'
    label.appendChild(required)
  }

  // 輸入框（根據類型）
  let input
  switch (paramDef.type) {
    case 'string':
      input = document.createElement('input')
      input.type = 'text'
      input.placeholder = paramDef.placeholder || ''
      break

    case 'boolean':
      input = document.createElement('input')
      input.type = 'checkbox'
      input.checked = paramDef.default || false
      break

    case 'number':
      input = document.createElement('input')
      input.type = 'number'
      input.min = paramDef.min || ''
      input.max = paramDef.max || ''
      input.value = paramDef.default || ''
      break

    case 'select':
      input = document.createElement('select')
      paramDef.options.forEach(opt => {
        const option = document.createElement('option')
        option.value = opt.value
        option.textContent = opt.label
        input.appendChild(option)
      })
      break
  }

  input.name = paramName
  input.required = paramDef.required || false

  // 說明文字
  const description = document.createElement('small')
  description.textContent = paramDef.description

  field.appendChild(label)
  field.appendChild(input)
  field.appendChild(description)

  return field
}

// 3. 使用範例
async function buildModuleForm(moduleId) {
  const response = await fetch(`/api/modules/schema/${moduleId}?lang=zh`)
  const { params_schema } = await response.json()

  const form = document.querySelector('#module-form')
  form.innerHTML = '' // 清空

  // 動態生成每個參數的表單欄位
  for (const [paramName, paramDef] of Object.entries(params_schema)) {
    const field = generateFormField(paramName, paramDef)
    form.appendChild(field)
  }
}
```

## 關鍵特性

### 1. ✅ i18n 支援
- API 接受 `lang` 參數 (`en`, `zh`, `ja`)
- 自動返回對應語言的 `label` 和 `description`
- 前端只需切換語言參數

### 2. ✅ 類型安全
- `params_schema` 定義所有參數類型
- 支援：`string`, `number`, `boolean`, `object`, `array`, `enum`
- 前端根據類型生成對應輸入框

### 3. ✅ 驗證
- 後端提供參數驗證 API
- 檢查必填欄位
- 檢查類型匹配

### 4. ✅ 視覺化
- 每個模組有 `icon` 和 `color`
- 前端可以顯示圖示和顏色標籤

### 5. ✅ 搜尋和過濾
- 按分類過濾
- 按標籤過濾
- 關鍵字搜尋

## 擴展：自訂表單組件

對於複雜的參數類型，可以創建自訂組件：

```vue
<!-- ObjectEditor.vue - 用於編輯 object 類型參數 -->
<template>
  <div class="object-editor">
    <div v-for="(propDef, propName) in schema.properties" :key="propName">
      <label>{{ propDef.label }}</label>
      <input
        :type="getInputType(propDef.type)"
        v-model="value[propName]"
      />
    </div>
  </div>
</template>

<!-- VariableSelector.vue - 用於選擇工作流變數 -->
<template>
  <div class="variable-selector">
    <input
      type="text"
      v-model="value"
      @focus="showVariables = true"
    />
    <div v-if="showVariables" class="variable-list">
      <div
        v-for="variable in availableVariables"
        :key="variable"
        @click="selectVariable(variable)"
      >
        {{ variable }}
      </div>
    </div>
  </div>
</template>
```

## 總結

完全可以實現！你只需要：

1. ✅ **後端已準備好** - `modules_metadata.py` API
2. 🔧 **前端需要做** - 調用 API 並動態生成表單
3. 🎨 **UI 設計** - 參考 n8n 的 UI 風格

就像 Swagger 自動從代碼生成 API 文檔，你的 UI 會從 `@register_module` 自動生成表單！
