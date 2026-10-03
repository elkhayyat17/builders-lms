import { ref } from 'vue'
import { createResource } from 'frappe-ui'

export const translations = ref(window.translatedMessages || {})

export default function translationPlugin(app) {
	app.config.globalProperties.__ = translate
	window.__ = translate
	if (window.translatedMessages) {
		translations.value = window.translatedMessages
	}
	if (!window.translatedMessages) {
		fetchTranslations()
	}
}

export function translate(message) {
	if (!message) return ''
	let dict = (translations.value && Object.keys(translations.value).length > 0)
		? translations.value
		: (window.translatedMessages || {})
	let translatedMessage = dict[message] || message

	const hasPlaceholders = /{\d+}/.test(message)
	if (!hasPlaceholders) {
		return translatedMessage
	}
	return {
		format: function (...args) {
			return translatedMessage.replace(
				/{(\d+)}/g,
				function (match, number) {
					return typeof args[number] !== 'undefined'
						? args[number]
						: match
				}
			)
		},
		toString: function () {
			return translatedMessage
		},
	}
}

function fetchTranslations() {
	if (typeof createResource !== 'function') return
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
