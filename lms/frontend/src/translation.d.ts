import type { App, Ref } from 'vue'

export const translations: Ref<Record<string, string>>
export function translate(message: string): any
export default function translationPlugin(app: App): void
