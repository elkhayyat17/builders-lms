# Full Bilingual Architecture & Flawless RTL/LTR Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a 100% pristine bilingual system (Arabic & English) across the LMS and Lesson Workspace, eliminating all hardcoded English leaks and hybrid slash strings, ensuring instant reactive translation and pixel-perfect RTL/LTR layout and typography.

**Architecture:** Frontend components will use clean, semantic English keys in `__()`. The translation plugin (`translation.js`) is upgraded to a reactive Vue store. A comprehensive Arabic gettext catalog (`ar.po` & `builders.mo`) provides authentic Saudi/Gulf engineering terminology. Dynamic `dir="rtl"` / `dir="ltr"` and typography styles handle layout orientation with formula LTR immunity.

**Tech Stack:** Vue 3, Frappe LMS, Frappe UI, Python 3.11, GNU gettext (`.po`/`.mo`), Tailwind CSS (logical properties), IBM Plex Sans Arabic & Latin.

**Spec:** `docs/superpowers/specs/2026-10-03-full-bilingual-and-rtl-design.md`

## Global Constraints
- Every key in `__()` MUST be clean English without hybrid slashes (`/`).
- Zero hardcoded English text in user-facing templates.
- In Arabic (`dir="rtl"`): zero untranslated English leaks in workspace components.
- In English (`dir="ltr"`): zero untranslated Arabic keys or slashes.
- Math equations, LaTeX formulas, timestamps (`00:00`), and code blocks MUST strictly remain `direction: ltr !important; text-align: left !important;` in both modes.
- Preserve all existing video security shields (AES-128, watermark, capture lockdown, anti-tamper).
- All changes must pass `docker exec -w /home/frappe/frappe-bench/apps/lms/frontend docker-frappe-1 yarn build` with code 0.

---

### Task 1: Reactive Translation Engine & Language Switching

**Files:**
- Modify: `lms/frontend/src/translation.js`
- Modify: `lms/frontend/src/components/Sidebar/UserDropdown.vue`
- Modify: `builders/builders/public/js/language-toggle.js`
- Test: `scripts/test_translation_engine.py`

**Interfaces:**
- Consumes: `lms.lms.api.get_translations`, `frappe.client.set_value`
- Produces: Reactive `translations` ref exported from `translation.js`, synchronous `translate()` helper, instant language switch setting `dir` and `lang` on document.

- [ ] **Step 1: Write test script to verify translation endpoint and user language persistence**
Create `scripts/test_translation_engine.py` that verifies `get_translations` returns Arabic keys when user language is set to `ar`, and checks that setting user language to `ar` updates `User.language` and returns translations.

- [ ] **Step 2: Run test script to establish baseline**
Run: `docker exec -w /home/frappe/frappe-bench/sites docker-frappe-1 ../env/bin/python /tmp/test_translation_engine.py`

- [ ] **Step 3: Make translation.js reactive in Vue 3**
Update `lms/frontend/src/translation.js`:
```javascript
import { ref } from 'vue'
import { createResource } from 'frappe-ui'

export const translations = ref(window.translatedMessages || {})

export default function translationPlugin(app) {
	app.config.globalProperties.__ = translate
	window.__ = translate
	if (!window.translatedMessages || Object.keys(window.translatedMessages).length === 0) {
		fetchTranslations()
	}
}

export function translate(message) {
	if (!message) return ''
	let dict = translations.value
	let translated = dict[message] || message

	const hasPlaceholders = /{\d+}/.test(message)
	if (!hasPlaceholders) {
		return translated
	}
	return {
		format: function (...args) {
			return translated.replace(/{(\d+)}/g, function (match, number) {
				return typeof args[number] !== 'undefined' ? args[number] : match
			})
		},
		toString: function () {
			return translated
		},
	}
}

function fetchTranslations() {
	createResource({
		url: 'lms.lms.api.get_translations',
		cache: 'translations',
		auto: true,
		transform: (data) => {
			translations.value = data || {}
			window.translatedMessages = data || {}
		},
	})
}
```

