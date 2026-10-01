#!/bin/bash
set -e

BENCH_DIR="/home/frappe/frappe-bench"
PATCHES_DIR="/workspace/lms/docker/patches"

echo "==> Applying @framework/ui stubs to $BENCH_DIR/apps/frappe/ui/src..."
mkdir -p "$BENCH_DIR/apps/frappe/ui/src/telemetry"
mkdir -p "$BENCH_DIR/apps/frappe/ui/src/components/Onboarding"
mkdir -p "$BENCH_DIR/apps/frappe/ui/src/components/TrialBanner"
mkdir -p "$BENCH_DIR/apps/frappe/ui/src/components/DataImport"

cp "$PATCHES_DIR/framework-ui/telemetry/index.ts" "$BENCH_DIR/apps/frappe/ui/src/telemetry/index.ts"
cp "$PATCHES_DIR/framework-ui/components/Onboarding/index.ts" "$BENCH_DIR/apps/frappe/ui/src/components/Onboarding/index.ts"
cp "$PATCHES_DIR/framework-ui/components/TrialBanner/index.ts" "$BENCH_DIR/apps/frappe/ui/src/components/TrialBanner/index.ts"
cp "$PATCHES_DIR/framework-ui/components/DataImport/index.ts" "$BENCH_DIR/apps/frappe/ui/src/components/DataImport/index.ts"

CODE_EDITOR_INDEX="$BENCH_DIR/apps/lms/frontend/node_modules/frappe-ui/src/molecules/code-editor/index.ts"
if [ -f "$CODE_EDITOR_INDEX" ]; then
    if ! grep -q "CodePreview" "$CODE_EDITOR_INDEX"; then
        echo "export { default as CodePreview } from './CodeEditor.vue'" >> "$CODE_EDITOR_INDEX"
        echo "==> Added CodePreview export to frappe-ui code-editor index.ts"
    fi
fi

echo "==> All patches successfully applied!"
