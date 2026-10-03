<template>
	<div class="lesson-qa-tab flex flex-col h-full min-h-0">
		<!-- Discussions Disabled Banner -->
		<div
			v-if="!allowDiscussions"
			class="p-4 m-3 rounded-7 border border-outline-gray-2 bg-surface-gray-1 text-center"
		>
			<MessageSquareOff class="size-8 text-ink-gray-4 mx-auto mb-2" />
			<h4 class="text-xs font-bold text-ink-gray-9 mb-1">
				{{ __('Discussions are disabled for this course') }}
			</h4>
			<p class="text-xs text-ink-gray-5">
				{{ __('Discussions are currently disabled by the instructor for this course.') }}
			</p>
		</div>

		<!-- Main Active Discussions Area -->
		<template v-else>
			<!-- VIEW 1: Active Thread (Detail View) -->
			<div v-if="activeTopic" class="flex flex-col h-full min-h-0">
				<!-- Thread Header with Back Action -->
				<div class="px-3 py-2.5 shrink-0 border-b border-outline-gray-2 bg-surface-base flex items-center justify-between gap-2">
					<button
						type="button"
						@click="closeThread"
						class="inline-flex items-center gap-1.5 px-2 py-1 rounded-6 text-xs font-medium text-ink-gray-7 hover:text-ink-gray-9 hover:bg-surface-gray-2 transition-colors cursor-pointer"
					>
						<ArrowLeft class="size-3.5" />
						<span>{{ __('Back to Questions') }}</span>
					</button>

					<button
						type="button"
						@click="refreshThread"
						class="p-1 rounded-6 text-ink-gray-5 hover:text-ink-gray-8 hover:bg-surface-gray-2 transition-colors"
						:title="__('Refresh replies')"
					>
						<RotateCw class="size-3.5" :class="{ 'animate-spin': repliesResource.loading }" />
					</button>
				</div>

				<!-- Thread Content & Replies List -->
				<div class="flex-1 min-h-0 overflow-y-auto px-3 py-3 space-y-3">
					<!-- Topic OP Card -->
					<div class="rounded-7 border border-outline-gray-2 bg-surface-base p-3.5 shadow-xs">
						<div class="flex items-start justify-between gap-2 mb-2">
							<div class="flex items-center gap-2 min-w-0">
								<UserAvatar :user="activeTopic.user" size="md" />
								<div class="min-w-0">
									<div class="text-xs font-bold text-ink-gray-9 truncate">
										{{ activeTopic.user?.full_name || activeTopic.owner || __('Student') }}
									</div>
									<div class="text-[11px] text-ink-gray-5">
										{{ timeAgo(activeTopic.creation) }}
									</div>
								</div>
							</div>

							<!-- Timestamp Jump Pill if captured -->
							<button
								v-if="getTopicTimestamp(activeTopic)"
								type="button"
								@click="seekTo(getTopicTimestamp(activeTopic)!.seconds)"
								class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-surface-blue-2 text-ink-blue-5 border border-outline-blue-2 hover:bg-surface-blue-3 transition-colors cursor-pointer shrink-0"
								:title="__('Jump video to this timestamp')"
							>
								<Play class="size-3 fill-current" />
								<span>{{ getTopicTimestamp(activeTopic)!.formatted }}</span>
							</button>
						</div>

						<h3 class="text-sm font-bold text-ink-gray-9 leading-snug mb-1.5">
							{{ cleanTitle(activeTopic.title) }}
						</h3>
					</div>

					<!-- Replies Divider -->
					<div class="flex items-center gap-2 px-1 text-xs font-semibold text-ink-gray-6">
						<MessageSquare class="size-3.5 text-ink-gray-5" />
						<span>{{ __('Replies') }} ({{ repliesList.length }})</span>
					</div>

					<!-- Replies Loading -->
					<div v-if="repliesResource.loading && repliesList.length === 0" class="py-6 text-center text-ink-gray-5 text-xs">
						<Loader2 class="size-5 animate-spin mx-auto mb-1 text-ink-blue-5" />
						<span>{{ __('Loading replies...') }}</span>
					</div>

					<!-- Empty Replies State -->
					<div
						v-else-if="repliesList.length === 0"
						class="rounded-6 border border-dashed border-outline-gray-2 p-5 text-center text-ink-gray-5"
					>
						<p class="text-xs">{{ __('No answers yet. Be the first to help!') }}</p>
					</div>

					<!-- Replies List -->
					<div v-else class="space-y-2">
						<div
							v-for="reply in repliesList"
							:key="reply.name"
							class="rounded-6 border border-outline-gray-2 bg-surface-gray-1 p-3 transition-all"
						>
							<div class="flex items-center justify-between gap-2 mb-1.5">
								<div class="flex items-center gap-2 min-w-0">
									<UserAvatar :user="reply.user" size="sm" />
									<div class="min-w-0">
										<span class="text-xs font-semibold text-ink-gray-9 block truncate">
											{{ reply.user?.full_name || reply.owner }}
										</span>
									</div>
								</div>
								<div class="flex items-center gap-2 shrink-0">
									<!-- Timestamp pill in reply if present -->
									<button
										v-if="getTimestampFromText(reply.reply)"
										type="button"
										@click="seekTo(getTimestampFromText(reply.reply)!.seconds)"
										class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-semibold bg-surface-blue-2 text-ink-blue-5 border border-outline-blue-2 hover:bg-surface-blue-3 transition-colors cursor-pointer"
										:title="__('Jump video to timestamp')"
									>
										<Play class="size-2.5 fill-current" />
										<span>{{ getTimestampFromText(reply.reply)!.formatted }}</span>
									</button>
									<span class="text-[10px] text-ink-gray-5">{{ timeAgo(reply.creation) }}</span>
								</div>
							</div>

							<!-- Reply Body HTML / Content -->
							<div
								class="text-xs text-ink-gray-8 leading-relaxed break-words prose-sm max-w-none"
								v-html="renderCleanContent(reply.reply)"
							/>
						</div>
					</div>
				</div>

				<!-- Inline Reply Composer -->
				<div class="p-3 shrink-0 border-t border-outline-gray-2 bg-surface-base">
					<div class="flex flex-col gap-2">
						<textarea
							v-model="newReplyText"
							rows="2"
							:placeholder="__('Write an answer...')"
							class="w-full p-2 text-xs rounded-6 border border-outline-gray-2 bg-surface-gray-1 focus:bg-surface-base focus:outline-none focus:ring-2 focus:ring-outline-blue-2 text-ink-gray-9 placeholder:text-ink-gray-4 resize-none transition-all"
						/>
						<div class="flex items-center justify-between gap-2">
							<!-- Quick Insert Timestamp into reply -->
							<button
								type="button"
								@click="insertCurrentTimeToReply"
								class="inline-flex items-center gap-1 px-2 py-1 rounded-5 text-[11px] font-medium text-ink-blue-5 bg-surface-blue-2 hover:bg-surface-blue-3 transition-colors cursor-pointer"
								:title="__('Insert current video timestamp into reply')"
							>
								<Clock class="size-3" />
								<span>{{ formatSeconds(currentVideoTime) }}</span>
							</button>

							<Button
								variant="solid"
								theme="primary"
								size="sm"
								:loading="isSubmittingReply"
								:disabled="!newReplyText.trim()"
								@click="postReply"
							>
								<template #prefix>
									<Send class="size-3" />
								</template>
								{{ __('Post Answer') }}
							</Button>
						</div>
					</div>
				</div>
			</div>

			<!-- VIEW 2: Ask New Question Form -->
			<div v-else-if="isCreatingQuestion" class="flex flex-col h-full min-h-0">
				<!-- Header -->
				<div class="px-4 py-3 shrink-0 border-b border-outline-gray-2 bg-surface-base flex items-center justify-between">
					<div class="flex items-center gap-2">
						<HelpCircle class="size-4 text-ink-blue-5" />
						<span class="text-xs font-bold text-ink-gray-9">{{ __('Ask a Question') }}</span>
					</div>
					<button
						type="button"
						@click="isCreatingQuestion = false"
						class="p-1 rounded-full text-ink-gray-4 hover:text-ink-gray-8 hover:bg-surface-gray-2"
					>
						<X class="size-4" />
					</button>
				</div>

				<!-- Form Content -->
				<div class="flex-1 min-h-0 overflow-y-auto p-4 space-y-4">
					<!-- Video Timestamp Anchor (Task 4 Brief Requirement) -->
					<div class="p-3 rounded-6 border border-outline-blue-2 bg-surface-blue-1/50 transition-all">
						<label class="flex items-center gap-2.5 cursor-pointer">
							<Checkbox
								v-model="linkToTimestamp"
							/>
							<div class="flex-1 min-w-0">
								<div class="flex items-center gap-1.5 text-xs font-bold text-ink-gray-9">
									<span>{{ __('Link to current video timestamp') }}</span>
								</div>
								<div class="flex items-center gap-1 text-[11px] text-ink-blue-5 mt-0.5">
									<Clock class="size-3" />
									<span>{{ __('Captured time:') }} {{ formatSeconds(capturedTime) }}</span>
								</div>
							</div>
							<button
								type="button"
								@click="recaptureTime"
								class="px-2 py-0.5 rounded-5 border border-outline-gray-2 bg-surface-base text-[10px] font-medium text-ink-gray-7 hover:bg-surface-gray-2"
								:title="__('Update timestamp to current video position')"
							>
								{{ __('Update') }}
							</button>
						</label>
					</div>

					<!-- Question Title -->
					<div>
						<label class="block text-xs font-bold text-ink-gray-8 mb-1">
							{{ __('Question Title') }} <span class="text-ink-red-5">*</span>
						</label>
						<input
							type="text"
							v-model="newQuestionTitle"
							:placeholder="__('e.g. Question about shear reinforcement in beams...')"
							class="w-full px-3 py-2 text-xs rounded-6 border border-outline-gray-2 bg-surface-base focus:outline-none focus:ring-2 focus:ring-outline-blue-2 text-ink-gray-9 placeholder:text-ink-gray-4 transition-all"
						/>
					</div>

					<!-- Question Details -->
					<div>
						<label class="block text-xs font-bold text-ink-gray-8 mb-1">
							{{ __('Question Details') }} <span class="text-ink-red-5">*</span>
						</label>
						<textarea
							v-model="newQuestionDetails"
							rows="5"
							:placeholder="__('Explain your question or formula in detail...')"
							class="w-full p-3 text-xs rounded-6 border border-outline-gray-2 bg-surface-base focus:outline-none focus:ring-2 focus:ring-outline-blue-2 text-ink-gray-9 placeholder:text-ink-gray-4 resize-none transition-all"
						/>
					</div>
				</div>

				<!-- Actions -->
				<div class="p-3 shrink-0 border-t border-outline-gray-2 bg-surface-base flex items-center justify-end gap-2">
					<Button
						variant="subtle"
						size="sm"
						@click="isCreatingQuestion = false"
					>
						{{ __('Cancel') }}
					</Button>
					<Button
						variant="solid"
						theme="primary"
						size="sm"
						:loading="isSubmittingQuestion"
						:disabled="!newQuestionTitle.trim() || !newQuestionDetails.trim()"
						@click="submitNewQuestion"
					>
						<template #prefix>
							<Send class="size-3" />
						</template>
						{{ __('Post Question') }}
					</Button>
				</div>
			</div>

			<!-- VIEW 3: Questions List (Master View) -->
			<div v-else class="flex flex-col h-full min-h-0">
				<!-- Search & Actions Top Bar -->
				<div class="px-3 pt-3 pb-2 shrink-0 border-b border-outline-gray-2 bg-surface-base space-y-2">
					<div class="flex items-center gap-2">
						<!-- Search Input -->
						<div class="relative flex-1 min-w-0">
							<Search class="absolute start-2.5 top-1/2 -translate-y-1/2 size-3.5 text-ink-gray-4 pointer-events-none" />
							<input
								type="text"
								v-model="searchQuery"
								:placeholder="__('Search Q&A')"
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

						<!-- Ask Button -->
						<Button
							variant="solid"
							theme="primary"
							size="sm"
							class="shrink-0"
							@click="openAskModal"
						>
							<template #prefix>
								<Plus class="size-3.5" />
							</template>
							{{ __('Ask a question') }}
						</Button>
					</div>

					<!-- Filter Chips (All, With Timestamps, My Questions) -->
					<div class="flex items-center gap-1.5 overflow-x-auto pb-0.5 text-[11px]">
						<button
							type="button"
							@click="activeFilter = 'all'"
							class="px-2.5 py-1 rounded-full font-medium transition-colors cursor-pointer shrink-0"
							:class="activeFilter === 'all' ? 'bg-surface-gray-8 text-ink-gray-2 font-semibold' : 'bg-surface-gray-2 text-ink-gray-7 hover:bg-surface-gray-3'"
						>
							{{ __('All') }}
						</button>
						<button
							type="button"
							@click="activeFilter = 'timestamps'"
							class="px-2.5 py-1 rounded-full font-medium inline-flex items-center gap-1 transition-colors cursor-pointer shrink-0"
							:class="activeFilter === 'timestamps' ? 'bg-surface-blue-2 text-ink-blue-5 font-semibold border border-outline-blue-2' : 'bg-surface-gray-2 text-ink-gray-7 hover:bg-surface-gray-3'"
						>
							<Clock class="size-3" />
							<span>{{ __('With Timestamps') }}</span>
						</button>
					</div>
				</div>

				<!-- Questions List Content -->
				<div class="flex-1 min-h-0 overflow-y-auto p-2">
					<!-- Loading -->
					<div v-if="topicsResource.loading" class="py-12 text-center text-ink-gray-5 text-xs">
						<Loader2 class="size-6 animate-spin mx-auto mb-2 text-ink-blue-5" />
						<span>{{ __('Loading questions...') }}</span>
					</div>

					<!-- Empty Search State -->
					<div
						v-else-if="filteredTopics.length === 0 && searchQuery"
						class="rounded-7 border border-dashed border-outline-gray-2 p-8 text-center my-4"
					>
						<SearchX class="size-8 text-ink-gray-4 mx-auto mb-2" />
						<h4 class="text-xs font-semibold text-ink-gray-9 mb-1">
							{{ __('No matching questions found') }}
						</h4>
						<p class="text-xs text-ink-gray-5 mb-3">
							{{ `${__('No questions found matching')} "${searchQuery}"` }}
						</p>
						<button
							type="button"
							@click="searchQuery = ''"
							class="px-3 py-1 text-xs font-medium rounded-6 bg-surface-gray-2 hover:bg-surface-gray-3 text-ink-gray-8 cursor-pointer"
						>
							{{ __('Clear search') }}
						</button>
					</div>

					<!-- Empty Discussions State -->
					<div
						v-else-if="filteredTopics.length === 0"
						class="rounded-7 border border-dashed border-outline-gray-2 p-8 text-center my-4"
					>
						<div class="mx-auto size-12 rounded-full bg-surface-blue-1 flex items-center justify-center text-ink-blue-5 mb-3">
							<MessageCircleQuestion class="size-6" />
						</div>
						<h3 class="text-xs font-bold text-ink-gray-9 mb-1">
							{{ __('No questions yet') }}
						</h3>
						<p class="text-xs text-ink-gray-5 max-w-xs mx-auto leading-relaxed mb-4">
							{{ __('No questions yet for this lesson. Have a question about this lecture? Ask below!') }}
						</p>
						<Button
							variant="solid"
							theme="primary"
							size="sm"
							@click="openAskModal"
						>
							<template #prefix>
								<Plus class="size-3.5" />
							</template>
							{{ __('Ask a question') }}
						</Button>
					</div>

					<!-- Questions Cards List -->
					<div v-else class="space-y-2">
						<div
							v-for="topic in filteredTopics"
							:key="topic.name"
							@click="openThread(topic)"
							class="rounded-6 border border-outline-gray-2 bg-surface-base p-3 hover:border-outline-gray-3 hover:shadow-xs transition-all cursor-pointer group"
						>
							<!-- Top Info: User & Timestamp -->
							<div class="flex items-start justify-between gap-2 mb-1.5">
								<div class="flex items-center gap-2 min-w-0">
									<UserAvatar :user="topic.user" size="sm" />
									<div class="min-w-0">
										<span class="text-xs font-semibold text-ink-gray-9 truncate block">
											{{ topic.user?.full_name || topic.owner || __('Student') }}
										</span>
										<span class="text-[10px] text-ink-gray-5">
											{{ timeAgo(topic.creation) }}
										</span>
									</div>
								</div>

								<!-- Timestamp Seek Pill (Interactive) -->
								<button
									v-if="getTopicTimestamp(topic)"
									type="button"
									@click.stop="seekTo(getTopicTimestamp(topic)!.seconds)"
									class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-surface-blue-2 text-ink-blue-5 border border-outline-blue-2 hover:bg-surface-blue-3 transition-colors cursor-pointer shrink-0"
									:title="__('Jump video to timestamp')"
								>
									<Play class="size-2.5 fill-current" />
									<span>{{ getTopicTimestamp(topic)!.formatted }}</span>
								</button>
							</div>

							<!-- Topic Title -->
							<h4 class="text-xs font-bold text-ink-gray-9 group-hover:text-ink-blue-5 transition-colors line-clamp-2 leading-snug mb-2">
								{{ cleanTitle(topic.title) }}
							</h4>

							<!-- Card Footer: Reply Count -->
							<div class="flex items-center justify-between text-[11px] text-ink-gray-5 pt-1 border-t border-outline-gray-2/60">
								<span class="inline-flex items-center gap-1">
									<MessageSquare class="size-3 text-ink-gray-4" />
									<span class="tabular-nums font-medium">
										{{ topic.reply_count || 0 }} {{ topic.reply_count === 1 ? __('Reply') : __('Replies') }}
									</span>
								</span>
								<span class="text-ink-blue-5 font-medium group-hover:underline inline-flex items-center gap-0.5">
									{{ __('View discussion') }}
									<ChevronRight class="size-3" />
								</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</template>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, onUnmounted, ref, watch } from 'vue'
