import { defineComponent, ref } from 'vue'

export const showHelpModal = ref(false)
export const minimize = ref(false)

export function useOnboarding(key?: string) {
	return {
		updateOnboardingStep: (step?: any) => {},
		isOnboardingCompleted: () => true,
		steps: [],
		currentStep: null,
	}
}

export const HelpModal = defineComponent({
	name: 'HelpModal',
	props: ['modelValue', 'articles', 'appName', 'title', 'logo', 'afterSkip', 'afterSkipAll', 'afterReset', 'afterResetAll', 'docsLink'],
	setup() {
		return () => null
	}
})

export const GettingStartedBanner = defineComponent({
	name: 'GettingStartedBanner',
	setup() {
		return () => null
	}
})

export const IntermediateStepModal = defineComponent({
	name: 'IntermediateStepModal',
	props: ['modelValue', 'currentStep'],
	setup() {
		return () => null
	}
})
