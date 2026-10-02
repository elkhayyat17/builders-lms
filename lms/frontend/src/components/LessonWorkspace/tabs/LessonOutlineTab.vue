<template>
	<div class="lesson-outline-tab flex flex-col h-full min-h-0">
		<!-- Outline Header & Search -->
		<div class="px-4 pt-3 pb-2 shrink-0 border-b border-outline-gray-2 bg-surface-base">
			<!-- Overall Course Progress Bar -->
			<div v-if="withProgress" class="mb-3">
				<div class="flex items-center justify-between text-xs font-medium text-ink-gray-7 mb-1.5">
					<span class="inline-flex items-center gap-1.5">
						<GraduationCap class="size-3.5 text-ink-blue-5" />
						<span>{{ __('مسار الدورة') }} • {{ __('Course Progress') }}</span>
					</span>
					<span class="font-bold tabular-nums text-ink-gray-9">{{ displayedProgress }}%</span>
				</div>
				<div class="h-1.5 w-full rounded-full bg-surface-gray-2 overflow-hidden">
					<div
						class="h-full bg-surface-green-3 transition-all duration-300 rounded-full"
						:style="{ width: `${displayedProgress}%` }"
					/>
				</div>
			</div>

			<!-- Search & Control Actions -->
			<div class="flex items-center gap-2">
				<div class="relative flex-1 min-w-0">
					<Search class="absolute start-2.5 top-1/2 -translate-y-1/2 size-3.5 text-ink-gray-4 pointer-events-none" />
					<input
						type="text"
						v-model="searchQuery"
						:placeholder="__('ابحث في الفصول والدروس... / Search lessons...')"
						class="w-full ps-8 pe-7 py-1.5 rounded-6 border border-outline-gray-2 bg-surface-gray-1 text-xs text-ink-gray-9 placeholder:text-ink-gray-4 focus:bg-surface-base focus:outline-none focus:ring-2 focus:ring-outline-blue-2 transition-all"
					/>
					<button
						v-if="searchQuery"
						type="button"
						@click="searchQuery = ''"
						class="absolute end-2 top-1/2 -translate-y-1/2 p-0.5 rounded-full text-ink-gray-4 hover:text-ink-gray-7"
						:title="__('Clear search')"
					>
						<X class="size-3" />
					</button>
				</div>

				<!-- Expand / Collapse All Toggle -->
				<button
					type="button"
					@click="toggleAllChapters"
					class="p-1.5 rounded-6 border border-outline-gray-2 bg-surface-base hover:bg-surface-gray-2 text-ink-gray-6 hover:text-ink-gray-9 text-xs font-medium transition-colors cursor-pointer shrink-0"
					:title="allExpanded ? __('Collapse all chapters') : __('Expand all chapters')"
				>
					<component :is="allExpanded ? ChevronsDownUp : ChevronsUpDown" class="size-3.5" />
				</button>
			</div>

			<!-- Chapter / Lesson Quick Summary -->
			<div class="flex items-center justify-between text-xs text-ink-gray-5 mt-2">
				<span>
					{{ totalLessonsCount }} {{ totalLessonsCount === 1 ? __('درس') : __('دروس') }}
					({{ totalLessonsCount }} {{ totalLessonsCount === 1 ? 'lesson' : 'lessons' }})
				</span>
				<span v-if="completedCount > 0" class="inline-flex items-center gap-1 text-ink-green-8">
					<CheckCircle2 class="size-3" />
					{{ completedCount }} {{ __('مكتمل') }}
				</span>
			</div>
		</div>

		<!-- Chapters & Lessons Accordion List -->
		<div class="flex-1 min-h-0 overflow-y-auto px-2 py-2">
			<!-- Loading State -->
			<div v-if="outline.loading" class="py-12 flex flex-col items-center justify-center gap-2 text-ink-gray-5">
				<Loader2 class="size-6 animate-spin text-ink-blue-5" />
				<span class="text-xs">{{ __('جاري تحميل الفصول والدروس...') }}</span>
			</div>

			<!-- Empty Search State -->
			<div
				v-else-if="filteredChapters.length === 0 && searchQuery"
				class="rounded-7 border border-dashed border-outline-gray-2 p-8 text-center my-4"
			>
				<SearchX class="size-8 text-ink-gray-4 mx-auto mb-2" />
				<h4 class="text-xs font-semibold text-ink-gray-9 mb-1">
					{{ __('لم يتم العثور على نتائج للبحث') }}
				</h4>
				<p class="text-xs text-ink-gray-5 mb-3">
					{{ __('No lessons matching "{0}"').replace('{0}', searchQuery) }}
				</p>
				<button
					type="button"
					@click="searchQuery = ''"
					class="inline-flex items-center gap-1 px-3 py-1 text-xs font-medium rounded-6 bg-surface-gray-2 hover:bg-surface-gray-3 text-ink-gray-8 transition-colors cursor-pointer"
				>
					{{ __('مسح البحث / Clear search') }}
				</button>
			</div>

			<!-- Empty Outline State -->
			<div
				v-else-if="filteredChapters.length === 0"
				class="rounded-7 border border-dashed border-outline-gray-2 p-8 text-center my-4"
			>
				<BookOpen class="size-8 text-ink-gray-4 mx-auto mb-2" />
				<h4 class="text-xs font-semibold text-ink-gray-9 mb-1">
					{{ __('لا توجد فصول دراسية متاحة حالياً') }}
				</h4>
				<p class="text-xs text-ink-gray-5">
					{{ __('No curriculum outline available for this course yet.') }}
				</p>
			</div>

			<!-- Chapter List -->
			<div v-else class="space-y-1.5">
				<div
					v-for="chapter in filteredChapters"
					:key="chapter.name || chapter.idx"
					class="rounded-6 border border-outline-gray-2 bg-surface-base overflow-hidden transition-all duration-200"
				>
					<!-- Chapter Header Toggle -->
					<button
						type="button"
						@click="toggleChapter(chapter.name || String(chapter.idx))"
						class="w-full flex items-center justify-between px-3 py-2.5 bg-surface-gray-1 hover:bg-surface-gray-2 text-start transition-colors cursor-pointer group"
					>
						<div class="flex items-center gap-2 min-w-0 flex-1 me-2">
							<ChevronDown
								class="size-4 shrink-0 text-ink-gray-5 group-hover:text-ink-gray-8 transition-transform duration-200"
								:class="{ '-rotate-90': !isChapterOpen(chapter.name || String(chapter.idx)) }"
							/>
							<div class="min-w-0 flex-1">
								<div class="flex items-center gap-1.5">
									<span class="text-xs font-bold text-ink-gray-9 truncate">
										{{ chapter.title }}
									</span>
								</div>
								<div class="flex items-center gap-2 text-[11px] text-ink-gray-5 mt-0.5">
									<span>
										{{ chapter.lessons?.length || 0 }} {{ __('دروس / lessons') }}
									</span>
									<span v-if="getChapterCompletedCount(chapter) > 0" class="text-ink-green-8 font-medium">
										• {{ getChapterCompletedCount(chapter) }}/{{ chapter.lessons?.length || 0 }} {{ __('مكتمل') }}
									</span>
								</div>
							</div>
						</div>

						<!-- Chapter Status Badge -->
						<div class="shrink-0 flex items-center gap-1.5">
							<div
								v-if="isChapterFullyComplete(chapter)"
								class="size-5 rounded-full bg-surface-green-3/20 flex items-center justify-center text-ink-green-8"
								:title="__('الفصل مكتمل بالكامل / Chapter completed')"
							>
								<CheckCircle2 class="size-3.5 fill-current" />
							</div>
							<span
								v-else-if="chapter.lessons?.length"
								class="px-1.5 py-0.5 rounded-full text-[10px] font-semibold bg-surface-gray-2 text-ink-gray-6 tabular-nums"
							>
								{{ getChapterCompletedCount(chapter) }}/{{ chapter.lessons.length }}
							</span>
						</div>
					</button>

					<!-- Chapter Lessons List (Collapsible) -->
					<div
						v-show="isChapterOpen(chapter.name || String(chapter.idx))"
						class="divide-y divide-outline-gray-2 border-t border-outline-gray-2 bg-surface-base"
					>
						<button
							v-for="lesson in chapter.lessons || []"
							:key="lesson.name || lesson.number"
							type="button"
							@click="onLessonClick(lesson)"
							:disabled="lesson.locked"
							class="w-full flex items-center gap-2.5 px-3 py-2 text-start transition-all duration-150 group/item relative cursor-pointer"
							:class="[
								lesson.locked
									? 'opacity-60 cursor-not-allowed bg-surface-gray-1/50'
									: 'hover:bg-surface-gray-2',
								isLessonActive(lesson)
									? 'bg-surface-blue-2 text-ink-blue-5 font-medium'
									: 'text-ink-gray-8',
							]"
						>
							<!-- Active Strip Indicator -->
							<div
								v-if="isLessonActive(lesson)"
								class="absolute start-0 top-0 bottom-0 w-1 bg-surface-blue-5 rounded-e"
							/>

							<!-- Status Icon (Left/Start) -->
							<div class="shrink-0">
								<!-- Locked Icon -->
								<template v-if="lesson.locked">
									<LockKeyhole
										class="size-3.5 text-ink-gray-4"
										:title="__('مغلق - أكمل الدروس السابقة لفتحه / Locked')"
									/>
								</template>

								<!-- Completed Icon -->
								<template v-else-if="lesson.is_complete">
									<CheckCircle2
										class="size-3.5 text-ink-green-8 fill-surface-green-3/30"
										:title="__('تم إكمال هذا الدرس / Completed')"
									/>
								</template>

								<!-- Active Icon -->
								<template v-else-if="isLessonActive(lesson)">
									<div class="size-3.5 rounded-full border-2 border-surface-blue-5 flex items-center justify-center">
										<div class="size-1.5 rounded-full bg-surface-blue-5" />
									</div>
								</template>

								<!-- Incomplete Icon -->
								<template v-else>
									<Circle class="size-3.5 text-ink-gray-4 group-hover/item:text-ink-gray-6" />
								</template>
							</div>

							<!-- Lesson Content Icon (Video, Quiz, Doc, etc.) -->
							<component
								:is="getLessonTypeIcon(lesson.icon)"
								class="size-3.5 shrink-0"
								:class="isLessonActive(lesson) ? 'text-ink-blue-5' : 'text-ink-gray-5'"
							/>

							<!-- Lesson Title & Info -->
							<div class="min-w-0 flex-1">
								<div class="flex items-center gap-1.5">
									<span
										class="text-xs truncate block"
										:class="isLessonActive(lesson) ? 'font-semibold text-ink-blue-5' : 'text-ink-gray-8 group-hover/item:text-ink-gray-9'"
									>
										{{ lesson.title }}
									</span>
								</div>

								<!-- Optional Duration / Number -->
								<div class="flex items-center gap-2 text-[10px] text-ink-gray-5 mt-0.5">
									<span v-if="lesson.number" class="font-mono">{{ lesson.number }}</span>
									<span v-if="lesson.duration" class="tabular-nums">
										• {{ formatDuration(lesson.duration) }}
									</span>
								</div>
							</div>

							<!-- Active Badge / Locked Pill -->
							<div class="shrink-0 flex items-center">
								<span
									v-if="isLessonActive(lesson)"
									class="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-surface-blue-3 text-ink-blue-5"
								>
									{{ __('الآن') }}
								</span>
								<LockKeyhole v-else-if="lesson.locked" class="size-3 text-ink-gray-4" />
							</div>
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, ref, watch, watchEffect } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createResource } from 'frappe-ui'
import {
	BookOpen,
	CheckCircle2,
	ChevronDown,
	ChevronsDownUp,
	ChevronsUpDown,
	Circle,
	FileText,
	GraduationCap,
	HelpCircle,
	Loader2,
	LockKeyhole,
	MonitorPlay,
	NotebookPen,
	Search,
	SearchX,
	SquareCode,
	X,
} from 'lucide-vue-next'