import { Button, Checkbox, call, createResource, toast } from 'frappe-ui'
import {
	ArrowLeft,
	Clock,
	ChevronRight,
	HelpCircle,
	Loader2,
	MessageCircleQuestion,
	MessageSquare,
	MessageSquareOff,
	Play,
	Plus,
	RotateCw,
	Search,
	SearchX,
	Send,
	X,
} from 'lucide-vue-next'
import UserAvatar from '@/components/UserAvatar.vue'
import { timeAgo } from '@/utils'

interface VideoPlayerAPI {
	getCurrentTime?: () => number
	seekTo?: (seconds: number) => void
	pauseVideo?: () => void
	resumeVideo?: () => void
}

interface Props {
	courseName?: string
	currentLesson: string
	videoPlayer?: VideoPlayerAPI | null
	allowDiscussions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	courseName: '',
	videoPlayer: null,
	allowDiscussions: true,
})

const emit = defineEmits<{
	(e: 'seek', seconds: number): void
}>()

const socket = inject<any>('$socket', null)
const user = inject<any>('$user', null)
const __ = (text: string) => (typeof window !== 'undefined' && (window as any).__ ? (window as any).__(text) : text)

const activeTopic = ref<any | null>(null)
const isCreatingQuestion = ref(false)
const searchQuery = ref('')
const activeFilter = ref<'all' | 'timestamps'>('all')

