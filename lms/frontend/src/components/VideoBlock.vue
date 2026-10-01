<template>
	<div class="ht-video-wrapper">
		<div v-if="quizzes.length && !showQuiz && readOnly" class="leading-6 mb-2">
			{{
				__('This video contains {0} {1}:').format(
					quizzes.length,
					quizzes.length == 1 ? 'quiz' : 'quizzes'
				)
			}}

			<div
				v-for="(quiz, index) in quizzes"
				:key="`${quiz.quiz}-${index}`"
				class="ps-3 mt-1"
			>
				<span>
					{{ index + 1 }}. <span class="font-semibold"> {{ quiz.quiz }} </span>
				</span>
				{{ __('at {0} minutes').format(formatTimestamp(quiz.time)) }}
			</div>
		</div>

		<div
			v-if="!showQuiz"
			ref="videoContainer"
			class="video-block relative group overflow-hidden rounded-7 border border-outline-gray-2 bg-slate-950"
			oncontextmenu="return false"
		>
			<!-- NATIVE / HLS VIDEO ELEMENT -->
			<video
				@timeupdate="updateTime"
				@ended="videoEnded"
				@click="togglePlay"
				oncontextmenu="return false"
				controlslist="nodownload noplaybackrate"
				disablePictureInPicture
				class="block cursor-pointer size-full object-contain"
				ref="videoRef"
				:src="isHls ? undefined : safeUrl(fileURL)"
				:type="type"
			></video>

			<!-- FORENSIC FLOATING WATERMARK OVERLAY -->
			<div
				v-if="watermarkData.email || watermarkData.user_id"
				ref="watermarkRef"
				id="ht-forensic-watermark"
				class="ht-watermark absolute pointer-events-none select-none z-20"
				:style="watermarkStyle"
			>
				<div
					class="ht-watermark-badge bg-black/45 backdrop-blur-xs text-white/50 px-2.5 py-1 rounded border border-white/10 shadow-sm flex flex-col items-center leading-tight"
				>
					<span class="font-bold text-white/70 tracking-wide">{{ watermarkData.full_name || watermarkData.user_id }}</span>
					<span class="text-[10px] tracking-wider">{{ watermarkData.email }} • {{ watermarkData.ip }}</span>
					<span class="text-[9px] text-white/40">{{ watermarkData.timestamp }} • Handastech</span>
				</div>
			</div>

			<!-- ANTI-TAMPER SECURITY SHIELD OVERLAY -->
			<div
				v-if="isTampered"
				class="absolute inset-0 z-40 bg-slate-950/95 backdrop-blur-md flex flex-col items-center justify-center p-6 text-center text-white"
			>
				<div class="w-14 h-14 rounded-full bg-red-600/20 border border-red-500 flex items-center justify-center text-red-500 mb-3 text-2xl font-bold">
					⚠️
				</div>
				<h3 class="text-base sm:text-lg font-bold text-red-400 mb-2">
					تنبيه أمني: تم رصد محاولة تلاعب أو حجب للعلامة المائية
				</h3>
				<p class="text-xs sm:text-sm text-slate-300 max-w-md mb-4 leading-relaxed">
					تم إيقاف تشغيل الفيديو آلياً لحماية حقوق الملكية الفكرية لمنصة Handastech. يرجى إعادة ضبط المشغل للمتابعة بشكل نظامي.
				</p>
				<Button variant="solid" theme="danger" @click="resetTamperState">
					إعادة تفعيل المشغل
				</Button>
			</div>

			<!-- PLAY OVERLAY BUTTON -->
			<button
				type="button"
				v-if="!playing && !isTampered"
				:aria-label="__('Play video')"
				class="absolute inset-0 flex items-center justify-center cursor-pointer z-10"
				@click="playVideo"
			>
				<div class="video-play-scrim rounded-full p-4 ps-4.5">
					<Play :class="scrimInk" />
				</div>
			</button>

			<!-- TRANSPORT CONTROL BAR -->
			<div
				class="flex items-center gap-x-2 py-2 px-1 bg-gradient-to-b from-transparent to-black-overlay-700 absolute bottom-0 start-0 end-0 mx-auto rounded-5 z-20"
				:class="{
					'invisible group-hover:visible [@media(hover:none)]:visible': playing,
				}"
			>
				<Button
					variant="ghost"
					class="hover:bg-transparent"
					:label="playing ? __('Pause') : __('Play')"
					@click="togglePlay"
				>
					<template #icon>
						<Play v-if="!playing" class="size-4" :class="scrimInk" />
						<span v-else class="lucide-pause size-5" :class="scrimInk" />
					</template>
				</Button>

				<div class="relative flex items-center w-full flex-1 min-w-0">
					<input
						type="range"
						min="0"
						:max="duration"
						step="0.1"
						v-model="currentTime"
						@input="changeCurrentTime"
						:aria-label="__('Seek')"
						class="duration-slider h-1"
					/>
					<div class="absolute top-0 start-0 w-full h-full pointer-events-none">
						<div
							v-for="(quiz, index) in quizzes"
							:key="index"
							:style="getQuizMarkerStyle(quiz.time)"
							class="absolute top-0 h-full w-2 bg-surface-amber-3"
						></div>
					</div>
				</div>

				<span
					class="text-sm-medium shrink-0 whitespace-nowrap"
					:class="scrimInk"
				>
					{{ formatSeconds(currentTime) }} / {{ formatSeconds(duration) }}
				</span>

				<Dropdown :options="dropdownOptions">
					<Button>{{ playbackSpeedLabel }}</Button>
				</Dropdown>

				<Button
					variant="ghost"
					@click="toggleMute"
					:label="muted ? __('Unmute') : __('Mute')"
					class="hover:bg-transparent"
				>
					<template #icon>
						<span
							class="lucide-volume-2 size-5"
							:class="scrimInk"
							v-if="!muted"
						/>
						<span class="lucide-volume-x size-5" :class="scrimInk" v-else />
					</template>
				</Button>

				<Button
					variant="ghost"
					@click="toggleFullscreen"
					:label="__('Toggle fullscreen')"
					class="hover:bg-transparent"
				>
					<template #icon>
						<span class="lucide-maximize size-5" :class="scrimInk" />
					</template>
				</Button>
			</div>
		</div>

		<!-- QUIZ OVERLAY -->
		<Quiz
			v-if="showQuiz && !readOnly"
			:quiz="currentQuiz"
			@resume="resumeVideo"
		/>

		<!-- EDIT QUIZ MODAL -->
		<QuizInVideo
			v-model="showQuizModal"
			:quizzes="quizzes"
			:saveQuizzes="saveQuizzes"
			:duration="duration"
		/>

		<!-- QUIZ NOTIFICATION MODAL -->
		<Dialog v-model:open="showQuizLoader" size="sm" bare>
			<template #default>
				<div class="flex flex-col space-y-2 p-5 text-base leading-5">
					<span class="font-semibold">
						{{ __('Time for a Quiz') }}
					</span>
					<span>
						{{
							__(
								'Complete the upcoming quiz to continue watching the video. The quiz will open in {0} {1}.'
							).format(quizLoadTimer, quizLoadTimer === 1 ? 'second' : 'seconds')
						}}
					</span>
				</div>
			</template>
		</Dialog>
	</div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onBeforeUnmount, nextTick } from 'vue'
