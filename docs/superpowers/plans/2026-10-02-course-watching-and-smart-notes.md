# Next-Gen Engineering Course Watching & Timestamped Smart Notes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the civil engineering course watching experience into a high-performance, Coursera/Udemy Pro workspace with interactive Theater Mode, timestamped smart notes, and a unified multi-tab sidebar without conflicting with existing video security or ABR streaming.

**Architecture:** Refactor `Lesson.vue` into a modular, split-grid workspace. Expose a playback control interface (`defineExpose`) in `VideoBlock.vue`. Implement an isolated `TimestampedNotes.vue` component that syncs time with video playback and persists to Frappe LMS's `LMS Lesson Note` via non-invasive custom fields (`video_timestamp`, `formatted_time`). Integrate a multi-tab sidebar featuring Outline, Notes, Q&A, and Engineering Resources with Theater Mode.

**Tech Stack:** Vue 3 (Composition API, `<script setup>`), TypeScript, Tailwind CSS, Frappe UI, Frappe Framework (Python / MariaDB), HLS.js, Chrome DevTools MCP.

**Spec:** [`docs/superpowers/specs/2026-10-02-course-watching-and-smart-notes-design.md`](file:///d:/Coding/LMS%20civil/docs/superpowers/specs/2026-10-02-course-watching-and-smart-notes-design.md)

## Global Constraints
- Preserve all existing AES-128 HLS decryption, ABR multi-rendition streaming (1080p -> 360p), permanent forensic watermark, and screen recording lockdown shields in `VideoBlock.vue`.
- Non-invasive backend extension: Add custom fields to `LMS Lesson Note` via `create_custom_fields` in `builders/setup.py` without modifying core Frappe LMS DocType schemas directly.
- Maintain backward compatibility: Notes without timestamps must render gracefully as general notes.
- Zero layout shift (CLS): 16:9 video container dimensions must remain stable.
- All interactive elements must follow UI/UX Pro Max standards: touch targets >= 44px, proper contrast ratios, and keyboard accessible focus states.

---

### Task 1: Backend Data Model Extension for Timestamped Notes

**Files:**
- Modify: `builders/builders/setup.py`
- Create: `scripts/test_notes_backend.py`

**Interfaces:**
- Consumes: Frappe's `create_custom_fields` API and DocType `LMS Lesson Note`.
- Produces: `LMS Lesson Note` with custom fields `video_timestamp` (Float), `formatted_time` (Data), and `is_pinned` (Check).

- [ ] **Step 1: Write test script to verify `LMS Lesson Note` custom fields**

```python
# scripts/test_notes_backend.py
import frappe

def run():
    frappe.init(site="localhost", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()

    meta = frappe.get_meta("LMS Lesson Note")
    has_timestamp = meta.has_field("video_timestamp")
    has_formatted = meta.has_field("formatted_time")
    has_pinned = meta.has_field("is_pinned")

    print(f"video_timestamp: {has_timestamp}")
    print(f"formatted_time: {has_formatted}")
    print(f"is_pinned: {has_pinned}")

    assert has_timestamp and has_formatted and has_pinned, "Custom fields missing on LMS Lesson Note!"
    print("ALL_CUSTOM_FIELDS_VERIFIED")

if __name__ == "__main__":
    run()
```

- [ ] **Step 2: Run test script to verify it fails before schema update**

Run: `docker exec -w /home/frappe/frappe-bench docker-frappe-1 python -c "import frappe; frappe.init('localhost', sites_path='sites'); frappe.connect(); meta = frappe.get_meta('LMS Lesson Note'); assert meta.has_field('video_timestamp'), 'Missing video_timestamp'"`
Expected: FAIL with `AssertionError: Missing video_timestamp`.

- [ ] **Step 3: Update `builders/builders/setup.py` to register custom fields on `LMS Lesson Note`**

Add custom fields to `create_builders_custom_fields()` in `builders/builders/setup.py`:
```python
"LMS Lesson Note": [
    {
        "fieldname": "video_timestamp",
        "label": "Video Timestamp (Seconds)",
        "fieldtype": "Float",
        "insert_after": "color",
        "module": "Builders",
    },
    {
        "fieldname": "formatted_time",
        "label": "Formatted Time (mm:ss)",
        "fieldtype": "Data",
        "insert_after": "video_timestamp",
        "module": "Builders",
    },
    {
        "fieldname": "is_pinned",
        "label": "Pinned Note",
        "fieldtype": "Check",
        "insert_after": "formatted_time",
        "module": "Builders",
    },
]
```
Execute setup in docker container:
`docker exec -w /home/frappe/frappe-bench docker-frappe-1 bench --site localhost execute builders.builders.setup.after_install`

- [ ] **Step 4: Run test script to verify custom fields pass**

Run: `docker exec -w /home/frappe/frappe-bench docker-frappe-1 python -c "import frappe; frappe.init('localhost', sites_path='sites'); frappe.connect(); meta = frappe.get_meta('LMS Lesson Note'); assert meta.has_field('video_timestamp') and meta.has_field('formatted_time') and meta.has_field('is_pinned'); print('PASS')"`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add builders/builders/setup.py scripts/test_notes_backend.py
git commit -m "feat(backend): add video_timestamp and formatted_time custom fields to LMS Lesson Note"
```

---

### Task 2: Video Player Interop API in `VideoBlock.vue`

**Files:**
- Modify: `lms/frontend/src/components/VideoBlock.vue:1040-1090`

**Interfaces:**
- Consumes: Native HTML5 `videoRef` element and existing HLS state.
- Produces: `defineExpose({ getCurrentTime, seekTo, pauseVideo, resumeVideo, isPlaying })` callable by parent and sibling components.

- [ ] **Step 1: Check existing `defineExpose` in `VideoBlock.vue`**

Inspect lines 1040-1090 in `lms/frontend/src/components/VideoBlock.vue` to confirm exposed methods.

- [ ] **Step 2: Add exposed playback and seeking methods in `VideoBlock.vue`**

Add functions inside `<script setup>`:
```typescript
const getCurrentTime = (): number => {
	return videoRef.value ? videoRef.value.currentTime : currentTime.value
}

const seekTo = (seconds: number) => {
	if (videoRef.value) {
		const target = Math.max(0, Math.min(seconds, duration.value || seconds))
		videoRef.value.currentTime = target
		currentTime.value = target
		if (videoRef.value.paused) {
			videoRef.value.play().catch(() => {})
		}
	}
}

const pauseVideo = () => {
	if (videoRef.value && !videoRef.value.paused) {
		videoRef.value.pause()
	}
}

const resumeVideo = () => {
	if (videoRef.value && videoRef.value.paused) {
		videoRef.value.play().catch(() => {})
	}
}

defineExpose({
	getCurrentTime,
	seekTo,
	pauseVideo,
	resumeVideo,
	resetTamperState,
	resolveCaptureLockdown,
	playing,
})
```

- [ ] **Step 3: Test compilation**

Run: `docker exec -w /home/frappe/frappe-bench/apps/lms/frontend docker-frappe-1 yarn build`
Expected: Exited with code 0.

- [ ] **Step 4: Commit changes**

```bash
git add lms/frontend/src/components/VideoBlock.vue
git commit -m "feat(player): expose playback control and seeking interface in VideoBlock.vue"
```

---

### Task 3: Timestamped Smart Notes Component (`TimestampedNotes.vue`)

**Files:**
- Create: `lms/frontend/src/components/LessonWorkspace/tabs/TimestampedNotes.vue`
- Create: `builders/builders/public/js/notes-exporter.js` or backend export helper in `builders/builders/utils.py`

**Interfaces:**
- Consumes: `lesson` (string), `course` (string), `videoPlayer` (exposed interface from `VideoBlock.vue`).
- Produces: Reactive interactive note list, note creation with timestamp capture, jump-to-time sync on click, edit/delete, and export to printable HTML/PDF.

- [ ] **Step 1: Implement `TimestampedNotes.vue` with Udemy-style card architecture**

Features to implement in `lms/frontend/src/components/LessonWorkspace/tabs/TimestampedNotes.vue`:
1. "Add note at mm:ss" quick trigger button reading `videoPlayer.getCurrentTime()`.
2. Global keyboard shortcut listener for `N` (ignores when user focuses text inputs).
3. Auto-pause video on note creation; auto-resume on save or dismiss.
4. Note cards list ordered by `video_timestamp asc`:
   - Interactive timestamp pill: clicking calls `videoPlayer.seekTo(note.video_timestamp)`.
   - Formatted note body.
   - Edit and delete actions.
5. Search input filtering notes by query text.
6. Export notes button: compiles current notes into a formatted printable document with course branding.

- [ ] **Step 2: Sync and build frontend**

Copy `TimestampedNotes.vue` into container and verify compilation via:
`docker exec -w /home/frappe/frappe-bench/apps/lms/frontend docker-frappe-1 yarn build`
Expected: Build passes with 0 errors.

- [ ] **Step 3: Commit changes**

```bash
git add lms/frontend/src/components/LessonWorkspace/tabs/TimestampedNotes.vue
git commit -m "feat(notes): implement TimestampedNotes component with video sync and export"
```

---

### Task 4: Interactive Multi-Tab Sidebar Components

**Files:**
- Create: `lms/frontend/src/components/LessonWorkspace/tabs/LessonOutlineTab.vue`
- Create: `lms/frontend/src/components/LessonWorkspace/tabs/LessonQATab.vue`
- Create: `lms/frontend/src/components/LessonWorkspace/tabs/LessonResourcesTab.vue`
- Create: `lms/frontend/src/components/LessonWorkspace/LessonSidebar.vue`

**Interfaces:**
- Consumes: `courseName`, `currentLesson`, `chapters`, `videoPlayer`, `allowDiscussions`.
- Produces: Unified sidebar container with 4 switchable tabs (Outline, Notes, Q&A, Resources).

- [ ] **Step 1: Implement `LessonOutlineTab.vue`**
Renders course curriculum chapters and lessons tree with completion badges (`✓`), durations, and active lesson indicator.

- [ ] **Step 2: Implement `LessonQATab.vue`**
Wraps Frappe LMS discussions with timestamp anchoring (`[✓] Link to current video timestamp`).

- [ ] **Step 3: Implement `LessonResourcesTab.vue`**
Lists downloadable civil engineering course resources (Excel sheets for SBC 304, CAD DWG files, calculation PDFs) with file format badges and instant download triggers.

- [ ] **Step 4: Implement `LessonSidebar.vue`**
Tab navigation container (`📑 Outline`, `📝 Notes`, `💬 Q&A`, `📎 Resources`) with persistent active state and smooth tab transitions.

- [ ] **Step 5: Verify build in docker container**

Run: `docker exec -w /home/frappe/frappe-bench/apps/lms/frontend docker-frappe-1 yarn build`
Expected: Code 0.

- [ ] **Step 6: Commit changes**

```bash
git add lms/frontend/src/components/LessonWorkspace/
git commit -m "feat(sidebar): create unified interactive multi-tab sidebar for course workspace"
```

---

### Task 5: Coursera/Udemy Workspace Grid & Theater Mode in `Lesson.vue`

**Files:**
- Create: `lms/frontend/src/components/LessonWorkspace/LessonOverview.vue`
- Modify: `lms/frontend/src/pages/Lesson.vue`

**Interfaces:**
- Consumes: `LessonSidebar`, `LessonOverview`, `VideoBlock`, route parameters.
- Produces: The complete Coursera/Udemy workspace layout with Theater Mode toggle and responsive adaptation.

- [ ] **Step 1: Implement `LessonOverview.vue`**
Extracts lecture content, instructor profiles, instructor notes, and mathematical LaTeX formulas into a clean, legible engineering overview section below the player.

- [ ] **Step 2: Update `Lesson.vue` with Theater Mode and Split Grid**
- Add `isTheaterMode` reactive state (persisted in localStorage).
- In standard mode: 70% main column (Video + Overview) / 30% sticky sidebar (`LessonSidebar.vue`).
- In theater mode: Video expands to 100% full-width at the top; sidebar and overview reposition beneath in a clean 2-column or stacked layout.
- Add Theater Mode button next to Zen Mode and video controls.
- Provide `videoPlayerRef` to sidebar and notes.

- [ ] **Step 3: Build and test frontend compilation**

Run: `docker exec -w /home/frappe/frappe-bench/apps/lms/frontend docker-frappe-1 yarn build`
Expected: Code 0.

- [ ] **Step 4: Commit changes**

```bash
git add lms/frontend/src/pages/Lesson.vue lms/frontend/src/components/LessonWorkspace/LessonOverview.vue
git commit -m "feat(workspace): integrate Coursera/Udemy hybrid layout with Theater Mode in Lesson.vue"
```

---

### Task 6: Production Build, Live Integration & DevTools Verification

**Files:**
- Test: Live testing on `http://localhost:8000/lms/courses/sbc-304/learn/1-1` via Chrome DevTools MCP.

**Interfaces:**
- End-to-end user experience in Chrome browser.

- [ ] **Step 1: Synchronize all frontend and backend changes into Docker container**
Ensure all updated files in `lms/frontend` and `builders` are copied to `/home/frappe/frappe-bench/apps/`.

- [ ] **Step 2: Execute production build and migrate bench**
Run `yarn build` in `lms/frontend`, copy build output to `/home/frappe/frappe-bench/apps/lms/lms/public/frontend`, and restart bench workers.

- [ ] **Step 3: Navigate and test live in Chrome via `chrome-devtools-mcp`**
- Reload `pageId: 2` with `ignoreCache: true`.
- Verify the new Coursera/Udemy layout renders.
- Verify the 4 tabs in the sidebar: Outline, Notes, Q&A, Resources.
- Create a timestamped note at `00:20` and verify:
  1. Video pauses automatically.
  2. Note appears with `[00:20]` pill badge.
  3. Clicking the pill badge jumps the video to 20s and resumes playback.
- Click the Theater Mode button and verify video expands to full width.
- Verify security shields and forensic watermark continue to function.

- [ ] **Step 4: Capture screenshots of the live system and verify visual polish**
Use `take_screenshot` in Chrome DevTools to save visual proof of:
1. Normal Split Grid with Smart Notes tab active.
2. Theater Mode layout.

- [ ] **Step 5: Final git commit and push to `origin/main`**

```bash
git add .
git commit -m "feat: complete next-gen engineering course watching and smart notes suite"
git push origin main
```