// Form reactive fields
const newQuestionTitle = ref('')
const newQuestionDetails = ref('')
const linkToTimestamp = ref(true)
const capturedTime = ref(0)
const isSubmittingQuestion = ref(false)

// Reply fields
const newReplyText = ref('')
const isSubmittingReply = ref(false)

// Read current video time
const currentVideoTime = computed(() => {
	if (props.videoPlayer && typeof props.videoPlayer.getCurrentTime === 'function') {
		try {
			return Math.floor(props.videoPlayer.getCurrentTime() || 0)
		} catch {
			return 0
		}
	}
	return 0
})

// Discussions Topics Resource
const topicsResource = createResource({
	url: 'lms.lms.utils.get_discussion_topics',
	cache: ['lesson_discussion_topics', props.currentLesson],
	makeParams() {
		return {
			doctype: 'Course Lesson',
			docname: props.currentLesson,
			single_thread: false,
		}
	},
	auto: Boolean(props.currentLesson && props.allowDiscussions),
})

// Replies Resource for selected topic
const repliesResource = createResource({
	url: 'frappe.client.get_list',
	makeParams() {
		return {
			doctype: 'Discussion Reply',
			filters: {
				topic: activeTopic.value?.name,
			},
			fields: ['name', 'reply', 'owner', 'creation', 'modified'],
			order_by: 'creation asc',
			limit_page_length: 50,
		}
	},
	auto: false,
})

