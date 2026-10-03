<template>
	<div class="lesson-resources-tab flex flex-col h-full min-h-0">
		<!-- Header: Search & Filter Chips -->
		<div class="px-3 pt-3 pb-2 shrink-0 border-b border-outline-gray-2 bg-surface-base space-y-2">
			<!-- Search Bar & Refresh -->
			<div class="flex items-center gap-2">
				<div class="relative flex-1 min-w-0">
					<Search class="absolute start-2.5 top-1/2 -translate-y-1/2 size-3.5 text-ink-gray-4 pointer-events-none" />
					<input
						type="text"
						v-model="searchQuery"
						:placeholder="__('Search files...')"
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

				<button
					type="button"
					@click="reloadResources"
					class="p-1.5 rounded-6 border border-outline-gray-2 bg-surface-base hover:bg-surface-gray-2 text-ink-gray-6 hover:text-ink-gray-9 transition-colors shrink-0"
					:title="__('Refresh resources')"
				>
					<RotateCw class="size-3.5" :class="{ 'animate-spin': isLoading }" />
				</button>
			</div>

			<!-- Filter Chips (All, DWG, XLSX, PDF, ZIP) -->
			<div class="flex items-center gap-1.5 overflow-x-auto pb-0.5 text-[11px]">
				<button
					v-for="filter in filterOptions"
					:key="filter.id"
					type="button"
					@click="activeFilter = filter.id"
					class="px-2.5 py-1 rounded-full font-medium transition-colors cursor-pointer shrink-0 inline-flex items-center gap-1"
					:class="
						activeFilter === filter.id
							? 'bg-surface-gray-8 text-ink-gray-2 font-semibold'
							: 'bg-surface-gray-2 text-ink-gray-7 hover:bg-surface-gray-3'
					"
				>
					<component :is="filter.icon" v-if="filter.icon" class="size-3" />
					<span>{{ filter.label }}</span>
					<span
						v-if="filterCounts[filter.id] > 0"
						class="ms-0.5 px-1 py-0.2 rounded-full text-[9px] font-bold"
						:class="activeFilter === filter.id ? 'bg-surface-gray-9 text-ink-gray-2' : 'bg-surface-gray-3 text-ink-gray-6'"
					>
						{{ filterCounts[filter.id] }}
					</span>
				</button>
			</div>
		</div>

		<!-- Resources List -->
		<div class="flex-1 min-h-0 overflow-y-auto p-2">
			<!-- Loading State -->
			<div v-if="isLoading" class="py-12 text-center text-ink-gray-5 text-xs">
				<Loader2 class="size-6 animate-spin mx-auto mb-2 text-ink-blue-5" />
				<span>{{ __('Loading resources...') }}</span>
			</div>

			<!-- Empty Search State -->
			<div
				v-else-if="filteredResources.length === 0 && searchQuery"
				class="rounded-7 border border-dashed border-outline-gray-2 p-8 text-center my-4"
			>
				<SearchX class="size-8 text-ink-gray-4 mx-auto mb-2" />
				<h4 class="text-xs font-semibold text-ink-gray-9 mb-1">
					{{ __('No matching files found') }}
				</h4>
				<p class="text-xs text-ink-gray-5 mb-3">
					{{ `${__('No files found matching')} "${searchQuery}"` }}
				</p>
				<button
					type="button"
					@click="searchQuery = ''"
					class="px-3 py-1 text-xs font-medium rounded-6 bg-surface-gray-2 hover:bg-surface-gray-3 text-ink-gray-8 cursor-pointer"
				>
					{{ __('Clear search') }}
				</button>
			</div>

			<!-- Empty Resources State -->
			<div
				v-else-if="filteredResources.length === 0"
				class="rounded-7 border border-dashed border-outline-gray-2 p-8 text-center my-4"
			>
				<div class="mx-auto size-12 rounded-full bg-surface-blue-1 flex items-center justify-center text-ink-blue-5 mb-3">
					<Paperclip class="size-6" />
				</div>
				<h3 class="text-xs font-bold text-ink-gray-9 mb-1">
					{{ __('No attachments for this lesson') }}
				</h3>
				<p class="text-xs text-ink-gray-5 max-w-xs mx-auto leading-relaxed mb-2">
					{{ __('No downloadable resources or attachments for this lesson.') }}
				</p>
				<p class="text-[11px] text-ink-gray-4 max-w-xs mx-auto leading-relaxed">
					{{ __('AutoCAD (DWG), Excel (XLSX), and engineering notes will appear here when added by the instructor.') }}
				</p>
			</div>

			<!-- Resource Cards -->
			<div v-else class="space-y-2">
				<div
					v-for="item in filteredResources"
					:key="item.id || item.file_url"
					class="rounded-6 border border-outline-gray-2 bg-surface-base p-3 hover:border-outline-gray-3 hover:shadow-xs transition-all flex flex-col gap-2 group"
				>
					<div class="flex items-start justify-between gap-2.5">
						<!-- Format Icon Badge -->
						<div
							class="size-9 rounded-6 flex items-center justify-center shrink-0 border transition-transform group-hover:scale-105"
							:class="getFormatBadgeClasses(item.extension)"
						>
							<component :is="getFormatIcon(item.extension)" class="size-4.5 stroke-1.5" />
						</div>

						<!-- File Details -->
						<div class="min-w-0 flex-1">
							<div class="flex items-center gap-1.5 flex-wrap">
								<!-- File Extension Pill -->
								<span
									class="px-1.5 py-0.2 rounded-4 text-[10px] font-mono font-bold tracking-wider uppercase border"
									:class="getFormatBadgeClasses(item.extension)"
								>
									{{ item.extension }}
								</span>

								<!-- Scope Pill (Lesson vs Course) -->
								<span
									class="px-1.5 py-0.2 rounded-4 text-[10px] font-medium"
									:class="
										item.scope === 'lesson'
											? 'bg-surface-blue-1 text-ink-blue-5 border border-outline-blue-2'
											: 'bg-surface-gray-2 text-ink-gray-6'
									"
								>
									{{ item.scope === 'lesson' ? __('Lesson attachment') : __('Course reference') }}
								</span>
							</div>

							<!-- File Name -->
							<h4
								class="text-xs font-bold text-ink-gray-9 mt-1 group-hover:text-ink-blue-5 transition-colors break-all leading-snug"
								:title="item.file_name"
							>
								{{ item.title || item.file_name }}
							</h4>

							<!-- Category & Size Meta -->
							<div class="flex items-center gap-2 text-[11px] text-ink-gray-5 mt-1">
								<span v-if="item.category">{{ item.category }}</span>
								<span v-if="item.category && item.formatted_size">•</span>
								<span v-if="item.formatted_size" class="tabular-nums font-mono">
									{{ item.formatted_size }}
								</span>
							</div>
						</div>
					</div>

					<!-- Bottom Action Row: Download & Copy Link -->
					<div class="flex items-center justify-between gap-2 pt-2 border-t border-outline-gray-2/70 mt-0.5">
						<button
							type="button"
							@click="copyResourceLink(item)"
							class="inline-flex items-center gap-1 text-[11px] font-medium text-ink-gray-5 hover:text-ink-gray-8 transition-colors cursor-pointer"
							:title="__('Copy file link')"
						>
							<Copy class="size-3" />
							<span>{{ copiedId === item.id ? __('Copied!') : __('Copy link') }}</span>
						</button>

						<!-- Instant Download Button -->
						<button
							type="button"
							@click="downloadResource(item)"
							class="inline-flex items-center gap-1.5 px-3 py-1 rounded-5 text-xs font-semibold bg-surface-gray-2 hover:bg-surface-blue-2 text-ink-gray-8 hover:text-ink-blue-5 border border-outline-gray-2 hover:border-outline-blue-2 transition-all cursor-pointer group/dl"
						>
							<Download class="size-3.5 group-hover/dl:-translate-y-0.5 transition-transform" />
							<span>{{ __('Download') }}</span>
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { call, toast } from 'frappe-ui'
import {
	Copy,
	Download,
	FileBox,
	FileCode,
	FileSpreadsheet,
	FileText,
	FolderArchive,
	Layers,
	Loader2,
	Paperclip,
	RotateCw,
	Search,
	SearchX,
	X,
} from 'lucide-vue-next'