- [ ] **Step 4: Update UserDropdown.vue and language-toggle.js**
Ensure language switching updates:
1. `call('frappe.client.set_value', { doctype: 'User', name: user, fieldname: 'language', value: lang })`
2. `document.cookie = 'preferred_language=' + lang + ';path=/;max-age=31536000;SameSite=Lax'`
3. Sets `document.documentElement.lang = lang` and `document.documentElement.dir = (lang === 'ar' ? 'rtl' : 'ltr')` before `window.location.reload()`.

- [ ] **Step 5: Run test to verify passes**
Run test script inside container and confirm success.

- [ ] **Step 6: Commit**
```bash
git add lms/frontend/src/translation.js lms/frontend/src/components/Sidebar/UserDropdown.vue builders/builders/public/js/language-toggle.js
git commit -m "feat(i18n): upgrade translation plugin to reactive Vue store and refine language switcher"
```

---

### Task 2: Frontend Semantic Keys Sanitization in LessonWorkspace

**Files:**
- Modify: `lms/frontend/src/components/LessonWorkspace/tabs/LessonOutlineTab.vue`
- Modify: `lms/frontend/src/components/LessonWorkspace/tabs/LessonQATab.vue`
- Modify: `lms/frontend/src/components/LessonWorkspace/tabs/LessonResourcesTab.vue`
- Modify: `lms/frontend/src/components/LessonWorkspace/tabs/TimestampedNotes.vue`
- Modify: `lms/frontend/src/components/LessonWorkspace/LessonSidebar.vue`
- Modify: `lms/frontend/src/components/LessonWorkspace/LessonOverview.vue`

**Interfaces:**
- Consumes: `__(key)`
- Produces: Clean semantic English keys in all workspace templates and scripts.

- [ ] **Step 1: Sanitize LessonOutlineTab.vue**
Remove all slashes:
- `:placeholder="__('Search lessons... / ابحث...')"` ➔ `:placeholder="__('Search lessons...')"`
- `{{ __('مسح البحث / Clear search') }}` ➔ `{{ __('Clear search') }}`
- `{{ __('دروس / lessons') }}` ➔ `{{ __('Lessons') }}`
- `:title="__('الفصل مكتمل بالكامل / Chapter completed')"` ➔ `:title="__('Chapter completed')"`
- `:title="__('مغلق - أكمل الدروس السابقة لفتحه / Locked')"` ➔ `:title="__('Locked')"`
- `:title="__('تم إكمال هذا الدرس / Completed')"` ➔ `:title="__('Completed')"`
- `totalLessonsCount === 1 ? __('Lesson') : __('Lessons')`

- [ ] **Step 2: Sanitize LessonQATab.vue**
Remove all slashes and wrap raw strings:
- `{{ __('العودة للأسئلة / All Questions') }}` ➔ `{{ __('Back to Questions') }}`
- `<p>No answers yet. Be the first to help!</p>` ➔ `<p>{{ __('No answers yet. Be the first to help!') }}</p>`
- `<span>[✓ Link to current video timestamp]</span>` ➔ `<span>{{ __('Link to current video timestamp') }}</span>`
- `{{ __('طرح استفسار جديد / Ask a Question') }}` ➔ `{{ __('Ask a Question') }}`
- `{{ __('عنوان السؤال / Question Title') }}` ➔ `{{ __('Question Title') }}`
- `{{ __('تفاصيل السؤال / Question Details') }}` ➔ `{{ __('Question Details') }}`
- `{{ __('إلغاء / Cancel') }}` ➔ `{{ __('Cancel') }}`
- `{{ __('نشر السؤال / Post Question') }}` ➔ `{{ __('Post Question') }}`
- `{{ __('إرسال الرد / Post Answer') }}` ➔ `{{ __('Post Answer') }}`
- `{{ __('الكل / All') }}` ➔ `{{ __('All') }}`
- `{{ __('طرح أول سؤال / Ask a question') }}` ➔ `{{ __('Ask a question') }}`
- Toast messages: `toast.success(__('Question posted successfully'))`, `toast.success(__('Reply posted successfully'))`