interface LessonItem {
	name: string
	title: string
	number: string
	icon?: string
	locked?: boolean
	is_complete?: boolean
	duration?: number
}

interface ChapterItem {
	name?: string
	title: string
	idx?: number
	lessons?: LessonItem[]
}

interface Props {
	courseName: string
	courseTitle?: string
	currentLesson?: string
	currentLessonNumber?: string
	selectedLessonNumber?: string
	completedLesson?: string | null
	progress?: number
	withProgress?: boolean
	inlineSelect?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	courseTitle: '',
	currentLesson: '',
	currentLessonNumber: '',
	selectedLessonNumber: '',
	completedLesson: null,
	progress: 0,
	withProgress: true,
	inlineSelect: false,
})

const emit = defineEmits<{
	(e: 'switchLesson', lessonNumber: string): void
	(e: 'select-lesson', payload: { chapterNumber: string; lessonNumber: string; name?: string }): void
}>()

const router = useRouter()
const route = useRoute()
const searchQuery = ref('')
const openChapters = ref<Set<string>>(new Set())
const allExpanded = ref(true)

const __ = (text: string) => (typeof window !== 'undefined' && (window as any).__ ? (window as any).__(text) : text)

const activeLessonIdentifier = computed(() => {
	return props.currentLessonNumber || props.selectedLessonNumber || ''
})