import { Button, Dialog, Dropdown, call } from 'frappe-ui'
import { formatSeconds, formatTimestamp } from '@/utils/format'
import { useSettings } from '@/stores/settings'
import { sessionStore } from '@/stores/session'
import Play from '@/components/Icons/Play.vue'
import Quiz from '@/components/Quiz.vue'
import QuizInVideo from '@/components/Modals/QuizInVideo.vue'
import { safeUrl } from '@/utils/safeUrl'

const scrimInk = 'text-white'

const videoRef = ref(null)
const videoContainer = ref(null)
const watermarkRef = ref(null)
let playing = ref(false)
let currentTime = ref(0)
let duration = ref(0)
let muted = ref(false)
const showQuizModal = ref(false)
const showQuiz = ref(false)
const showQuizLoader = ref(false)
const quizLoadTimer = ref(0)
const currentQuiz = ref(null)
const nextQuiz = ref({})
const { settings } = useSettings()
const session = sessionStore()

// HLS and Video Protection State
let hlsInstance = null
const isTampered = ref(false)
let tamperObserver = null
let driftTimer = null

const watermarkData = ref({
	user_id: '',
	full_name: '',
	email: '',
	ip: '',
	timestamp: '',
})

const watermarkStyle = ref({
	top: '14%',
	left: '16%',
	opacity: '0.35',
})

