path = '/home/frappe/frappe-bench/apps/lms/frontend/node_modules/frappe-ui/src/molecules/code-editor/index.ts'
content = open(path).read()
# Remove all CodePreview exports
content = content.replace("export { default as CodePreview } from './CodeEditor.vue'\n", "")
content = content.replace("export { default as CodePreview } from './CodeEditor.vue'", "")
# Add exactly one export
content = content.strip() + "\nexport { default as CodePreview } from './CodeEditor.vue'\n"
with open(path, 'w') as f:
    f.write(content)
print("deduped and patched cleanly")