// Outline Resource
const outline = createResource({
	url: 'lms.lms.utils.get_course_outline',
	cache: [
		'course_outline_student',
		props.courseName,
		props.withProgress ? 'progress' : 'no-progress',
	],
	makeParams() {
		return {
			course: props.courseName,
			progress: props.withProgress,
		}
	},
	auto: Boolean(props.courseName),
})

watch(
	() => props.courseName,
	(newVal) => {
		if (newVal) outline.reload()
	}
)

// Reactively apply completedLesson updates
watchEffect(() => {
	const lessonName = props.completedLesson
	if (!lessonName || !outline.data) return
	for (const chapter of outline.data as ChapterItem[]) {
		const found = chapter.lessons?.find((l) => l.name === lessonName)
		if (found) {
			found.is_complete = true
			return
		}
	}
})

// Auto-open chapter containing the active lesson
watch(
	() => [outline.data, activeLessonIdentifier.value, props.currentLesson],
	() => {
		if (!outline.data) return
		const chapters = outline.data as ChapterItem[]
		for (const ch of chapters) {
			const id = ch.name || String(ch.idx)
			const hasActive = ch.lessons?.some((l) => {
				return (
					(activeLessonIdentifier.value && l.number === activeLessonIdentifier.value) ||
					(props.currentLesson && (l.name === props.currentLesson || l.number === props.currentLesson))
				)
			})
			if (hasActive) {
				openChapters.value.add(id)
			}
		}
		// Default: if no chapter opened yet, open first chapter
		if (openChapters.value.size === 0 && chapters.length > 0) {
			const firstId = chapters[0].name || String(chapters[0].idx)
			openChapters.value.add(firstId)
		}
	},
	{ immediate: true, deep: true }
)