export interface ResourceItem {
	id: string
	file_name: string
	title?: string
	file_url: string
	file_size?: number
	formatted_size?: string
	extension: string
	category?: string
	scope: 'lesson' | 'course'
	is_private?: boolean
}

interface Props {
	courseName: string
	currentLesson: string
	lessonTitle?: string
	resources?: ResourceItem[]
}

const props = withDefaults(defineProps<Props>(), {
	lessonTitle: '',
	resources: () => [],
})

const __ = (text: string) => (typeof window !== 'undefined' && (window as any).__ ? (window as any).__(text) : text)

const searchQuery = ref('')
const activeFilter = ref<string>('all')
const isLoading = ref(false)
const fetchedResources = ref<ResourceItem[]>([])
const copiedId = ref<string | null>(null)

const filterOptions = computed(() => [
	{ id: 'all', label: __('All'), icon: null },
	{ id: 'dwg', label: __('CAD / DWG'), icon: Layers },
	{ id: 'xlsx', label: __('Excel / XLSX'), icon: FileSpreadsheet },
	{ id: 'pdf', label: __('PDF'), icon: FileText },
	{ id: 'zip', label: __('ZIP / Archive'), icon: FolderArchive },
])

// Fetch attachments for current lesson & course
async function fetchAttachments() {
	if (!props.currentLesson && !props.courseName) return

	isLoading.value = true
	const items: ResourceItem[] = []

	try {
		// 1. Fetch lesson attachments
		if (props.currentLesson) {
			const lessonFiles: any = await call('frappe.client.get_list', {
				doctype: 'File',
				filters: {
					attached_to_doctype: 'Course Lesson',
					attached_to_name: props.currentLesson,
				},
				fields: ['name', 'file_name', 'file_url', 'file_size', 'is_private'],
				limit_page_length: 50,
			}).catch(() => [])

			if (Array.isArray(lessonFiles)) {
				for (const f of lessonFiles) {
					items.push(formatFileToResource(f, 'lesson'))
				}
			}
		}

		// 2. Fetch course attachments
		if (props.courseName) {
			const courseFiles: any = await call('frappe.client.get_list', {
				doctype: 'File',
				filters: {
					attached_to_doctype: 'LMS Course',
					attached_to_name: props.courseName,
				},
				fields: ['name', 'file_name', 'file_url', 'file_size', 'is_private'],
				limit_page_length: 50,
			}).catch(() => [])

			if (Array.isArray(courseFiles)) {
				for (const f of courseFiles) {
					// Avoid duplicates
					if (!items.some((i) => i.file_url === f.file_url)) {
						items.push(formatFileToResource(f, 'course'))
					}
				}
			}
		}
	} catch (err) {
		console.warn('Could not fetch attachments from Frappe File doctype', err)
	} finally {
		fetchedResources.value = items
		isLoading.value = false
	}
}

