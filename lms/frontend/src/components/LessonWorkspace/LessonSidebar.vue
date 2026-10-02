<template>
	<aside
		class="lesson-sidebar-container flex flex-col h-full min-h-0 bg-surface-base border-s border-outline-gray-2 select-none"
		:class="{ 'w-14 items-center': isCollapsed }"
	>
		<!-- Top Compact Bar: Course Title, Progress & Collapse Action -->
		<div
			class="px-3.5 py-2.5 shrink-0 border-b border-outline-gray-2 bg-surface-gray-1/70 flex items-center justify-between gap-2"
			:class="{ 'flex-col !px-1.5 !py-3': isCollapsed }"
		>
			<!-- Expanded Header Info -->
			<div v-if="!isCollapsed" class="min-w-0 flex-1">
				<div class="flex items-center gap-1.5">
					<span
						class="text-xs font-bold text-ink-gray-9 truncate block"
						:title="courseTitle || courseName"
					>
						{{ courseTitle || courseName }}
					</span>
				</div>
				<div class="flex items-center gap-2 text-[11px] text-ink-gray-5 mt-0.5">
					<span v-if="currentLessonNumber" class="font-mono text-ink-blue-5 font-bold">
						{{ __('درس') }} {{ currentLessonNumber }}
					</span>
					<span v-if="currentLessonNumber && progress !== undefined">•</span>
					<span v-if="progress !== undefined" class="tabular-nums font-medium">
						{{ Math.ceil(progress) }}% {{ __('مكتمل') }}
					</span>
				</div>
			</div>

			<!-- Collapse / Expand Toggle Button -->
			<button
				type="button"
				@click="toggleCollapsed"
				class="p-1.5 rounded-6 border border-outline-gray-2 bg-surface-base hover:bg-surface-gray-2 text-ink-gray-6 hover:text-ink-gray-9 transition-colors cursor-pointer shrink-0"
				:title="isCollapsed ? __('Expand sidebar') : __('Collapse sidebar')"
			>
				<component :is="isCollapsed ? PanelRightOpen : PanelRightClose" class="size-4" />
			</button>
		</div>

		<!-- Tab Navigation Header (Task 4 Brief Requirement: 4 tabs Outline, Notes, Q&A, Resources) -->
		<div
			v-if="!isCollapsed"
			class="px-2 pt-2 pb-1 shrink-0 border-b border-outline-gray-2 bg-surface-base"
			role="tablist"
			aria-label="Lesson workspace tabs"
		>
			<div class="grid grid-cols-4 gap-1 p-0.5 rounded-7 bg-surface-gray-2">
				<button
					v-for="tab in tabDefinitions"
					:key="tab.id"
					type="button"
					role="tab"
					:aria-selected="activeTab === tab.id"
					:tabindex="activeTab === tab.id ? 0 : -1"
					@click="activeTab = tab.id"
					class="relative flex flex-col items-center justify-center py-1.5 px-1 rounded-6 text-xs transition-all duration-150 cursor-pointer group"
					:class="
						activeTab === tab.id
							? 'bg-surface-base text-ink-blue-5 font-bold shadow-xs'
							: 'text-ink-gray-6 hover:text-ink-gray-9 hover:bg-surface-base/50 font-medium'
					"
					:title="`${tab.labelAr} - ${tab.labelEn}`"
				>
					<div class="flex items-center gap-1">
						<component
							:is="tab.icon"
							class="size-3.5 transition-transform group-hover:scale-105"
							:class="activeTab === tab.id ? 'text-ink-blue-5' : 'text-ink-gray-5'"
						/>
						<span class="truncate text-[11px]">{{ tab.labelAr }}</span>
					</div>

					<!-- Active Underline Indicator (UI/UX Pro Max Tokens) -->
					<div
						v-if="activeTab === tab.id"
						class="absolute bottom-0 inset-x-2 h-0.5 bg-surface-blue-5 rounded-full"
					/>
				</button>
			</div>
		</div>

		<!-- Collapsed Mode Vertical Icon Rail -->
		<div
			v-else
			class="flex flex-col items-center gap-2 py-3 flex-1 min-h-0"
		>
			<button
				v-for="tab in tabDefinitions"
				:key="tab.id"
				type="button"
				@click="selectTabFromCollapsed(tab.id)"
				class="p-2.5 rounded-6 transition-all duration-150 cursor-pointer relative group"
				:class="
					activeTab === tab.id
						? 'bg-surface-blue-2 text-ink-blue-5 font-bold shadow-xs'
						: 'text-ink-gray-6 hover:text-ink-gray-9 hover:bg-surface-gray-2'
				"
				:title="`${tab.labelAr} • ${tab.labelEn}`"
			>
				<component :is="tab.icon" class="size-4.5" />
				<div
					v-if="activeTab === tab.id"
					class="absolute start-0 top-1.5 bottom-1.5 w-1 bg-surface-blue-5 rounded-e"
				/>
			</button>
		</div>

		<!-- Tab Content Container -->
		<div
			v-if="!isCollapsed"
			class="flex-1 min-h-0 overflow-hidden bg-surface-base"
		>
			<!-- TAB 1: Course Outline -->
			<LessonOutlineTab
				v-show="activeTab === 'outline'"
				:courseName="courseName"
				:courseTitle="courseTitle"
				:currentLesson="currentLesson"
				:currentLessonNumber="currentLessonNumber"
				:selectedLessonNumber="currentLessonNumber"
				:completedLesson="completedLesson"
				:progress="progress"
				@switchLesson="onSwitchLesson"
				@select-lesson="(payload) => emit('select-lesson', payload)"
			/>

			<!-- TAB 2: Timestamped Smart Notes (Task 3 Component) -->
			<TimestampedNotes
				v-show="activeTab === 'notes'"
				:lesson="currentLesson"
				:course="courseName"
				:videoPlayer="videoPlayer"
				@seek="onSeek"
				@updateNotes="emit('updateNotes')"
			/>

			<!-- TAB 3: Q&A Discussions with Timestamp Capture -->
			<LessonQATab
				v-show="activeTab === 'qa'"
				:courseName="courseName"
				:currentLesson="currentLesson"
				:videoPlayer="videoPlayer"
				:allowDiscussions="allowDiscussions"
				@seek="onSeek"
			/>

			<!-- TAB 4: Downloadable Civil Engineering Resources -->
			<LessonResourcesTab
				v-show="activeTab === 'resources'"
				:courseName="courseName"
				:currentLesson="currentLesson"
				:lessonTitle="currentLessonTitle"
			/>
		</div>
	</aside>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
	FolderDown,
	ListTree,
	MessageCircleQuestion,
	NotebookPen,
	PanelRightClose,
	PanelRightOpen,
} from 'lucide-vue-next'
import LessonOutlineTab from './tabs/LessonOutlineTab.vue'
import TimestampedNotes from './tabs/TimestampedNotes.vue'
import LessonQATab from './tabs/LessonQATab.vue'
import LessonResourcesTab from './tabs/LessonResourcesTab.vue'