const displayedProgress = computed(() => Math.ceil(props.progress || 0))

// Total lessons count
const totalLessonsCount = computed(() => {
	if (!outline.data) return 0
	return (outline.data as ChapterItem[]).reduce((acc, ch) => acc + (ch.lessons?.length || 0), 0)
})

// Completed lessons count
const completedCount = computed(() => {
	if (!outline.data) return 0
	return (outline.data as ChapterItem[]).reduce((acc, ch) => {
		return acc + (ch.lessons?.filter((l) => l.is_complete)?.length || 0)
	}, 0)
})

// Filtered chapters according to search query
const filteredChapters = computed(() => {
	if (!outline.data) return []
	const list = outline.data as ChapterItem[]
	const q = searchQuery.value.trim().toLowerCase()
	if (!q) return list

	return list
		.map((ch) => {
			const chapterTitleMatches = ch.title.toLowerCase().includes(q)
			const matchingLessons = (ch.lessons || []).filter((l) => {
				return (
					l.title.toLowerCase().includes(q) ||
					(l.number && l.number.toLowerCase().includes(q))
				)
			})

			if (chapterTitleMatches) {
				return ch
			}

			if (matchingLessons.length > 0) {
				return {
					...ch,
					lessons: matchingLessons,
				}
			}

			return null
		})
		.filter((ch): ch is ChapterItem => ch !== null)
})