// Convert Frappe File record to structured ResourceItem
function formatFileToResource(file: any, scope: 'lesson' | 'course'): ResourceItem {
	const rawName = file.file_name || file.file_url?.split('/')?.pop() || 'attachment'
	let decodedName = rawName
	try {
		decodedName = decodeURIComponent(rawName)
	} catch {
		// ignore URI malformed error
	}

	const ext = getExtension(decodedName)
	return {
		id: file.name || file.file_url,
		file_name: decodedName,
		title: decodedName,
		file_url: file.file_url,
		file_size: file.file_size,
		formatted_size: formatBytes(file.file_size),
		extension: ext,
		category: getCategoryForExtension(ext),
		scope,
		is_private: Boolean(file.is_private),
	}
}

function getExtension(filename: string): string {
	if (!filename) return 'FILE'
	const parts = filename.split('.')
	if (parts.length > 1) {
		return parts.pop()!.toUpperCase()
	}
	return 'FILE'
}

function getCategoryForExtension(ext: string): string {
	switch (ext.toUpperCase()) {
		case 'DWG':
		case 'DXF':
			return __('CAD Drawing')
		case 'XLSX':
		case 'XLS':
		case 'CSV':
			return __('Calculation Sheet')
		case 'PDF':
			return __('Engineering Code')
		case 'ZIP':
		case 'RAR':
		case '7Z':
			return __('Project Bundle')
		default:
			return __('Attachment')
	}
}

