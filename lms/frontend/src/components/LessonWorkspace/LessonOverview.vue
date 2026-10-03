<template>
	<div class="lesson-overview-container max-w-4xl mx-auto py-2">
		<!-- Course & Chapter Context Breadcrumb Badge -->
		<div
			v-if="!zenModeEnabled && (lesson?.chapter_title || lesson?.course_title)"
			class="flex items-center gap-2 text-xs font-medium text-ink-gray-5 mb-3 flex-wrap"
		>
			<span
				v-if="lesson.chapter_title"
				class="inline-flex items-center gap-1 font-mono text-ink-blue-5 font-semibold bg-surface-blue-2 px-2.5 py-0.5 rounded-full border border-outline-blue-2/30"
			>
				{{ lesson.chapter_title }}
			</span>
			<span v-if="lesson.chapter_title && lesson.course_title" class="text-ink-gray-4">•</span>
			<span v-if="lesson.course_title" class="truncate text-ink-gray-6 font-medium">
				{{ lesson.course_title }}
			</span>
		</div>

		<!-- Lesson Title -->
		<div class="flex flex-col gap-2">
			<h1 class="text-2xl sm:text-3xl font-extrabold text-ink-gray-9 tracking-tight leading-snug">
				{{ lesson?.title }}
			</h1>

			<!-- Zen Mode Completion Indicator -->
			<div
				v-if="zenModeEnabled"
				class="relative flex items-center gap-x-2 text-xs text-ink-gray-6 group w-fit mt-1"
			>
				<span>{{ lesson?.chapter_title }} — {{ lesson?.course_title }}</span>
				<span class="lucide-info size-3 text-ink-blue-5" />
				<div
					v-if="lesson?.membership?.progress !== undefined"
					class="hidden group-hover:block [@media(hover:none)]:block [@media(hover:none)]:static [@media(hover:none)]:mt-0 rounded-4 bg-surface-gray-10 px-2 py-1 text-xs text-ink-base shadow-xl absolute start-0 top-full mt-1.5 z-20"
				>
					{{ Math.ceil(lesson.membership.progress) }}% {{ __('Completed') }}
				</div>
			</div>
		</div>

		<!-- Instructors Avatar & Badges -->
		<div
			v-if="!zenModeEnabled && lesson?.instructors && lesson.instructors.length > 0"
			class="flex items-center gap-3 mt-4 pt-3 border-t border-outline-gray-2/60 flex-wrap"
		>
			<div class="flex items-center gap-2">
				<span
					class="h-7 me-1 inline-flex items-center"
					:class="{
						'avatar-group overlap': lesson.instructors.length > 1,
					}"
				>
					<UserAvatar
						v-for="instructor in lesson.instructors"
						:key="typeof instructor === 'object' ? instructor.name : instructor"
						:user="instructor"
						class="size-7 ring-2 ring-surface-base"
					/>
				</span>
				<CourseInstructors :instructors="lesson.instructors" />
			</div>

			<!-- Civil Engineering Verified Tag -->
			<div class="ms-auto flex items-center gap-1.5 text-[11px] font-medium text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">
				<span class="size-1.5 rounded-full bg-emerald-500 animate-pulse" />
				<span>{{ __('Certified Engineering Content') }} • {{ __('SBC Compliant') }}</span>
			</div>
		</div>

		<!-- Civil Engineering Design Equations & Formulas Showcase (LaTeX Equations) -->
		<div
			class="engineering-formulas-card my-6 rounded-xl border border-sky-200 bg-sky-50/70 dark:border-sky-900/60 dark:bg-sky-950/25 p-4 sm:p-5 transition-all shadow-xs"
		>
			<div class="flex items-center justify-between gap-2 mb-3 pb-2.5 border-b border-sky-200/70 dark:border-sky-900/40">
				<div class="flex items-center gap-2.5">
					<span class="p-1.5 rounded-lg bg-sky-500/10 text-sky-600 dark:text-sky-400">
						<Binary class="size-4" />
					</span>
					<div>
						<h3 class="text-xs sm:text-sm font-bold text-sky-950 dark:text-sky-200">
							{{ __('Design Equations (SBC 304 / ACI 318)') }}
						</h3>
						<p class="text-[11px] text-sky-800/80 dark:text-sky-400/80 mt-0.5">
							{{ __('Load combination equations and ultimate flexural strength requirements') }}
						</p>
					</div>
				</div>
				<span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-sky-100 dark:bg-sky-900/60 text-sky-700 dark:text-sky-300 font-semibold shrink-0">
					<span>{{ __('LaTeX Math') }}</span>
				</span>
			</div>

			<!-- Formatted LaTeX Equations Grid (UI/UX Pro Max Engineering Typography) -->
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
				<!-- Equation 1: U = 1.2D + 1.6L (Required verbatim) -->
				<div class="p-3.5 rounded-xl bg-surface-base border border-sky-200/80 dark:border-sky-900/60 shadow-xs flex flex-col justify-between group hover:border-sky-400 dark:hover:border-sky-700 transition-all">
					<div class="flex items-center justify-between gap-1 mb-2">
						<span class="text-[11px] text-ink-gray-6 font-semibold">
							{{ __('Ultimate Load Combination:') }}
						</span>
						<button
							type="button"
							@click="copyFormula('$U = 1.2D + 1.6L$')"
							class="text-[10px] text-sky-600 hover:text-sky-800 dark:text-sky-400 font-medium opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer px-1.5 py-0.5 rounded bg-sky-50 dark:bg-sky-950/60"
							:title="__('Copy equation')"
						>
							{{ __('Copy') }}
						</button>
					</div>
					<div
						class="engineering-formula py-2.5 px-3 bg-surface-gray-2/70 dark:bg-slate-900/80 rounded-lg text-center border border-outline-blue-2/30 select-all dir-ltr"
						dir="ltr"
						:title="'$U = 1.2D + 1.6L$'"
					>
						<span class="font-serif italic font-bold text-lg text-ink-blue-5">U</span>
						<span class="mx-1.5 text-ink-gray-5 font-semibold">=</span>
						<span class="font-bold text-ink-gray-9 text-base">1.2</span><span class="font-serif italic font-bold text-lg text-ink-blue-5">D</span>
						<span class="mx-1.5 text-ink-gray-5 font-semibold">+</span>
						<span class="font-bold text-ink-gray-9 text-base">1.6</span><span class="font-serif italic font-bold text-lg text-ink-blue-5">L</span>
						<span class="sr-only">$U = 1.2D + 1.6L$</span>
					</div>
					<span class="text-[10px] text-ink-gray-5 mt-2 text-center font-mono font-medium">
						<span>{{ __('SBC 304 - Sec. 5.3.1 (Load Combo)') }}</span>
					</span>
				</div>

				<!-- Equation 2: Nominal Flexural Strength: phi Mn >= Mu -->
				<div class="p-3.5 rounded-xl bg-surface-base border border-sky-200/80 dark:border-sky-900/60 shadow-xs flex flex-col justify-between group hover:border-sky-400 dark:hover:border-sky-700 transition-all">
					<div class="flex items-center justify-between gap-1 mb-2">
						<span class="text-[11px] text-ink-gray-6 font-semibold">
							{{ __('Flexural Design Strength:') }}
						</span>
						<button
							type="button"
							@click="copyFormula('$\\phi M_n \\ge M_u$')"
							class="text-[10px] text-sky-600 hover:text-sky-800 dark:text-sky-400 font-medium opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer px-1.5 py-0.5 rounded bg-sky-50 dark:bg-sky-950/60"
							:title="__('Copy equation')"
						>
							{{ __('Copy') }}
						</button>
					</div>
					<div
						class="engineering-formula py-2.5 px-3 bg-surface-gray-2/70 dark:bg-slate-900/80 rounded-lg text-center border border-outline-blue-2/30 select-all dir-ltr"
						dir="ltr"
						:title="'$\\phi M_n \\ge M_u$'"
					>
						<span class="font-serif font-bold text-xl text-ink-blue-5">ϕ</span>
						<span class="font-serif italic font-bold text-lg text-ink-blue-5">M</span><sub class="text-xs font-bold text-ink-blue-5">n</sub>
						<span class="mx-2 text-base text-ink-gray-6 font-bold">≥</span>
						<span class="font-serif italic font-bold text-lg text-ink-blue-5">M</span><sub class="text-xs font-bold text-ink-blue-5">u</sub>
						<span class="sr-only">$\phi M_n \ge M_u$</span>
					</div>
					<span class="text-[10px] text-ink-gray-5 mt-2 text-center font-mono font-medium">
						ϕ = 0.90 ({{ __('Tension-controlled') }})
					</span>
				</div>

				<!-- Equation 3: Reinforcement Ratio: rho = As / (b * d) -->
				<div class="p-3.5 rounded-xl bg-surface-base border border-sky-200/80 dark:border-sky-900/60 shadow-xs flex flex-col justify-between group hover:border-sky-400 dark:hover:border-sky-700 transition-all">
					<div class="flex items-center justify-between gap-1 mb-2">
						<span class="text-[11px] text-ink-gray-6 font-semibold">
							{{ __('Reinforcement Ratio:') }}
						</span>
						<button
							type="button"
							@click="copyFormula('$\\rho = \\frac{A_s}{b \\cdot d}$')"
							class="text-[10px] text-sky-600 hover:text-sky-800 dark:text-sky-400 font-medium opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer px-1.5 py-0.5 rounded bg-sky-50 dark:bg-sky-950/60"
							:title="__('Copy equation')"
						>
							{{ __('Copy') }}
						</button>
					</div>
					<div
						class="engineering-formula py-2 px-3 bg-surface-gray-2/70 dark:bg-slate-900/80 rounded-lg flex items-center justify-center border border-outline-blue-2/30 select-all dir-ltr gap-1.5"
						dir="ltr"
						:title="'$\\rho = \\frac{A_s}{b \\cdot d}$'"
					>
						<span class="font-serif font-bold text-xl text-ink-blue-5">ρ</span>
						<span class="mx-1 text-ink-gray-5 font-semibold">=</span>
						<div class="inline-flex flex-col items-center justify-center text-xs leading-none">
							<span class="font-serif italic font-bold text-ink-blue-5 pb-0.5 border-b border-ink-gray-4 dark:border-ink-gray-6 px-1.5">
								A<sub class="text-[10px]">s</sub>
							</span>
							<span class="font-serif italic font-medium text-ink-gray-8 dark:text-ink-gray-2 pt-0.5 px-1.5">
								b · d
							</span>
						</div>
						<span class="sr-only">$\rho = \frac{A_s}{b \cdot d}$</span>
					</div>
					<span class="text-[10px] text-ink-gray-5 mt-2 text-center font-mono font-medium">
						ρ<sub>min</sub> ≤ ρ ≤ ρ<sub>max</sub>
					</span>
				</div>
			</div>
		</div>

		<!-- Instructor Notes Section -->
		<div
			v-if="hasInstructorNotes && allowInstructorContent"
			class="bg-surface-gray-2 p-4 sm:p-5 rounded-xl border border-outline-gray-2 mt-6 shadow-xs"
		>
			<div class="flex items-center gap-2 mb-2.5 text-ink-gray-8">
				<NotebookPen class="size-4 text-ink-blue-5" />
				<h2 class="text-sm font-bold text-ink-gray-9">
					{{ __('Instructor Notes') }}
				</h2>
			</div>
			<div
				id="instructor-content"
				class="ProseMirror prose prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-outline-gray-2 prose-th:border-outline-gray-2 prose-td:relative prose-th:relative prose-th:bg-surface-gray-2 prose-sm max-w-none !whitespace-normal"
			></div>
		</div>
		<div
			v-else-if="lesson?.instructor_notes"
			class="ProseMirror prose prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-outline-gray-2 prose-th:border-outline-gray-2 prose-td:relative prose-th:relative prose-th:bg-surface-gray-2 prose-sm max-w-none !whitespace-normal mt-6 bg-surface-gray-2 p-4 sm:p-5 rounded-xl border border-outline-gray-2"
		>
			<div class="flex items-center gap-2 mb-2 text-ink-gray-8 not-prose">
				<NotebookPen class="size-4 text-ink-blue-5" />
				<h2 class="text-sm font-bold text-ink-gray-9">
					{{ __('Instructor Notes') }}
				</h2>
			</div>
			<LessonContent
				:key="lesson.name"
				:content="lesson.instructor_notes"
			/>
		</div>

		<!-- Content Unreadable Notice -->
		<div
			v-if="contentUnreadable"
			class="flex items-center gap-3 rounded-xl bg-surface-amber-2 p-4 mt-6 border border-outline-amber-2"
		>
			<div class="grid size-8 shrink-0 place-items-center text-ink-amber-5">
				<span class="lucide-circle-alert size-5" aria-hidden="true" />
			</div>
			<div class="flex min-w-0 flex-1 flex-col">
				<span class="text-sm font-semibold text-ink-gray-8">
					{{ __('This lesson could not be displayed') }}
				</span>
				<span class="text-xs text-ink-gray-6 mt-0.5">
					{{
						__(
							'Its content is stored in a form we cannot read. Reload the page, and tell your instructor if it keeps happening.'
						)
					}}
				</span>
			</div>
		</div>

		<!-- Formatted Lecture Content (EditorJS or Markdown/LessonContent) -->
		<div
			v-else-if="lesson?.content"
			@mouseup="emit('toggleInlineMenu')"
			class="ProseMirror prose prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-outline-gray-2 prose-th:border-outline-gray-2 prose-td:relative prose-th:relative prose-th:bg-surface-gray-2 prose-sm max-w-none !whitespace-normal mt-6 leading-relaxed"
		>
			<div id="editor"></div>
		</div>
		<div
			v-else-if="sanitizedBody"
			class="ProseMirror prose prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-outline-gray-2 prose-th:border-outline-gray-2 prose-td:relative prose-th:relative prose-th:bg-surface-gray-2 prose-sm max-w-none !whitespace-normal mt-6 leading-relaxed"
		>
			<LessonContent
				:key="lesson.name"
				:content="sanitizedBody"
				:youtube="hasVideo ? undefined : lesson.youtube"
				:quizId="lesson.quiz_id"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { toast } from 'frappe-ui'
