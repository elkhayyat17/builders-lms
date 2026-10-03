# Design Specification: Full Bilingual Architecture & Flawless RTL/LTR Direction
# مواصفات التصميم: البنية ثنائية اللغة المتكاملة وضبط الاتجاهات RTL/LTR بنسبة 100%

**Date:** 2026-10-03  
**Status:** Approved by User  
**Scope:** Builders LMS (`builders` app + `lms/frontend` + Frappe i18n engine)

---

## 1. Executive Summary & Problem Statement

The platform is an engineering learning management system designed for Saudi Arabia and the Gulf region, serving both Arabic and international learners. The user explicitly required:
1. Full support for **BOTH languages (Arabic & English)**.
2. In **Arabic mode**: 100% pristine, professional Arabic terminology with zero English leaks, zero hardcoded English words, and zero hybrid slash labels (`عربي / English`).
3. In **English mode**: 100% clean English terminology with zero unparsed keys or missing translations.
4. Seamless **Directionality (RTL ↔ LTR)**:
   - Arabic: `dir="rtl"`, `lang="ar"`, Arabic typography (`IBM Plex Sans Arabic`), mirrored navigation, correct chevron mirroring.
   - English: `dir="ltr"`, `lang="en"`, Latin typography (`IBM Plex Sans`), standard navigation and orientation.
5. Instant one-click toggle between languages via both the top navigation toggle and the user profile dropdown.

### Root Causes of Current Imperfections
- **Audit Findings**:
  - Out of 1,764 total keys in frontend code, only 317 (18.0%) were translated in the Arabic dictionary. 1,447 keys had no Arabic translation.
  - 28 keys were written with static bilingual slashes (`العودة للأسئلة / All Questions`, `الكل / All`, `تحميل / Download`), polluting both languages.
  - 54 keys in code were written with Arabic text directly in `__('...')`, which breaks English mode completely (English mode displays Arabic).
  - Several components had raw English text not wrapped in `__()` at all (`No answers yet`, `LaTeX Math`, `My Profile`, `Settings`, `Log out`).
  - In `lms/frontend/src/translation.js`, `translate()` accessed a plain non-reactive `window.translatedMessages`, causing race conditions and flash of unlocalized content on initial load.
  - `User.language` was `None` and `System Settings.language` was empty, defaulting to English `ltr` without active translations.

---

## 2. Architecture & The 4 Pillars

```
+-----------------------------------------------------------------------------------+
|                            User Switches Language                                 |
|               (Quick Navbar Button [ع / EN] or User Dropdown)                     |
+-----------------------------------------------------------------------------------+
                                          |
          +-------------------------------+-------------------------------+
          | (Sets User.language & cookie preferred_language)               |
          v                                                               v
+-----------------------------------+           +-----------------------------------+
|           ARABIC MODE             |           |           ENGLISH MODE            |
|-----------------------------------|           |-----------------------------------|
| • <html lang="ar" dir="rtl">      |           | • <html lang="en" dir="ltr">      |
| • Font: IBM Plex Sans Arabic      |           | • Font: IBM Plex Sans / Inter     |
| • Logical CSS: ms-*, me-*, start-*|           | • Logical CSS: standard LTR flow  |
| • Icons: RTL chevrons mirrored    |           | • Icons: standard LTR chevrons    |
| • Dict: 100% Arabic gettext       |           | • Dict: Clean English base keys   |
| • Pure Arabic Engineering Terms   |           | • Pure English Engineering Terms  |
| • ZERO English leaks              |           | • ZERO Arabic leaks in English    |
+-----------------------------------+           +-----------------------------------+
```

### Pillar 1: Clean Semantic Base Keys in Frontend Code
- **Rule**: All base keys passed to `__()` in Vue/TS/JS MUST be concise, professional English semantic keys.
- **Eliminate all slashes**:
  - `__('العودة للأسئلة / All Questions')` ➔ `__('Back to Questions')`
  - `__('الكل / All')` ➔ `__('All')`
  - `__('تحميل / Download')` ➔ `__('Download')`
  - `__('ابحث في الفصول والدروس... / Search lessons...')` ➔ `__('Search lessons...')`
  - `__('دروس / lessons')` ➔ `__('Lessons')`
  - `__('طرح استفسار جديد / Ask a Question')` ➔ `__('Ask a Question')`
- **Wrap all unlocalized English strings**:
  - `No answers yet. Be the first to help!` ➔ `__('No answers yet. Be the first to help!')`
  - `LaTeX Math` ➔ `__('LaTeX Math')`
  - `My Profile` ➔ `__('My Profile')`
  - `Settings` ➔ `__('Settings')`
  - `Log out` ➔ `__('Log out')`
  - `Log in` ➔ `__('Log in')`
  - `Clear Demo Data` ➔ `__('Clear Demo Data')`

### Pillar 2: Reactive Translation Plugin (`translation.js`)
- Replace the non-reactive `window.translatedMessages` lookup with a reactive Vue ref:
  ```javascript
  import { ref } from 'vue'
  export const translations = ref({})
  ```
- When translations load, update `translations.value`. This triggers instant, clean reactivity across all components without needing manual reloads.
- Also inject initial translations during server-side boot in `_lms.py` if available to prevent any Flash of Unlocalized Text (FOUT).