function formatBytes(bytes?: number): string {
	if (!bytes || bytes <= 0) return ''
	if (bytes < 1024) return `${bytes} B`
	if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`
	return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// Combined list: custom props + fetched resources
const allResources = computed<ResourceItem[]>(() => {
	const set = new Map<string, ResourceItem>()

	// Passed via props
	if (props.resources && props.resources.length > 0) {
		for (const r of props.resources) {
			const ext = r.extension || getExtension(r.file_name || r.file_url)
			set.set(r.id || r.file_url, {
				...r,
				extension: ext.toUpperCase(),
				category: r.category || getCategoryForExtension(ext),
				formatted_size: r.formatted_size || formatBytes(r.file_size),
			})
		}
	}

	// Fetched from backend
	for (const r of fetchedResources.value) {
		if (!set.has(r.id) && !set.has(r.file_url)) {
			set.set(r.id, r)
		}
	}

	return Array.from(set.values())
})

// Filter counts
const filterCounts = computed<Record<string, number>>(() => {
	const counts: Record<string, number> = {
		all: allResources.value.length,
		dwg: 0,
		xlsx: 0,
		pdf: 0,
		zip: 0,
	}

	for (const r of allResources.value) {
		const ext = r.extension?.toLowerCase()
		if (ext === 'dwg' || ext === 'dxf') counts.dwg++
		else if (ext === 'xlsx' || ext === 'xls' || ext === 'csv') counts.xlsx++
		else if (ext === 'pdf') counts.pdf++
		else if (ext === 'zip' || ext === 'rar' || ext === '7z') counts.zip++
	}

	return counts
})

// Filtered Resources
const filteredResources = computed(() => {
	let list = allResources.value

	// Extension filter
	if (activeFilter.value !== 'all') {
		const target = activeFilter.value.toLowerCase()
		list = list.filter((r) => {
			const ext = r.extension?.toLowerCase()
			if (target === 'dwg') return ext === 'dwg' || ext === 'dxf'
			if (target === 'xlsx') return ext === 'xlsx' || ext === 'xls' || ext === 'csv'
			if (target === 'pdf') return ext === 'pdf'
			if (target === 'zip') return ext === 'zip' || ext === 'rar' || ext === '7z'
			return ext === target
		})
	}

	// Search query filter
	const q = searchQuery.value.trim().toLowerCase()
	if (q) {
		list = list.filter((r) => {
			return (
				r.file_name.toLowerCase().includes(q) ||
				(r.title && r.title.toLowerCase().includes(q)) ||
				(r.category && r.category.toLowerCase().includes(q))
			)
		})
	}

	return list
})

function getFormatBadgeClasses(ext: string): string {
	switch (ext?.toUpperCase()) {
		case 'DWG':
		case 'DXF':
			return 'bg-surface-blue-2 text-ink-blue-5 border-outline-blue-2'
		case 'XLSX':
		case 'XLS':
		case 'CSV':
			return 'bg-surface-green-2 text-ink-green-8 border-outline-green-2'
		case 'PDF':
			return 'bg-surface-red-2 text-ink-red-5 border-outline-red-2'
		case 'ZIP':
		case 'RAR':
		case '7Z':
			return 'bg-surface-amber-2 text-ink-amber-5 border-outline-amber-2'
		default:
			return 'bg-surface-gray-2 text-ink-gray-7 border-outline-gray-2'
	}
}

function getFormatIcon(ext: string) {
	switch (ext?.toUpperCase()) {
		case 'DWG':
		case 'DXF':
			return Layers
		case 'XLSX':
		case 'XLS':
		case 'CSV':
			return FileSpreadsheet
		case 'PDF':
			return FileText
		case 'ZIP':
		case 'RAR':
		case '7Z':
			return FolderArchive
		default:
			return FileBox
	}
}

// Download action
function downloadResource(item: ResourceItem) {
	let downloadUrl = item.file_url

	// If it is a private file, route through serve_resource
	if (item.is_private || downloadUrl.startsWith('/private/')) {
		downloadUrl = `/api/method/lms.lms.doctype.course_lesson.course_lesson.serve_resource?file_url=${encodeURIComponent(
			downloadUrl
		)}`
	}

	const a = document.createElement('a')
	a.href = downloadUrl
	a.download = item.file_name || 'download'
	a.target = '_blank'
	document.body.appendChild(a)
	a.click()
	document.body.removeChild(a)

	toast.success(`${__('Downloading')} ${item.file_name}`)
}

function copyResourceLink(item: ResourceItem) {
	const fullUrl = window.location.origin + item.file_url
	navigator.clipboard.writeText(fullUrl).then(() => {
		copiedId.value = item.id
		toast.success(__('File link copied to clipboard'))
		setTimeout(() => {
			if (copiedId.value === item.id) {
				copiedId.value = null
			}
		}, 2000)
	})
}

function reloadResources() {
	fetchAttachments()
}

watch(
	() => [props.currentLesson, props.courseName],
	() => {
		fetchAttachments()
	}
)

onMounted(() => {
	fetchAttachments()
})
</script>

<style scoped>
.lesson-resources-tab {
	direction: inherit;
}
</style>