const repliesList = computed<any[]>(() => {
	if (!repliesResource.data) return []
	return repliesResource.data
})

watch(
	() => props.currentLesson,
	(newVal) => {
		activeTopic.value = null
		isCreatingQuestion.value = false
		if (newVal && props.allowDiscussions) {
			topicsResource.reload()
		}
	}
)

onMounted(() => {
	if (props.currentLesson && props.allowDiscussions) {
		topicsResource.reload()
	}
	if (socket && typeof socket.on === 'function') {
		socket.on('new_discussion_topic', () => {
			topicsResource.refresh()
		})
	}
})

onUnmounted(() => {
	if (socket && typeof socket.off === 'function') {
		socket.off('new_discussion_topic')
	}
})

// Timestamp helpers
function formatSeconds(secs: number): string {
	if (isNaN(secs) || secs < 0) return '00:00'
	const h = Math.floor(secs / 3600)
	const m = Math.floor((secs % 3600) / 60)
	const s = Math.floor(secs % 60)
	if (h > 0) {
		return `${h}:${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`
	}
	return `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`
}

function getTimestampFromText(text?: string): { seconds: number; formatted: string } | null {
	if (!text) return null
	const match = text.match(/\[(\d{1,2}:)?(\d{1,2}):(\d{2})\]/) || text.match(/(\d{1,2}):(\d{2})/)
	if (match) {
		const raw = match[0].replace(/[\[\]]/g, '')
		const parts = raw.split(':').map(Number)
		let seconds = 0
		if (parts.length === 3) {
			seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
		} else if (parts.length === 2) {
			seconds = parts[0] * 60 + parts[1]
		}
		return { seconds, formatted: raw }
	}
	return null
}