- [ ] **Step 3: Sanitize LessonResourcesTab.vue**
Remove all slashes and translate filters/categories:
- `:placeholder="__('ابحث في المرفقات... / Search files...')"` ➔ `:placeholder="__('Search files...')"`
- `{{ __('تحميل / Download') }}` ➔ `{{ __('Download') }}`
- Category helper:
  - `__('CAD Drawing')`
  - `__('Calculation Sheet')`
  - `__('Engineering Code')`
  - `__('Project Bundle')`
  - `__('Attachment')`
- Filter chips:
  - `label: __('All')`
  - `label: __('CAD / DWG')`
  - `label: __('Excel / XLSX')`
  - `label: __('PDF')`
  - `label: __('ZIP / Archive')`

- [ ] **Step 4: Sanitize TimestampedNotes.vue**
Ensure all strings are wrapped in `__()` with clean English keys:
- Buttons: `__('Pinned')`, `__('Export')`, `__('Add note at {0}')`, `__('Video paused')`, `__('Pin note')`, `__('Save note')`, `__('Cancel')`, `__('Edit note')`, `__('Delete note')`, `__('Delete Note')`
- Placeholders: `__('Search notes...')`, `__('Write your note here... (Press Ctrl+Enter to save)')`
- Toasts: `__('Note saved successfully')`, `__('Note updated successfully')`, `__('Note deleted successfully')`, `__('Failed to save note')`
- Palette tooltips: `__('Yellow')`, `__('Blue')`, `__('Green')`, `__('Purple')`, `__('Red')`
- Printable export: `${__('Notes')}`, `${__('Learner')}`, `${__('Generated')}`, `${__('Total Notes')}`, `${__('Pinned Notes')}`

- [ ] **Step 5: Sanitize LessonSidebar.vue & LessonOverview.vue**
- In `LessonSidebar.vue`:
  - `tabDefinitions`: `{ id: 'outline', label: 'Outline', icon: ListTree }`, `{ id: 'notes', label: 'Notes', icon: NotebookPen }`, `{ id: 'qa', label: 'Q&A', icon: MessageCircleQuestion }`, `{ id: 'resources', label: 'Resources', icon: FolderDown }`
  - Render as: `{{ __(tab.label) }}` and `:title="__(tab.label)"`
- In `LessonOverview.vue`:
  - `__('Certified Engineering Content')`
  - `__('SBC Compliant')`
  - `__('Design Equations (SBC 304 / ACI 318)')`
  - `__('LaTeX Math')`
  - `__('Instructor Notes')`
  - `__('SBC 304 - Sec. 5.3.1 (Load Combo)')`
  - `__('Tension-controlled')`

- [ ] **Step 6: Test compilation**
Run: `docker cp "lms/frontend/src/components/LessonWorkspace" docker-frappe-1:/home/frappe/frappe-bench/apps/lms/frontend/src/components/ && docker exec -w /home/frappe/frappe-bench/apps/lms/frontend docker-frappe-1 yarn build`
Expected: code 0.

- [ ] **Step 7: Commit**
```bash
git add lms/frontend/src/components/LessonWorkspace/
git commit -m "refactor(i18n): sanitize LessonWorkspace keys to clean semantic English base strings"
```

---

### Task 3: Lesson.vue, VideoBlock.vue & Navigation Sanitization

**Files:**
- Modify: `lms/frontend/src/pages/Lesson.vue`
- Modify: `lms/frontend/src/components/VideoBlock.vue`
- Modify: `lms/frontend/src/components/Sidebar/UserDropdown.vue`