// Speed control states
const playbackSpeed = ref(1)
const playbackSpeedLabel = ref('1x')
const playbackSpeeds = [
	{ label: '0.5x', value: 0.5 },
	{ label: '1x', value: 1 },
	{ label: '1.5x', value: 1.5 },
	{ label: '2x', value: 2 },
]

const props = defineProps({
	file: {
		type: String,
		required: true,
	},
	type: {
		type: String,
		default: 'video/mp4',
	},
	readOnly: {
		type: Boolean,
		default: true,
	},
	quizzes: {
		type: Array,
		default: () => [],
	},
	saveQuizzes: {
		type: Function,
		default: () => {},
	},
})

const fileURL = computed(() => {
	return props.file
})

const isHls = computed(() => {
	return typeof props.file === 'string' && (props.file.includes('.m3u8') || props.file.includes('hls'))
})

onMounted(async () => {
	updateCurrentTime()
	updateNextQuiz()
	await setupWatermarkAndProtection()
	if (isHls.value) {
		await initHlsPlayer()
	} else if (videoRef.value) {
		videoRef.value.playbackRate = 1
	}
	startWatermarkDrift()
	startAntiTamperGuard()
})

onBeforeUnmount(() => {
	if (hlsInstance) {
		hlsInstance.destroy()
		hlsInstance = null
	}
	if (driftTimer) {
		clearInterval(driftTimer)
	}
	if (tamperObserver) {
		tamperObserver.disconnect()
	}
})

// Dynamic HLS.js Loader & Player
const loadHlsScript = () => {
	return new Promise((resolve) => {
		if (window.Hls) {
			resolve(window.Hls)
			return
		}
		const script = document.createElement('script')
		script.src = '/assets/builders/js/hls.min.js'
		script.onload = () => resolve(window.Hls)
		script.onerror = () => {
			const fallback = document.createElement('script')
			fallback.src = 'https://cdn.jsdelivr.net/npm/hls.js@1.5.17/dist/hls.min.js'
			fallback.onload = () => resolve(window.Hls)
			document.head.appendChild(fallback)
		}
		document.head.appendChild(script)
	})
}

const initHlsPlayer = async () => {
	const Hls = await loadHlsScript()
	if (!Hls || !videoRef.value) return

	if (Hls.isSupported()) {
		if (hlsInstance) {
			hlsInstance.destroy()
		}
		hlsInstance = new Hls({
			debug: false,
			enableWorker: true,
			xhrSetup: function (xhr) {
				xhr.withCredentials = true
			},
		})

		hlsInstance.loadSource(safeUrl(fileURL.value))
		hlsInstance.attachMedia(videoRef.value)

		hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
			if (videoRef.value) {
				duration.value = videoRef.value.duration || 0
			}
		})

		hlsInstance.on(Hls.Events.ERROR, (event, data) => {
			if (data.fatal) {
				switch (data.type) {
					case Hls.ErrorTypes.NETWORK_ERROR:
						hlsInstance.startLoad()
						break
					case Hls.ErrorTypes.MEDIA_ERROR:
						hlsInstance.recoverMediaError()
						break
					default:
						hlsInstance.destroy()
						break
				}
			}
		})
	} else if (videoRef.value.canPlayType('application/vnd.apple.mpegurl')) {
		// Native HLS for Safari iOS/macOS
		videoRef.value.src = safeUrl(fileURL.value)
	}
}

