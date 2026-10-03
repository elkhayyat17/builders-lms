<template>
	<div class="timestamped-notes-container flex flex-col h-full">
		<!-- Search, Filter & Actions Bar -->
		<div class="flex items-center justify-between gap-2 mb-3 shrink-0">
			<!-- Search Input -->
			<div class="relative flex-1 min-w-0">
				<Search class="absolute start-3 top-1/2 -translate-y-1/2 size-4 text-ink-gray-4 pointer-events-none" />
				<input
					type="text"
					v-model="searchQuery"
					:placeholder="__('Search notes...')"
					class="w-full ps-9 pe-8 py-1.5 rounded-6 border border-outline-gray-2 bg-surface-base text-sm text-ink-gray-9 placeholder:text-ink-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-4 transition-all"
				/>
				<button
					v-if="searchQuery"
					type="button"
					@click="searchQuery = ''"
					class="absolute end-2.5 top-1/2 -translate-y-1/2 p-0.5 rounded-full text-ink-gray-4 hover:text-ink-gray-7"
					:title="__('Clear search')"
				>
					<X class="size-3.5" />
				</button>
			</div>

			<!-- Pinned Filter Toggle -->
			<button
				type="button"
				@click="filterPinnedOnly = !filterPinnedOnly"
				class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-6 border text-xs font-medium transition-colors cursor-pointer shrink-0"
				:class="
					filterPinnedOnly
						? 'border-outline-amber-2 bg-surface-amber-2 text-ink-amber-5'
						: 'border-outline-gray-2 bg-surface-base text-ink-gray-7 hover:bg-surface-gray-2'
				"
				:title="filterPinnedOnly ? __('Show all notes') : __('Show pinned notes only')"
			>
				<Pin class="size-3.5" :class="{ 'fill-current text-ink-amber-5': filterPinnedOnly }" />
				<span class="hidden sm:inline">{{ __('Pinned') }}</span>
			</button>

			<!-- Export Printable Document Button -->
			<button
				type="button"
				@click="exportNotes"
				class="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-6 border border-outline-gray-2 bg-surface-base hover:bg-surface-gray-2 text-ink-gray-7 text-xs font-medium transition-colors cursor-pointer shrink-0"
				:title="__('Export formatted printable notes')"
			>
				<Printer class="size-3.5" />
				<span class="hidden sm:inline">{{ __('Export') }}</span>
			</button>
		</div>

		<!-- Quick Note Creation Trigger (Udemy Style) -->
		<div v-if="!isCreating" class="mb-3 shrink-0">
			<button
				type="button"
				@click="startCreateNote"
				class="w-full flex items-center justify-between px-3.5 py-2.5 rounded-7 border border-dashed border-outline-gray-2 hover:border-outline-blue-2 bg-surface-gray-2 hover:bg-surface-blue-2 text-ink-gray-7 hover:text-ink-blue-5 transition-all group cursor-pointer"
			>
				<div class="flex items-center gap-2.5">
					<div class="p-1 rounded-5 bg-surface-blue-2 text-ink-blue-5 group-hover:scale-105 transition-transform">
						<Plus class="size-4" />
					</div>
					<span class="text-sm font-medium">
						{{
							videoPlayer
								? `${__('Add note at')} ${formatSeconds(currentVideoTime)}`
								: __('Add a note')
						}}
					</span>
				</div>
				<kbd
					class="px-2 py-0.5 text-xs font-mono font-semibold text-ink-gray-5 bg-surface-base border border-outline-gray-2 rounded-5"
					:title="__('Keyboard shortcut')"
				>
					N
				</kbd>
			</button>
		</div>

		<!-- Active Note Creation Card -->
		<div
			v-if="isCreating"
			class="mb-3 shrink-0 rounded-7 border-2 border-outline-blue-2 bg-surface-base p-4 shadow-sm transition-all"
		>
			<div class="flex items-center justify-between gap-2 mb-3">
				<div class="flex items-center gap-2">
					<span
						class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-surface-blue-2 text-ink-blue-5 border border-outline-blue-2"
					>
						<Clock class="size-3" />
						<span>{{ formattedCapturedTime }}</span>
					</span>
					<span
						v-if="videoPlayer"
						class="inline-flex items-center gap-1 text-xs font-medium text-ink-gray-5"
					>
						<Pause class="size-2.5" />
						<span>{{ __('Video paused') }}</span>
					</span>
				</div>
				<button
					type="button"
					@click="cancelCreateNote"
					class="p-1 rounded-5 text-ink-gray-4 hover:text-ink-gray-7 transition-colors cursor-pointer"
					:title="__('Cancel')"
				>
					<X class="size-4" />
				</button>
			</div>

			<textarea
				ref="newNoteTextareaRef"
				v-model="newNoteText"
				rows="3"
				class="w-full rounded-6 border border-outline-gray-2 bg-surface-gray-2 p-3 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-outline-blue-2 focus:bg-surface-base transition-all placeholder:text-ink-gray-4"
				:placeholder="__('Write your note here... (Press Ctrl+Enter to save)')"
				@keydown.ctrl.enter="saveNewNote"
				@keydown.meta.enter="saveNewNote"
			/>

			<div class="mt-3 flex items-center justify-between flex-wrap gap-2 pt-1">
				<div class="flex items-center gap-3">
					<!-- Pin Toggle via Frappe-UI Checkbox -->
					<Checkbox
						v-model="isPinned"
						:label="__('Pin note')"
					/>

					<!-- Color Selector -->
					<div class="flex items-center gap-1.5">
						<button
							v-for="color in colorPalette"
							:key="color.name"
							type="button"
							@click="selectedColor = color.name"
							class="size-4 rounded-full transition-transform cursor-pointer"
							:class="[
								color.dot,
								selectedColor === color.name
									? 'ring-2 ring-outline-gray-4 scale-110'
									: 'opacity-60 hover:opacity-100',
							]"
							:title="color.name"
						/>
					</div>
				</div>

				<div class="flex items-center gap-2">
					<Button variant="subtle" size="sm" @click="cancelCreateNote">
						{{ __('Cancel') }}
					</Button>
					<Button
						variant="solid"
						size="sm"
						theme="primary"
						:loading="isSubmitting"
						:disabled="!newNoteText.trim()"
						@click="saveNewNote"
					>
						{{ __('Save note') }}
					</Button>
				</div>
			</div>
		</div>

		<!-- Notes List Section -->
		<div class="notes-scroll-area flex-1 overflow-y-auto space-y-3 pe-1">
			<!-- Loading State -->
			<div
				v-if="notesResource.loading && (!notesResource.data || notesResource.data.length === 0)"
				class="flex flex-col items-center justify-center py-10 space-y-2 text-ink-gray-4"
			>
				<span class="lucide-loader-2 size-6 animate-spin text-ink-blue-5" />
				<span class="text-xs">{{ __('Loading notes...') }}</span>
			</div>

			<!-- Empty State: Filter Returned No Match -->
			<div
				v-else-if="filteredNotes.length === 0 && (searchQuery || filterPinnedOnly)"
				class="rounded-7 border border-dashed border-outline-gray-2 p-8 text-center"
			>
				<Search class="mx-auto size-7 text-ink-gray-4 mb-2" />
				<p class="text-sm font-medium text-ink-gray-7">
					{{ __('No notes match your filter') }}
				</p>
				<p class="text-xs text-ink-gray-5 mt-1">
					{{ __('Try clearing your search query or pin filter.') }}
				</p>
				<button
					type="button"
					@click="
						searchQuery = '';
						filterPinnedOnly = false;
					"
					class="mt-3 text-xs font-semibold text-ink-blue-5 hover:underline cursor-pointer"
				>
					{{ __('Reset filters') }}
				</button>
			</div>

			<!-- Empty State: Zero Notes Recorded -->
			<div
				v-else-if="filteredNotes.length === 0"
				class="rounded-7 border border-dashed border-outline-gray-2 p-8 text-center"
			>
				<div class="mx-auto size-12 rounded-full bg-surface-blue-2 flex items-center justify-center text-ink-blue-5 mb-3">
					<FileText class="size-6" />
				</div>
				<h3 class="text-sm font-semibold text-ink-gray-9">
					{{ __('No notes in this lesson yet') }}
				</h3>
				<p class="text-xs text-ink-gray-5 mt-1 max-w-xs mx-auto leading-relaxed">
					{{
						__(
							'Capture key formulas, diagrams, or questions synchronized with video timestamps. Press "N" anytime while watching to pause and take a note.'
						)
					}}
				</p>
				<Button
					variant="solid"
					size="sm"
					theme="primary"
					class="mt-4"
					@click="startCreateNote"
				>
					<template #prefix>
						<Plus class="size-3.5" />
					</template>
					{{ __('Create first note') }}
				</Button>
			</div>

			<!-- Notes Cards (Udemy Style) -->
			<div
				v-for="note in filteredNotes"
				:key="note.name"
				class="group relative rounded-7 border border-outline-gray-2 bg-surface-base p-4 transition-all duration-200 hover:shadow-sm hover:border-outline-gray-3"
				:class="{
					'ring-1 ring-outline-amber-2 bg-surface-amber-1': note.is_pinned,
				}"
			>
				<!-- Color Accent Strip -->
				<div
					class="absolute start-0 top-3 bottom-3 w-1 rounded-full"
					:class="getColorAccentClass(note.color)"
				/>

				<!-- Card Header -->
				<div class="flex items-center justify-between gap-2 mb-2">
					<div class="flex items-center gap-2 flex-wrap">
						<!-- Interactive Timestamp Pill (Jump to second) -->
						<button
							type="button"
							v-if="note.video_timestamp !== undefined && note.video_timestamp !== null"
							@click="onSeekClick(note.video_timestamp)"
							class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-surface-blue-2 text-ink-blue-5 border border-outline-blue-2 hover:bg-surface-blue-3 transition-colors cursor-pointer group/pill"
							:title="__('Jump video to this timestamp')"
						>
							<Play class="size-3 fill-current group-hover/pill:scale-110 transition-transform" />
							<span>{{ note.formatted_time || formatSeconds(note.video_timestamp) }}</span>
						</button>

						<!-- Pinned Badge -->
						<span
							v-if="note.is_pinned"
							class="inline-flex items-center gap-1 px-2 py-0.5 rounded-5 text-xs font-semibold bg-surface-amber-2 text-ink-amber-5 border border-outline-amber-2"
						>
							<Pin class="size-3 fill-current" />
							<span>{{ __('Pinned') }}</span>
						</span>
					</div>

					<!-- Note Actions -->
					<div class="flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity">
						<button
							type="button"
							@click="togglePin(note)"
							class="p-1.5 rounded-5 text-ink-gray-4 hover:text-ink-amber-5 hover:bg-surface-gray-2 transition-colors cursor-pointer"
							:title="note.is_pinned ? __('Unpin note') : __('Pin note to top')"
						>
							<Pin class="size-3.5" :class="{ 'fill-current text-ink-amber-5': note.is_pinned }" />
						</button>
						<button
							type="button"
							@click="startEditNote(note)"
							class="p-1.5 rounded-5 text-ink-gray-4 hover:text-ink-blue-5 hover:bg-surface-gray-2 transition-colors cursor-pointer"
							:title="__('Edit note')"
						>
							<Pencil class="size-3.5" />
						</button>
						<button
							type="button"
							@click="promptDeleteNote(note)"
							class="p-1.5 rounded-5 text-ink-gray-4 hover:text-ink-red-5 hover:bg-surface-gray-2 transition-colors cursor-pointer"
							:title="__('Delete note')"
						>
							<Trash2 class="size-3.5" />
						</button>
					</div>
				</div>

				<!-- Note Text Body (View Mode) -->
				<div
					v-if="editingNoteName !== note.name"
					class="text-sm text-ink-gray-7 whitespace-pre-wrap leading-relaxed break-words"
				>
					{{ note.note }}
				</div>

				<!-- Inline Editor (Edit Mode) -->
				<div v-else class="mt-2 space-y-3">
					<textarea
						v-model="editingNoteText"
						rows="3"
						class="w-full rounded-6 border border-outline-gray-2 bg-surface-gray-2 p-2.5 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-outline-blue-2 transition-all"
						:placeholder="__('Write your note...')"
						@keydown.ctrl.enter="saveEditNote(note)"
						@keydown.meta.enter="saveEditNote(note)"
					/>
					<div class="flex items-center justify-between flex-wrap gap-2">
						<div class="flex items-center gap-2">
							<Checkbox
								v-model="editingIsPinned"
								:label="__('Pin to top')"
							/>
							<div class="flex items-center gap-1 ms-2">
								<button
									v-for="color in colorPalette"
									:key="color.name"
									type="button"
									@click="editingColor = color.name"
									class="size-4 rounded-full transition-transform cursor-pointer"
									:class="[
										color.dot,
										editingColor === color.name
											? 'ring-2 ring-outline-gray-4 scale-110'
											: 'opacity-70 hover:opacity-100',
									]"
									:title="color.name"
								/>
							</div>
						</div>
						<div class="flex items-center gap-2">
							<Button variant="subtle" size="sm" @click="cancelEditNote">
								{{ __('Cancel') }}
							</Button>
							<Button
								variant="solid"
								size="sm"
								theme="primary"
								:loading="isSubmitting"
								@click="saveEditNote(note)"
							>
								{{ __('Save') }}
							</Button>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Delete Confirmation Dialog -->
		<Dialog
			v-model:open="showDeleteDialog"
			:title="__('Delete Note')"
			:message="__('Are you sure you want to delete this note? This action cannot be undone.')"
			size="sm"
			:actions="deleteDialogActions"
		/>
	</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick, inject } from 'vue'