function getTopicTimestamp(topic: any): { seconds: number; formatted: string } | null {
	return getTimestampFromText(topic.title)
}

function cleanTitle(title?: string): string {
	if (!title) return ''
	// Remove timestamp prefix like [02:30] for clean display if desired, or keep as is
	return title.replace(/^\[(\d{1,2}:)?\d{1,2}:\d{2}\]\s*/, '')
}

function renderCleanContent(content?: string): string {
	if (!content) return ''
	// Basic sanitation/escaping for safe display
	return content
}

// Filtered Topics
const filteredTopics = computed(() => {
	if (!topicsResource.data) return []
	let list = topicsResource.data as any[]

	// Filter by search query
	const q = searchQuery.value.trim().toLowerCase()
	if (q) {
		list = list.filter((t) => {
			return (
				(t.title && t.title.toLowerCase().includes(q)) ||
				(t.owner && t.owner.toLowerCase().includes(q)) ||
				(t.user?.full_name && t.user.full_name.toLowerCase().includes(q))
			)
		})
	}

	// Filter by timestamps toggle
	if (activeFilter.value === 'timestamps') {
		list = list.filter((t) => Boolean(getTopicTimestamp(t)))
	}

	return list
})

function seekTo(seconds: number) {
	if (props.videoPlayer && typeof props.videoPlayer.seekTo === 'function') {
		props.videoPlayer.seekTo(seconds)
	}
	emit('seek', seconds)
}