// Forensic Watermark Setup
const setupWatermarkAndProtection = async () => {
	try {
		const videoId = props.file.split('/').pop().replace('.m3u8', '').replace('.mp4', '') || 'handastech-video'
		const res = await call('builders.video_security.get_playback_session', {
			video_id: videoId,
		})
		if (res && res.watermark) {
			watermarkData.value = res.watermark
		}
	} catch (err) {
		// Graceful fallback to session data
		const user = session.user || 'student@handastech.sa'
		watermarkData.value = {
			user_id: user,
			full_name: user.split('@')[0],
			email: user,
			ip: 'Secure Session',
			timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
		}
	}
}

// Randomized Drift (Defeats Screen Cropping & static watermark blurs)
const startWatermarkDrift = () => {
	const zones = [
		{ top: '12%', left: '14%' },
		{ top: '14%', right: '14%' },
		{ top: '44%', left: '16%' },
		{ top: '46%', right: '18%' },
		{ bottom: '22%', left: '14%' },
		{ bottom: '24%', right: '16%' },
		{ top: '28%', left: '38%' },
		{ bottom: '38%', left: '34%' },
	]

	driftTimer = setInterval(() => {
		const nextZone = zones[Math.floor(Math.random() * zones.length)]
		watermarkStyle.value = {
			top: nextZone.top || 'auto',
			left: nextZone.left || 'auto',
			right: nextZone.right || 'auto',
			bottom: nextZone.bottom || 'auto',
			opacity: (0.24 + Math.random() * 0.12).toFixed(2),
		}
	}, 9000)
}

// Anti-Tamper Guard using MutationObserver
const startAntiTamperGuard = () => {
	if (!window.MutationObserver || !videoContainer.value) return

	tamperObserver = new MutationObserver(() => {
		if (isTampered.value) return

		let violated = false
		if (watermarkRef.value) {
			if (!videoContainer.value.contains(watermarkRef.value)) {
				violated = true
			} else {
				const cs = window.getComputedStyle(watermarkRef.value)
				if (
					cs.display === 'none' ||
					cs.visibility === 'hidden' ||
					parseFloat(cs.opacity) < 0.1 ||
					cs.filter.includes('blur')
				) {
					violated = true
				}
			}
		}

		if (violated) {
			isTampered.value = true
			if (videoRef.value) {
				videoRef.value.pause()
				playing.value = false
			}
		}
	})

	tamperObserver.observe(videoContainer.value, {
		childList: true,
		subtree: true,
		attributes: true,
		attributeFilter: ['style', 'class', 'hidden'],
	})
}

const resetTamperState = async () => {
	isTampered.value = false
	await nextTick()
	startAntiTamperGuard()
}

const updateCurrentTime = () => {
	setTimeout(() => {
		if (!videoRef.value) return
		videoRef.value.onloadedmetadata = () => {
			duration.value = videoRef.value.duration
		}
		videoRef.value.ontimeupdate = () => {
			currentTime.value = videoRef.value?.currentTime || currentTime.value
			if (currentTime.value >= nextQuiz.value.time) {
				videoRef.value.pause()
				playing.value = false
				videoRef.value.ontimeupdate = null
				currentQuiz.value = nextQuiz.value.quiz
				quizLoadTimer.value = 7
			}
		}
	}, 0)
}

watch(quizLoadTimer, () => {
	if (quizLoadTimer.value > 0) {
		showQuizLoader.value = true
		setTimeout(() => {
			quizLoadTimer.value -= 1
		}, 1000)
	} else {
		showQuizLoader.value = false
		showQuiz.value = true
	}
})

const resumeVideo = (restart = false) => {
	showQuiz.value = false
	currentQuiz.value = null
	updateCurrentTime()
	setTimeout(() => {
		if (!videoRef.value) return
		videoRef.value.currentTime = restart ? 0 : currentTime.value
		videoRef.value.play()
		playing.value = true
		updateNextQuiz()
	}, 0)
}