import { Binary, NotebookPen } from 'lucide-vue-next'
import UserAvatar from '@/components/UserAvatar.vue'
import CourseInstructors from '@/components/CourseInstructors.vue'
import LessonContent from '@/components/LessonContent.vue'

interface Instructor {
	name?: string
	title?: string
	avatar?: string
	full_name?: string
	[key: string]: any
}

interface LessonData {
	name?: string
	title?: string
	course_title?: string
	chapter_title?: string
	instructors?: (Instructor | string)[]
	instructor_notes?: string | null
	instructor_content?: string | null
	content?: string | null
	body?: string | null
	youtube?: string | null
	quiz_id?: string | null
	membership?: { progress?: number } | null
	[key: string]: any
}

interface Props {
	lesson: LessonData | null
	zenModeEnabled?: boolean
	contentUnreadable?: boolean
	allowInstructorContent?: boolean
	hasInstructorNotes?: boolean
	hasVideo?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	zenModeEnabled: false,
	contentUnreadable: false,
	allowInstructorContent: false,
	hasInstructorNotes: false,
	hasVideo: false,
})

const emit = defineEmits<{
	(e: 'toggleInlineMenu'): void
}>()

const __ = (text: string) =>
	typeof window !== 'undefined' && (window as any).__ ? (window as any).__(text) : text

// If a top VideoBlock is active in the workspace, strip the {{ Video(...) }}
// macro from markdown body to avoid mounting a second duplicate video player.
const sanitizedBody = computed(() => {
	if (!props.lesson?.body) return ''
	if (props.hasVideo) {
		return props.lesson.body
			.replace(/\{\{\s*Video\([^)]+\)\s*\}\}\n?/g, '')
			.trim()
	}
	return props.lesson.body
})

const copyFormula = (formula: string) => {
	if (navigator.clipboard) {
		navigator.clipboard.writeText(formula).then(() => {
			toast.success(__('Equation copied to clipboard'))
		}).catch(() => {})
	}
}
</script>

<style scoped>
.dir-ltr {
	direction: ltr;
}

.avatar-group {
	display: inline-flex;
	align-items: center;
}

.avatar-group .avatar {
	transition: margin 0.1s ease-in-out;
}
</style>