function isChapterOpen(chapterId: string): boolean {
	return openChapters.value.has(chapterId)
}

function toggleChapter(chapterId: string) {
	if (openChapters.value.has(chapterId)) {
		openChapters.value.delete(chapterId)
	} else {
		openChapters.value.add(chapterId)
	}
}

function toggleAllChapters() {
	if (allExpanded.value) {
		openChapters.value.clear()
		allExpanded.value = false
	} else {
		if (outline.data) {
			for (const ch of outline.data as ChapterItem[]) {
				const id = ch.name || String(ch.idx)
				openChapters.value.add(id)
			}
		}
		allExpanded.value = true
	}
}

function getChapterCompletedCount(chapter: ChapterItem): number {
	return (chapter.lessons || []).filter((l) => l.is_complete).length
}

function isChapterFullyComplete(chapter: ChapterItem): boolean {
	if (!chapter.lessons || chapter.lessons.length === 0) return false
	return chapter.lessons.every((l) => l.is_complete)
}

function isLessonActive(lesson: LessonItem): boolean {
	if (activeLessonIdentifier.value && lesson.number === activeLessonIdentifier.value) {
		return true
	}
	if (props.currentLesson && (lesson.name === props.currentLesson || lesson.number === props.currentLesson)) {
		return true
	}
	return false
}

function getLessonTypeIcon(icon?: string) {
	switch (icon) {
		case 'icon-youtube':
			return MonitorPlay
		case 'icon-quiz':
			return HelpCircle
		case 'icon-assignment':
			return NotebookPen
		case 'icon-code':
			return SquareCode
		case 'icon-lock':
			return LockKeyhole
		default:
			return FileText
	}
}

function formatDuration(seconds: number): string {
	if (!seconds) return ''
	const mins = Math.floor(seconds / 60)
	const secs = Math.floor(seconds % 60)
	if (mins >= 60) {
		const hrs = Math.floor(mins / 60)
		const remMins = mins % 60
		return `${hrs}h ${remMins}m`
	}
	return `${mins}:${secs < 10 ? '0' : ''}${secs}`
}

function onLessonClick(lesson: LessonItem) {
	if (lesson.locked) return

	// 1. Emit @switchLesson(lessonNumber) per Task 4 brief requirement
	emit('switchLesson', lesson.number)

	// 2. Emit @select-lesson payload for router / parent compatibility
	const parts = lesson.number ? lesson.number.split('-') : ['1', '1']
	emit('select-lesson', {
		chapterNumber: parts[0] || '1',
		lessonNumber: parts[1] || '1',
		name: lesson.name,
	})

	// 3. Navigate if router available and not in inline-select mode
	if (!props.inlineSelect && router && lesson.number) {
		const studentViewQuery = route?.query?.studentView === '1' ? { studentView: 1 } : undefined
		router.push({
			name: 'Lesson',
			params: {
				courseName: props.courseName,
				chapterNumber: parts[0] || '1',
				lessonNumber: parts[1] || '1',
			},
			query: studentViewQuery,
		}).catch(() => {
			// Ignore navigation duplication errors
		})
	}
}
</script>

<style scoped>
.lesson-outline-tab {
	direction: inherit;
}
</style>