const updateNextQuiz = () => {
	if (!props.quizzes.length) return

	props.quizzes.forEach((quiz) => {
		if (typeof quiz.time == 'string' && quiz.time.includes(':')) {
			let time = quiz.time.split(':')
			let timeInSeconds = parseInt(time[0]) * 60 + parseInt(time[1])
			quiz.time = timeInSeconds
		}
	})

	props.quizzes.sort((a, b) => a.time - b.time)

	const nextQuizIndex = props.quizzes.findIndex(
		(quiz) => quiz.time > currentTime.value
	)
	if (nextQuizIndex !== -1) {
		nextQuiz.value = props.quizzes[nextQuizIndex]
	} else {
		nextQuiz.value = {}
	}
}

const playVideo = () => {
	if (isTampered.value || !videoRef.value) return
	videoRef.value.play()
	playing.value = true
}

const pauseVideo = () => {
	if (!videoRef.value) return
	videoRef.value.pause()
	playing.value = false
}

const togglePlay = () => {
	if (playing.value) {
		pauseVideo()
	} else {
		playVideo()
	}
}

const updateTime = () => {
	if (!videoRef.value) return
	currentTime.value = videoRef.value.currentTime
}

const videoEnded = () => {
	playing.value = false
}

const toggleMute = () => {
	if (!videoRef.value) return
	videoRef.value.muted = !videoRef.value.muted
	muted.value = videoRef.value.muted
}

const changeCurrentTime = () => {
	if (!videoRef.value) return
	if (
		settings.data?.prevent_skipping_videos &&
		currentTime.value > videoRef.value.currentTime
	)
		return
	videoRef.value.currentTime = currentTime.value
	updateNextQuiz()
}

const toggleFullscreen = () => {
	if (document.fullscreenElement) {
		document.exitFullscreen()
	} else if (videoContainer.value) {
		videoContainer.value.requestFullscreen()
	}
}

const getQuizMarkerStyle = (time) => {
	const percentage = ((time - 5) / Math.ceil(duration.value || 1)) * 100
	return {
		insetInlineStart: `${percentage}%`,
	}
}

const setPlaybackSpeed = (speed, label) => {
	playbackSpeed.value = speed
	playbackSpeedLabel.value = label
	if (videoRef.value) {
		videoRef.value.playbackRate = speed
	}
}

const dropdownOptions = computed(() =>
	playbackSpeeds.map((speed) => ({
		label: speed.label,
		selected: playbackSpeed.value === speed.value,
		onClick: () => setPlaybackSpeed(speed.value, speed.label),
	}))
)
</script>

<style scoped>
/* Container query layout per modern web guidance */
.ht-video-wrapper {
	width: 100%;
}

.video-block {
	container-type: inline-size;
	container-name: video-player;
	width: 100%;
	aspect-ratio: 16 / 9;
	margin: 0 auto;
}

.ht-watermark {
	transition: top 1.2s ease-in-out, left 1.2s ease-in-out, right 1.2s ease-in-out, bottom 1.2s ease-in-out, opacity 0.6s ease;
}

.ht-watermark-badge {
	font-size: clamp(10px, 1.6cqi, 13px);
}

.duration-slider {
	-webkit-appearance: none;
	appearance: none;
	border-radius: 10px;
	background-color: theme('colors.gray.600');
	cursor: pointer;
}

.duration-slider::-webkit-slider-thumb {
	width: 2px;
	border-radius: 50%;
	-webkit-appearance: none;
	background-color: theme('colors.white');
}

@media screen and (-webkit-min-device-pixel-ratio: 0) {
	input[type='range'] {
		overflow: hidden;
		width: 100%;
		-webkit-appearance: none;
	}

	input[type='range']::-webkit-slider-thumb {
		-webkit-appearance: none;
		cursor: pointer;
		box-shadow: -500px 0 0 500px theme('colors.white');
	}
}

.video-play-scrim {
	background: radial-gradient(
		circle,
		rgba(0, 0, 0, 0.4) 0%,
		rgba(0, 0, 0, 0.6) 60%
	);
}
</style>