**Interfaces:**
- Consumes: `__(key)`
- Produces: Clean semantic English keys across lesson wrapper, video player, and global user dropdown.

- [ ] **Step 1: Sanitize Lesson.vue**
- Theater mode button: `isTheaterMode ? __('Standard Mode') : __('Theater Mode')`
- Zen mode: `__('Zen Mode')`
- Navigation: `__('Previous lesson')`, `__('Next lesson')`, `__('Editor View')`
- Locked states: `__('This lesson is locked')`, `__('This lesson is not available for preview. Please enroll in the course to access it.')`, `__('Start Learning')`
- Tabs: `__('Questions')`, `__('Notes')`, `__('Community')`

- [ ] **Step 2: Sanitize VideoBlock.vue**
- Wrap tooltips: `playing ? __('Pause') : __('Play')`, `muted ? __('Unmute') : __('Mute')`, `__('Toggle fullscreen')`, `__('Play video')`, `__('Seek')`
- Quality picker: `level.height ? \`\${level.height}p\` : __('Auto')`
- Plurals: `quizzes.length === 1 ? __('quiz') : __('quizzes')`

- [ ] **Step 3: Sanitize UserDropdown.vue**
- Menu items: `__('My Profile')`, `__('Theme')`, `__('Language')`, `__('Arabic')`, `__('English')`, `__('Apps')`, `__('Settings')`, `__('Configuration')`, `__('Import')`, `__('Clear Demo Data')`, `__('Log out')`, `__('Log in')`

- [ ] **Step 4: Test compilation**
Run: `docker cp "lms/frontend/src/pages/Lesson.vue" docker-frappe-1:/home/frappe/frappe-bench/apps/lms/frontend/src/pages/Lesson.vue && docker cp "lms/frontend/src/components/VideoBlock.vue" docker-frappe-1:/home/frappe/frappe-bench/apps/lms/frontend/src/components/VideoBlock.vue && docker exec -w /home/frappe/frappe-bench/apps/lms/frontend docker-frappe-1 yarn build`
Expected: code 0.

- [ ] **Step 5: Commit**
```bash
git add lms/frontend/src/pages/Lesson.vue lms/frontend/src/components/VideoBlock.vue lms/frontend/src/components/Sidebar/UserDropdown.vue
git commit -m "refactor(i18n): sanitize Lesson.vue, VideoBlock.vue, and UserDropdown.vue to clean English keys"
```

---

### Task 4: Comprehensive Arabic Translation Catalog (`ar.po` & `builders.mo`)

**Files:**
- Modify: `builders/builders/locale/ar.po`
- Script: `scripts/generate_complete_po.py`
- Test: `scripts/i18n_coverage.py`

**Interfaces:**
- Consumes: English semantic keys from frontend
- Produces: Complete Arabic translations dictionary compiled into `builders.mo` and Frappe translation cache.

- [ ] **Step 1: Write generator script to merge and validate all keys**
Create `scripts/generate_complete_po.py` that extracts every English key from `lms/frontend/src` and ensures a high-standard Arabic translation exists in `builders/builders/locale/ar.po`.