type TabKey = 'outline' | 'notes' | 'qa' | 'resources'

interface VideoPlayerAPI {
	getCurrentTime?: () => number
	seekTo?: (seconds: number) => void
	pauseVideo?: () => void
	resumeVideo?: () => void
}

interface Props {
	courseName: string
	courseTitle?: string
	currentLesson: string
	currentLessonNumber?: string
	currentLessonTitle?: string
	videoPlayer?: VideoPlayerAPI | null
	allowDiscussions?: boolean
	progress?: number
	completedLesson?: string | null
	initialTab?: TabKey
	collapsed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	courseTitle: '',
	currentLessonNumber: '',
	currentLessonTitle: '',
	videoPlayer: null,
	allowDiscussions: true,
	progress: 0,
	completedLesson: null,
	initialTab: 'outline',
	collapsed: false,
})

const emit = defineEmits<{
	(e: 'switchLesson', lessonNumber: string): void
	(e: 'select-lesson', payload: { chapterNumber: string; lessonNumber: string; name?: string }): void
	(e: 'seek', seconds: number): void
	(e: 'updateNotes'): void
	(e: 'update:collapsed', val: boolean): void
}>()

const __ = (text: string) => (typeof window !== 'undefined' && (window as any).__ ? (window as any).__(text) : text)

const activeTab = ref<TabKey>(props.initialTab || 'outline')
const isCollapsed = ref<boolean>(props.collapsed)

watch(
	() => props.initialTab,
	(tab) => {
		if (tab) activeTab.value = tab
	}
)

watch(
	() => props.collapsed,
	(val) => {
		isCollapsed.value = val
	}
)

const tabDefinitions = [
	{
		id: 'outline' as TabKey,
		labelAr: __('المحتوى'),
		labelEn: 'Outline',
		icon: ListTree,
	},
	{
		id: 'notes' as TabKey,
		labelAr: __('الملاحظات'),
		labelEn: 'Notes',
		icon: NotebookPen,
	},
	{
		id: 'qa' as TabKey,
		labelAr: __('الأسئلة'),
		labelEn: 'Q&A',
		icon: MessageCircleQuestion,
	},
	{
		id: 'resources' as TabKey,
		labelAr: __('المرفقات'),
		labelEn: 'Resources',
		icon: FolderDown,
	},
]

function toggleCollapsed() {
	isCollapsed.value = !isCollapsed.value
	emit('update:collapsed', isCollapsed.value)
}

function selectTabFromCollapsed(tab: TabKey) {
	activeTab.value = tab
	isCollapsed.value = false
	emit('update:collapsed', false)
}

function onSwitchLesson(lessonNumber: string) {
	emit('switchLesson', lessonNumber)
}

function onSeek(seconds: number) {
	if (props.videoPlayer && typeof props.videoPlayer.seekTo === 'function') {
		props.videoPlayer.seekTo(seconds)
	}
	emit('seek', seconds)
}
</script>

<style scoped>
.lesson-sidebar-container {
	direction: inherit;
}
</style>