import { Button, Checkbox, Dialog, call, createListResource, toast } from 'frappe-ui'
import {
	Play,
	Pause,
	Plus,
	Search,
	Trash2,
	Pencil,
	Pin,
	Printer,
	Clock,
	X,
	FileText,
} from 'lucide-vue-next'

interface VideoPlayerAPI {
	getCurrentTime?: () => number
	seekTo?: (seconds: number) => void
	pauseVideo?: () => void
	resumeVideo?: () => void
	playing?: any
}

interface Props {
	lesson: string
	course?: string
	videoPlayer?: VideoPlayerAPI | null
}

const props = withDefaults(defineProps<Props>(), {
	course: '',
	videoPlayer: null,
})

const emit = defineEmits<{
	(e: 'updateNotes'): void
	(e: 'seek', seconds: number): void
}>()

interface LessonNoteItem {
	name: string
	lesson?: string
	course?: string
	member?: string
	color?: string
	note?: string | null
	video_timestamp?: number
	formatted_time?: string
	is_pinned?: number | boolean
	creation?: string
	modified?: string
}

const user = inject<any>('$user')
const __ = (text: string) => (typeof window !== 'undefined' && window.__ ? window.__(text) : text)

// Helper: converts seconds to "mm:ss" or "hh:mm:ss" (e.g. 125 -> "02:05")
const formatSeconds = (sec: number): string => {
	if (isNaN(sec) || sec < 0) return '00:00'
	const totalSeconds = Math.floor(sec)
	const hours = Math.floor(totalSeconds / 3600)
	const minutes = Math.floor((totalSeconds % 3600) / 60)
	const seconds = totalSeconds % 60
	const pad = (n: number) => String(n).padStart(2, '0')
	if (hours > 0) {
		return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`
	}
	return `${pad(minutes)}:${pad(seconds)}`
}

// Color palettes for notes using semantic tokens
const colorPalette = [
	{ name: 'Yellow', dot: 'bg-surface-amber-5' },
	{ name: 'Blue', dot: 'bg-surface-blue-5' },
	{ name: 'Green', dot: 'bg-surface-green-5' },
	{ name: 'Purple', dot: 'bg-surface-violet-5' },
	{ name: 'Red', dot: 'bg-surface-red-5' },
]

const getColorAccentClass = (colorName?: string) => {
	switch (colorName) {
		case 'Blue':
			return 'bg-surface-blue-5'
		case 'Green':
			return 'bg-surface-green-5'
		case 'Purple':
			return 'bg-surface-violet-5'
		case 'Red':
			return 'bg-surface-red-5'
		case 'Yellow':
		default:
			return 'bg-surface-amber-5'
	}
}

// Reactive component state
const searchQuery = ref('')
const filterPinnedOnly = ref(false)
const isCreating = ref(false)
const isSubmitting = ref(false)
const newNoteText = ref('')
const selectedColor = ref('Yellow')
const isPinned = ref(false)
const capturedTime = ref(0)
const formattedCapturedTime = ref('00:00')
const newNoteTextareaRef = ref<HTMLTextAreaElement | null>(null)

// Editing state
const editingNoteName = ref<string | null>(null)
const editingNoteText = ref('')
const editingIsPinned = ref(false)
const editingColor = ref('Yellow')

// Deletion dialog state
const noteToDelete = ref<LessonNoteItem | null>(null)
const showDeleteDialog = ref(false)

// Video tracking state
const currentVideoTime = ref(0)
let wasPlayingBeforeOpen = false
let timePollTimer: ReturnType<typeof setInterval> | null = null

// Frappe list resource for LMS Lesson Note
const notesResource = createListResource<LessonNoteItem>({
	doctype: 'LMS Lesson Note',
	filters: {
		lesson: props.lesson,
		member: user?.data?.name,
	},
	fields: [
		'name',
		'lesson',
		'course',
		'member',
		'color',
		'note',
		'video_timestamp',
		'formatted_time',
		'is_pinned',
		'creation',
	],
	orderBy: 'video_timestamp asc, creation asc',
	auto: true,
})

// Watch lesson change and update notes resource filters
watch(
	() => props.lesson,
	(newLesson) => {
		if (newLesson && user?.data?.name) {
			notesResource.update({
				filters: {
					lesson: newLesson,
					member: user.data.name,
				},
			})
			notesResource.reload()
		}
	}
)

watch(
	() => user?.data?.name,
	(userName) => {
		if (userName && props.lesson) {
			notesResource.update({
				filters: {
					lesson: props.lesson,
					member: userName,
				},
			})
			notesResource.reload()
		}
	}
)

// Computed all notes with pinned-first sorting
const allNotes = computed<LessonNoteItem[]>(() => {
	if (!notesResource.data) return []
	return [...notesResource.data].sort((a, b) => {
		const pinA = a.is_pinned ? 1 : 0
		const pinB = b.is_pinned ? 1 : 0
		if (pinA !== pinB) return pinB - pinA
		const timeA = a.video_timestamp ?? 0
		const timeB = b.video_timestamp ?? 0
		if (timeA !== timeB) return timeA - timeB
		return (a.creation || '').localeCompare(b.creation || '')
	})
})

// Computed filtered notes (search and pinned filters)
const filteredNotes = computed<LessonNoteItem[]>(() => {
	let list = allNotes.value
	if (filterPinnedOnly.value) {
		list = list.filter((n) => Boolean(n.is_pinned))
	}
	if (searchQuery.value.trim()) {
		const q = searchQuery.value.toLowerCase().trim()
		list = list.filter((n) => {
			const text = (n.note || '').toLowerCase()
			const time = (n.formatted_time || formatSeconds(n.video_timestamp || 0)).toLowerCase()
			return text.includes(q) || time.includes(q)
		})
	}
	return list
})

// Seeking handler
const onSeekClick = (timestamp: number) => {
	if (props.videoPlayer?.seekTo) {
		props.videoPlayer.seekTo(timestamp)
		emit('seek', timestamp)
	}
}

// Start creating a note
const startCreateNote = () => {
	if (isCreating.value) return

	if (props.videoPlayer) {
		const isPlaying =
			typeof props.videoPlayer.playing === 'boolean'
				? props.videoPlayer.playing
				: Boolean(props.videoPlayer.playing?.value)
		wasPlayingBeforeOpen = isPlaying
		props.videoPlayer.pauseVideo?.()
	}

	const currentTime = props.videoPlayer?.getCurrentTime?.() ?? currentVideoTime.value ?? 0
	capturedTime.value = Math.max(0, currentTime)
	formattedCapturedTime.value = formatSeconds(capturedTime.value)
	isCreating.value = true
	newNoteText.value = ''
	selectedColor.value = 'Yellow'
	isPinned.value = false

	nextTick(() => {
		newNoteTextareaRef.value?.focus()
	})
}

// Cancel note creation
const cancelCreateNote = () => {
	isCreating.value = false
	newNoteText.value = ''
	if (wasPlayingBeforeOpen && props.videoPlayer?.resumeVideo) {
		props.videoPlayer.resumeVideo()
	}
}

// Save new note via POST to frappe.client.insert
const saveNewNote = async () => {
	if (!newNoteText.value.trim() || isSubmitting.value) return
	isSubmitting.value = true

	try {
		const timeSec = capturedTime.value
		const timeFormatted = formattedCapturedTime.value || formatSeconds(timeSec)

		await call('frappe.client.insert', {
			doc: {
				doctype: 'LMS Lesson Note',
				lesson: props.lesson,
				course: props.course || undefined,
				member: user?.data?.name,
				color: selectedColor.value || 'Yellow',
				note: newNoteText.value.trim(),
				video_timestamp: timeSec,
				formatted_time: timeFormatted,
				is_pinned: isPinned.value ? 1 : 0,
			},
		})

		toast.success(__('Note saved successfully'))
		isCreating.value = false
		newNoteText.value = ''
		notesResource.reload()
		emit('updateNotes')

		if (wasPlayingBeforeOpen && props.videoPlayer?.resumeVideo) {
			props.videoPlayer.resumeVideo()
		}
	} catch (err: any) {
		console.error('Failed to create note:', err)
		toast.error(err.message || __('Failed to save note'))
	} finally {
		isSubmitting.value = false
	}
}

// Edit existing note
const startEditNote = (note: LessonNoteItem) => {
	if (props.videoPlayer) {
		const isPlaying =
			typeof props.videoPlayer.playing === 'boolean'
				? props.videoPlayer.playing
				: Boolean(props.videoPlayer.playing?.value)
		wasPlayingBeforeOpen = isPlaying
		props.videoPlayer.pauseVideo?.()
	}
	editingNoteName.value = note.name
	editingNoteText.value = note.note || ''
	editingIsPinned.value = Boolean(note.is_pinned)
	editingColor.value = note.color || 'Yellow'
}

const cancelEditNote = () => {
	editingNoteName.value = null
	editingNoteText.value = ''
	if (wasPlayingBeforeOpen && props.videoPlayer?.resumeVideo) {
		props.videoPlayer.resumeVideo()
	}
}

const saveEditNote = async (note: LessonNoteItem) => {
	if (!editingNoteText.value.trim() || isSubmitting.value) return
	isSubmitting.value = true

	try {
		await call('frappe.client.set_value', {
			doctype: 'LMS Lesson Note',
			name: note.name,
			fieldname: {
				note: editingNoteText.value.trim(),
				is_pinned: editingIsPinned.value ? 1 : 0,
				color: editingColor.value,
			},
		})

		toast.success(__('Note updated successfully'))
		editingNoteName.value = null
		editingNoteText.value = ''
		notesResource.reload()
		emit('updateNotes')

		if (wasPlayingBeforeOpen && props.videoPlayer?.resumeVideo) {
			props.videoPlayer.resumeVideo()
		}
	} catch (err: any) {
		console.error('Failed to update note:', err)
		toast.error(err.message || __('Failed to update note'))
	} finally {
		isSubmitting.value = false
	}
}

// Toggle pin status
const togglePin = async (note: LessonNoteItem) => {
	try {
		const newPinned = note.is_pinned ? 0 : 1
		await call('frappe.client.set_value', {
			doctype: 'LMS Lesson Note',
			name: note.name,
			fieldname: 'is_pinned',
			value: newPinned,
		})
		notesResource.reload()
		emit('updateNotes')
	} catch (err: any) {
		console.error('Failed to toggle pin:', err)
	}
}

// Deletion confirmation
const promptDeleteNote = (note: LessonNoteItem) => {
	noteToDelete.value = note
	showDeleteDialog.value = true
}

const confirmDelete = async () => {
	if (!noteToDelete.value) return
	try {
		await call('frappe.client.delete', {
			doctype: 'LMS Lesson Note',
			name: noteToDelete.value.name,
		})
		toast.success(__('Note deleted successfully'))
		showDeleteDialog.value = false
		noteToDelete.value = null
		notesResource.reload()
		emit('updateNotes')
	} catch (err: any) {
		console.error('Failed to delete note:', err)
		toast.error(err.message || __('Failed to delete note'))
	}
}

const deleteDialogActions = computed(() => [
	{
		label: __('Cancel'),
		onClick: ({ close }: { close: () => void }) => {
			close()
			noteToDelete.value = null
		},
	},
	{
		label: __('Delete'),
		variant: 'solid' as const,
		theme: 'red' as const,
		onClick: async ({ close }: { close: () => void }) => {
			await confirmDelete()
			close()
		},
	},
])

// HTML escape helper for secure document export
const HTML_ESCAPE_MAP: Record<string, string> = {
	'&': '&amp;',
	'<': '&lt;',
	'>': '&gt;',
	'"': '&quot;',
	"'": '&#39;',
	'`': '&#x60;',
	'=': '&#x3D;',
}

const escapeHTML = (text: string | null | undefined): string => {
	if (!text) return ''
	return String(text).replace(/[&<>"'`=]/g, (char) => HTML_ESCAPE_MAP[char] || char)
}

// Export formatted printable notes via iframe without triggering popup blockers
const exportNotes = () => {
	if (!notesResource.data || notesResource.data.length === 0) {
		toast.info(__('No notes available to export'))
		return
	}

	const isRtl = typeof document !== 'undefined' && document.documentElement.dir === 'rtl'
	const userName = user?.data?.full_name || user?.data?.name || 'Learner'
	const lessonTitle = props.lesson
	const courseTitle = props.course || 'Civil Engineering Course'
	const currentDate = new Date().toLocaleDateString(isRtl ? 'ar-SA' : 'en-US', {
		year: 'numeric',
		month: 'long',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
	})

	const sortedForExport = [...notesResource.data].sort((a, b) => {
		const pinA = a.is_pinned ? 1 : 0
		const pinB = b.is_pinned ? 1 : 0
		if (pinA !== pinB) return pinB - pinA
		return (a.video_timestamp ?? 0) - (b.video_timestamp ?? 0)
	})

	// token-exempt-start: physical document print styling rendered to paper
	const notesHtml = sortedForExport
		.map((n) => {
			const timeFormatted = n.formatted_time || formatSeconds(n.video_timestamp || 0)
			const pinnedBadge = n.is_pinned
				? `<span style="background:var(--surface-amber-2,#fef3c7);color:var(--ink-amber-5,#92400e);padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">📌 ${__('Pinned')}</span>`
				: ''
			const noteBody = escapeHTML(n.note || '').replace(/\n/g, '<br>')
			return `
				<div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px 20px; margin-bottom: 14px; background: ${
					n.is_pinned ? '#fffdf7' : '#ffffff'
				}; page-break-inside: avoid;">
					<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
						<span style="background: #0284c7; color: #ffffff; padding: 3px 12px; border-radius: 9999px; font-size: 12px; font-weight: 700;">⏱ ${timeFormatted}</span>
						${pinnedBadge}
					</div>
					<div style="font-size: 14px; line-height: 1.6; color: #334155; white-space: pre-wrap;">${noteBody}</div>
				</div>
			`
		})
		.join('')

	const printableDoc = `
		<!DOCTYPE html>
		<html dir="${isRtl ? 'rtl' : 'ltr'}" lang="${isRtl ? 'ar' : 'en'}">
		<head>
			<meta charset="utf-8">
			<title>${escapeHTML(lessonTitle)} - ${__('Notes')}</title>
			<style>
				@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');
				body {
					font-family: ${isRtl ? "'Cairo', sans-serif" : "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"};
					margin: 0;
					padding: 36px;
					background: #ffffff;
					color: #0f172a;
				}
				.header {
					border-bottom: 2px solid #0284c7;
					padding-bottom: 18px;
					margin-bottom: 24px;
					display: flex;
					justify-content: space-between;
					align-items: flex-start;
				}
				.brand {
					font-size: 12px;
					text-transform: uppercase;
					letter-spacing: 0.08em;
					color: #0284c7;
					font-weight: 700;
				}
				h1 {
					margin: 6px 0 4px;
					font-size: 22px;
					color: #0f172a;
				}
				.course-info {
					font-size: 14px;
					color: #64748b;
				}
				.meta {
					text-align: ${isRtl ? 'left' : 'right'};
					font-size: 12px;
					color: #64748b;
					line-height: 1.5;
				}
				.summary-bar {
					background: #f8fafc;
					border: 1px solid #e2e8f0;
					border-radius: 8px;
					padding: 10px 16px;
					margin-bottom: 20px;
					font-size: 13px;
					color: #475569;
					display: flex;
					justify-content: space-between;
				}
				.footer {
					margin-top: 36px;
					padding-top: 14px;
					border-top: 1px solid #e2e8f0;
					text-align: center;
					font-size: 12px;
					color: #94a3b8;
				}
				@media print {
					body { padding: 12mm; }
					.no-print { display: none !important; }
				}
			</style>
		</head>
		<body>
			<div class="header">
				<div>
					<div class="brand">Handastech • Builders LMS</div>
					<h1>📝 ${escapeHTML(lessonTitle)}</h1>
					<div class="course-info">${escapeHTML(courseTitle)}</div>
				</div>
				<div class="meta">
					<div><strong>${__('Learner')}:</strong> ${escapeHTML(userName)}</div>
					<div><strong>${__('Generated')}:</strong> ${escapeHTML(currentDate)}</div>
				</div>
			</div>
			<div class="summary-bar">
				<span><strong>${__('Total Notes')}:</strong> ${sortedForExport.length}</span>
				<span><strong>${__('Pinned Notes')}:</strong> ${sortedForExport.filter((n) => n.is_pinned).length}</span>
			</div>
			<div class="notes-container">
				${notesHtml}
			</div>
			<div class="footer">
				${__('Builders LMS Engineering Course Watching & Smart Notes')}
			</div>
		</body>
		</html>
	`
	// token-exempt-end

	const iframe = document.createElement('iframe')
	iframe.setAttribute('style', 'position:fixed;right:0;bottom:0;width:0;height:0;border:0;')
	document.body.appendChild(iframe)
	const iframeDoc = iframe.contentWindow?.document
	if (iframeDoc) {
		iframeDoc.open()
		iframeDoc.write(printableDoc)
		iframeDoc.close()
		setTimeout(() => {
			iframe.contentWindow?.focus()
			iframe.contentWindow?.print()
			setTimeout(() => {
				iframe.remove()
			}, 1000)
		}, 300)
	}
}

// Global keyboard shortcut listener for "N" key
const handleGlobalKeyDown = (e: KeyboardEvent) => {
	if (e.key === 'n' || e.key === 'N') {
		const target = e.target as HTMLElement | null
		if (
			target &&
			(target.tagName === 'INPUT' ||
				target.tagName === 'TEXTAREA' ||
				target.isContentEditable ||
				target.closest('input') ||
				target.closest('textarea') ||
				target.closest('.ProseMirror') ||
				target.closest('[contenteditable="true"]'))
		) {
			return
		}
		if (e.ctrlKey || e.metaKey || e.altKey) {
			return
		}
		e.preventDefault()
		startCreateNote()
	}
}

// Video time polling for live "Add note at mm:ss" display
const updateLiveTime = () => {
	if (props.videoPlayer?.getCurrentTime) {
		currentVideoTime.value = props.videoPlayer.getCurrentTime()
	}
}

onMounted(() => {
	window.addEventListener('keydown', handleGlobalKeyDown)
	timePollTimer = setInterval(updateLiveTime, 500)
	updateLiveTime()
})

onBeforeUnmount(() => {
	window.removeEventListener('keydown', handleGlobalKeyDown)
	if (timePollTimer) {
		clearInterval(timePollTimer)
		timePollTimer = null
	}
})

defineExpose({
	formatSeconds,
	onSeekClick,
	startCreateNote,
	saveNewNote,
	exportNotes,
	notesResource,
})
</script>
