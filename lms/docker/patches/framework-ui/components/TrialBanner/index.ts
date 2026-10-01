import { defineComponent } from 'vue'

export const TrialBanner = defineComponent({
  name: 'TrialBanner',
  props: ['collapsed'],
  setup() {
    return () => null
  }
})