- [ ] **Step 2: Update builders/builders/locale/ar.po**
Add complete translation entries for all workspace keys:
- Theater Mode ➔ `الوضع المسرحي`
- Standard Mode ➔ `الوضع القياسي`
- Zen Mode ➔ `وضع التركيز (Zen)`
- Outline ➔ `المحتوى`
- Notes ➔ `الملاحظات`
- Q&A ➔ `الأسئلة`
- Resources ➔ `المرفقات`
- Pinned ➔ `ملاحظات مثبتة`
- Export ➔ `تصدير الملاحظات`
- Add note at {0} ➔ `إضافة ملاحظة عند {0}`
- Video paused ➔ `تم إيقاف الفيديو مؤقتاً`
- Back to Questions ➔ `العودة للأسئلة`
- Ask a Question ➔ `طرح استفسار جديد`
- Question Title ➔ `عنوان السؤال`
- Question Details ➔ `تفاصيل السؤال`
- Post Question ➔ `نشر السؤال`
- Post Answer ➔ `إرسال الرد`
- CAD Drawing ➔ `مخطط أوتوكاد إنشائي`
- Calculation Sheet ➔ `شيت حسابات وتصميم`
- Engineering Code ➔ `كود ومواصفات هندسية`
- Project Bundle ➔ `حزمة ملفات المشروع`
- Attachment ➔ `ملف مرفق`
- Download ➔ `تحميل`
- Search lessons... ➔ `ابحث في الفصول والدروس...`
- Search Q&A... ➔ `ابحث في أسئلة الدرس...`
- Search files... ➔ `ابحث في المرفقات...`
- Search notes... ➔ `ابحث في الملاحظات...`
- Certified Engineering Content ➔ `محتوى هندسي معتمد`
- SBC Compliant ➔ `مطابق لكود البناء السعودي`
- Design Equations (SBC 304 / ACI 318) ➔ `المعادلات التصميمية المعتمدة (SBC 304 / ACI 318)`
- LaTeX Math ➔ `معادلات LaTeX الرياضية`
- Instructor Notes ➔ `ملاحظات المدرب`
- Tension-controlled ➔ `قطاع محكوم بالشد`
- My Profile ➔ `ملفي الشخصي`
- Settings ➔ `الإعدادات`
- Log out ➔ `تسجيل الخروج`
- Log in ➔ `تسجيل الدخول`
- Clear Demo Data ➔ `مسح البيانات التجريبية`
- Language ➔ `اللغة`
- Arabic ➔ `العربية`
- English ➔ `الإنجليزية`

- [ ] **Step 3: Compile ar.po to builders.mo inside Docker**
Run:
```bash
docker cp "builders/builders/locale/ar.po" docker-frappe-1:/home/frappe/frappe-bench/apps/builders/builders/locale/ar.po
docker exec -w /home/frappe/frappe-bench docker-frappe-1 bench compile-po-to-mo --app builders --force
```

- [ ] **Step 4: Verify translation coverage via i18n_coverage.py**
Run:
```bash
docker exec -w /home/frappe/frappe-bench/sites docker-frappe-1 ../env/bin/python /tmp/i18n_coverage.py lms.localhost
```
Confirm:
- Missing workspace keys = 0
- Arabic-only keys in code = 0
- Bilingual slash keys = 0

- [ ] **Step 5: Commit**
```bash
git add builders/builders/locale/ar.po scripts/generate_complete_po.py
git commit -m "feat(i18n): populate complete Arabic translation catalog and compile builders.mo"
```

---

### Task 5: Flawless RTL/LTR Direction, Typography & Formula Immunity

**Files:**
- Modify: `lms/frontend/src/styles/builders.css`
- Modify: `builders/builders/public/css/builders-theme.css`
- Modify: `builders/builders/public/css/builders-rtl.css`

**Interfaces:**
- Consumes: `[dir='rtl']` and `[dir='ltr']` on `<html>`
- Produces: Perfect typography and mirroring in Arabic RTL, clean LTR in English, with strict LTR isolation for math formulas and code.