### Pillar 3: Comprehensive Arabic PO Catalog (`ar.po` & `builders.mo`)
- Add every single frontend key used in the workspace and LMS to `builders/builders/locale/ar.po`.
- Ensure high-standard Gulf & Saudi engineering terminology:
  - `Standard Mode`: `الوضع القياسي`
  - `Theater Mode`: `الوضع المسرحي`
  - `Pinned`: `ملاحظات مثبتة`
  - `Pin note`: `تثبيت الملاحظة`
  - `Export`: `تصدير الملاحظات`
  - `Add note at {0}`: `إضافة ملاحظة عند {0}`
  - `Video paused`: `تم إيقاف الفيديو مؤقتاً`
  - `Course Outline`: `محتوى المساق`
  - `Discussions & Q&A`: `الأسئلة والنقاشات`
  - `Engineering Resources`: `المرفقات الهندسية`
  - `Calculation Sheet`: `شيت حسابات وتصميم`
  - `CAD Drawing`: `مخطط أوتوكاد إنشائي`
  - `Engineering Code`: `كود ومواصفات هندسية`
- Compile `.po` to `.mo` using `frappe.gettext` / `bench compile-po-to-mo`.
- Register runtime translations in Frappe's translation cache so `lms.lms.api.get_translations` returns the full dictionary.

### Pillar 4: Directional Precision (RTL & LTR)
- Ensure `<html lang="ar" dir="rtl">` or `<html lang="en" dir="ltr">` is set accurately on page load in `_lms.html` and synced by `setAppLanguage()`.
- CSS styling in `builders.css` & `builders-rtl.css`:
  - `[dir='rtl']` sets font to `'IBM Plex Sans Arabic'` and text alignment to `right`.
  - `[dir='ltr']` sets font to `'IBM Plex Sans', sans-serif` and text alignment to `left`.
  - Math, LaTeX formulas, code snippets, and timestamps strictly retain `direction: ltr !important; text-align: left;` in both modes because equations ($U = 1.2D + 1.6L$) and code are internationally LTR.
  - Breadcrumbs and chevrons properly mirror using CSS transform `scaleX(-1)` only in RTL.

---

## 3. Affected Files Matrix

| File | Change Required |
|---|---|
| `lms/frontend/src/translation.js` | Make translations reactive using Vue `ref`, export reactive store |
| `lms/frontend/src/components/LessonWorkspace/tabs/LessonOutlineTab.vue` | Remove all bilingual slashes, use clean English keys in `__()` |
| `lms/frontend/src/components/LessonWorkspace/tabs/LessonQATab.vue` | Remove all bilingual slashes, wrap all hardcoded English in `__()` |
| `lms/frontend/src/components/LessonWorkspace/tabs/LessonResourcesTab.vue` | Remove bilingual slashes, wrap CAD/Excel/PDF category labels in `__()` |
| `lms/frontend/src/components/LessonWorkspace/tabs/TimestampedNotes.vue` | Use clean English keys in `__()`, clean up printable export template |
| `lms/frontend/src/components/LessonWorkspace/LessonSidebar.vue` | Remove bilingual strings, use clean English tab keys |
| `lms/frontend/src/components/LessonWorkspace/LessonOverview.vue` | Clean up bilingual labels, wrap `LaTeX Math` and citations in `__()` |
| `lms/frontend/src/pages/Lesson.vue` | Use clean English keys for Theater Mode, Zen Mode, Questions |
| `lms/frontend/src/components/Sidebar/UserDropdown.vue` | Wrap all menu items in `__()`, remove `Language / اللغة` slash |
| `lms/frontend/src/components/VideoBlock.vue` | Clean up plural strings and transport button tooltips |
| `builders/builders/locale/ar.po` | Complete translation catalog with 100% Arabic coverage for all keys |
| `builders/builders/setup.py` | Clean backend labels to standard Frappe style with clean translations |
| `builders/builders/public/js/language-toggle.js` | Ensure instant RTL/LTR switching and cookie/user persistence |
| `builders/builders/public/css/builders-theme.css` | Verify typography and direction tokens |
| `builders/builders/public/css/builders-rtl.css` | Mirroring rules for RTL |

---

## 4. Verification & Success Criteria

1. **Test Suite**:
   - `scripts/i18n_coverage.py`: Missing Arabic keys reduced to 0 for all workspace and primary LMS components.
   - Arabic-only keys in code reduced to 0.
   - Bilingual slash keys reduced to 0.
2. **Build Verification**:
   - `yarn build` in container finishes with code 0 and 0 errors.
3. **Live Browser Verification (Chrome DevTools MCP)**:
   - In Arabic (`lang="ar", dir="rtl"`):
     - Workspace loads with `dir="rtl"`.
     - Sidebar tabs display: `المحتوى`, `الملاحظات`, `الأسئلة`, `المرفقات`.
     - Theater Mode button displays: `الوضع المسرحي`.
     - Notes tab displays: `إضافة ملاحظة عند 00:00`, `ملاحظات مثبتة`, `تصدير الملاحظات`.
     - Zero English leaks in buttons, labels, placeholders, or badges.
     - LaTeX equations remain cleanly formatted in LTR.
   - In English (`lang="en", dir="ltr"`):
     - Workspace toggles smoothly to `dir="ltr"`.
     - Sidebar tabs display: `Outline`, `Notes`, `Q&A`, `Resources`.
     - Theater Mode button displays: `Theater Mode`.
     - Notes tab displays: `Add note at 00:00`, `Pinned`, `Export`.
     - Zero unparsed Arabic keys or slashes.