function openAskModal() {
	capturedTime.value = currentVideoTime.value
	linkToTimestamp.value = currentVideoTime.value > 0
	newQuestionTitle.value = ''
	newQuestionDetails.value = ''
	isCreatingQuestion.value = true
}

function recaptureTime() {
	capturedTime.value = currentVideoTime.value
}

function openThread(topic: any) {
	activeTopic.value = topic
	newReplyText.value = ''
	repliesResource.reload()
}

function closeThread() {
	activeTopic.value = null
	newReplyText.value = ''
}

function refreshThread() {
	if (activeTopic.value) {
		repliesResource.reload()
	}
}

function insertCurrentTimeToReply() {
	const ts = formatSeconds(currentVideoTime.value)
	newReplyText.value += (newReplyText.value ? ' ' : '') + `[${ts}] `
}

async function submitNewQuestion() {
	if (!newQuestionTitle.value.trim() || !newQuestionDetails.value.trim()) return

	isSubmittingQuestion.value = true

	let titleToSave = newQuestionTitle.value.trim()
	if (linkToTimestamp.value) {
		const ts = formatSeconds(capturedTime.value)
		titleToSave = `[${ts}] ${titleToSave}`
	}

	try {
		// 1. Insert Discussion Topic
		const topicDoc: any = await call('frappe.client.insert', {
			doc: {
				doctype: 'Discussion Topic',
				reference_doctype: 'Course Lesson',
				reference_docname: props.currentLesson,
				title: titleToSave,
			},
		})

		// 2. Insert Initial Reply (Question Details)
		let replyContent = newQuestionDetails.value.trim()
		if (linkToTimestamp.value) {
			const ts = formatSeconds(capturedTime.value)
			replyContent = `[${ts}] ${replyContent}`
		}

		await call('frappe.client.insert', {
			doc: {
				doctype: 'Discussion Reply',
				topic: topicDoc.name,
				reply: replyContent,
			},
		})

		toast.success(__('Question posted successfully'))
		isCreatingQuestion.value = false
		newQuestionTitle.value = ''
		newQuestionDetails.value = ''

		// Reload topics and auto-open new topic
		await topicsResource.reload()
		const created = (topicsResource.data as any[])?.find((t) => t.name === topicDoc.name)
		if (created) {
			openThread(created)
		}
	} catch (err: any) {
		console.error('Failed to post discussion topic', err)
		toast.error(err?.messages?.[0] || __('Failed to post question'))
	} finally {
		isSubmittingQuestion.value = false
	}
}

async function postReply() {
	if (!newReplyText.value.trim() || !activeTopic.value) return

	isSubmittingReply.value = true
	try {
		await call('frappe.client.insert', {
			doc: {
				doctype: 'Discussion Reply',
				topic: activeTopic.value.name,
				reply: newReplyText.value.trim(),
			},
		})

		toast.success(__('Reply posted successfully'))
		newReplyText.value = ''
		await repliesResource.reload()
		topicsResource.refresh()
	} catch (err: any) {
		console.error('Failed to post reply', err)
		toast.error(err?.messages?.[0] || __('Failed to post reply'))
	} finally {
		isSubmittingReply.value = false
	}
}
</script>

<style scoped>
.lesson-qa-tab {
	direction: inherit;
}
</style>