- [ ] **Step 1: Update builders.css and theme stylesheets**
Ensure:
1. RTL typography:
```css
[dir='rtl'] body, [dir='rtl'] button, [dir='rtl'] input, [dir='rtl'] select, [dir='rtl'] textarea {
  font-family: 'IBM Plex Sans Arabic', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  text-align: right;
}
```
2. LTR typography:
```css
[dir='ltr'] body, [dir='ltr'] button, [dir='ltr'] input, [dir='ltr'] select, [dir='ltr'] textarea {
  font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  text-align: left;
}
```
3. Strict LTR immunity for engineering equations, LaTeX math, timestamps, and code:
```css
[dir='rtl'] pre,
[dir='rtl'] code,
[dir='rtl'] .code-block,
[dir='rtl'] .codemirror,
[dir='rtl'] .katex,
[dir='rtl'] .katex-display,
[dir='rtl'] [dir='ltr'],
[dir='rtl'] .engineering-formula {
  direction: ltr !important;
  text-align: left !important;
}
```
4. Mirroring for navigation icons only:
```css
[dir='rtl'] .breadcrumb-separator svg,
[dir='rtl'] .lucide-chevron-right,
[dir='rtl'] .lucide-chevrons-right {
  transform: scaleX(-1);
}
```

- [ ] **Step 2: Sync CSS files to Docker**
Run:
```bash
docker cp "lms/frontend/src/styles/builders.css" docker-frappe-1:/home/frappe/frappe-bench/apps/lms/frontend/src/styles/builders.css
docker cp "builders/builders/public/css" docker-frappe-1:/home/frappe/frappe-bench/apps/builders/builders/public/
```

- [ ] **Step 3: Commit**
```bash
git add lms/frontend/src/styles/builders.css builders/builders/public/css/
git commit -m "style(rtl): enforce RTL/LTR typography and strict LTR formula immunity"
```

---

### Task 6: Production Build & Dual-Language Live Browser Verification

**Files:**
- Test: Production bundle compilation
- Test: Chrome DevTools MCP live verification in Arabic (`ar`) and English (`en`)

- [ ] **Step 1: Production build in Docker**
Run:
```bash
docker cp "lms/frontend/src" docker-frappe-1:/home/frappe/frappe-bench/apps/lms/frontend/
docker exec -w /home/frappe/frappe-bench/apps/lms/frontend docker-frappe-1 yarn build
```
Confirm: Exit code 0, 0 compilation errors.

- [ ] **Step 2: Verify in Arabic mode (`ar`) via Chrome DevTools**
1. Set user language to `'ar'` and cookie `preferred_language=ar`.
2. Reload page `http://localhost:8000/lms/courses/sbc-304/learn/1-1`.
3. Check DOM properties: `lang === 'ar'`, `dir === 'rtl'`.
4. Check sidebar tabs: `المحتوى`, `الملاحظات`, `الأسئلة`, `المرفقات`.
5. Check Theater Mode button: `الوضع المسرحي`.
6. Click Notes tab: verify `إضافة ملاحظة عند 00:00`, `ملاحظات مثبتة`, `تصدير الملاحظات`.
7. Verify equations: $U = 1.2D + 1.6L$ cleanly rendered in LTR.
8. Capture screenshot: `C:\Users\royal\.gemini\antigravity\brain\b326ec92-a318-4349-b51e-42fac085f442\live-arabic-workspace.png`.

- [ ] **Step 3: Verify in English mode (`en`) via Chrome DevTools**
1. Set user language to `'en'` and cookie `preferred_language=en`.
2. Reload page `http://localhost:8000/lms/courses/sbc-304/learn/1-1`.
3. Check DOM properties: `lang === 'en'`, `dir === 'ltr'`.
4. Check sidebar tabs: `Outline`, `Notes`, `Q&A`, `Resources`.
5. Check Theater Mode button: `Theater Mode`.
6. Click Notes tab: verify `Add note at 00:00`, `Pinned`, `Export`.
7. Capture screenshot: `C:\Users\royal\.gemini\antigravity\brain\b326ec92-a318-4349-b51e-42fac085f442\live-english-workspace.png`.

- [ ] **Step 4: Check console messages**
Confirm 0 JavaScript runtime errors in both modes.

- [ ] **Step 5: Commit and Push**
```bash
git add .
git commit -m "feat(i18n): complete 100% bilingual Arabic & English suite with flawless RTL/LTR direction"
git push origin main
```
