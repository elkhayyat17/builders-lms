import { defineComponent, h } from 'vue'

export const DataImport = defineComponent({
  name: 'DataImport',
  props: ['doctype', 'importName', 'doctypeMap'],
  setup() {
    return () => h('div', { class: 'data-import-placeholder' }, 'Data Import')
  }
})
