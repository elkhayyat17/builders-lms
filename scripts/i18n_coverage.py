"""Arabic translation coverage audit for the LMS SPA + builders app.

Run inside the bench container:
    cd /home/frappe/frappe-bench/sites && ../env/bin/python ../apps/builders/../../apps/lms/../builders/scripts/i18n_coverage.py
or simply:
    ../env/bin/python /tmp/i18n_coverage.py [site] [--json out.json]

Reports:
  * keys used in __() across frontend that have NO Arabic translation
  * keys that themselves contain Arabic (break the English UI)
  * bilingual "عربي / English" keys
"""
import json
import os
import re
import sys

ARABIC = re.compile(r"[\u0600-\u06FF]")
KEY_RE = re.compile(r"""__\(\s*(['"`])((?:\\.|(?!\1).)*?)\1\s*[\),]""", re.S)

SCAN_DIRS = [
	"/home/frappe/frappe-bench/apps/lms/frontend/src",
]
EXTS = (".vue", ".js", ".ts")


def extract_keys():
	keys = {}
	for base in SCAN_DIRS:
		for root, _dirs, files in os.walk(base):
			if "node_modules" in root or "/tests" in root:
				continue
			for f in files:
				if not f.endswith(EXTS):
					continue
				path = os.path.join(root, f)
				with open(path, encoding="utf-8", errors="ignore") as fh:
					text = fh.read()
				for m in KEY_RE.finditer(text):
					key = m.group(2)
					if m.group(1) == "`" and "${" in key:
						continue
					key = key.replace("\\'", "'").replace('\\"', '"')
					keys.setdefault(key, set()).add(os.path.relpath(path, base))
	return keys


def main():
	site = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "lms.localhost"
	out = None
	if "--json" in sys.argv:
		out = sys.argv[sys.argv.index("--json") + 1]

	import frappe
	from frappe.translate import get_all_translations

	os.chdir("/home/frappe/frappe-bench/sites")
	frappe.init(site=site)
	frappe.connect()
	frappe.cache.delete_key("merged_translations")
	tr = get_all_translations("ar")

	keys = extract_keys()
	missing, arabic_keys, bilingual = [], [], []
	for k, files in sorted(keys.items()):
		if ARABIC.search(k):
			(bilingual if "/" in k and re.search(r"[A-Za-z]", k) else arabic_keys).append((k, sorted(files)))
			continue
		if not re.search(r"[A-Za-z]", k):
			continue
		if not tr.get(k):
			missing.append((k, sorted(files)))

	total = len([k for k in keys if re.search(r"[A-Za-z]", k) and not ARABIC.search(k)])
	print(f"Total English keys: {total}")
	print(f"Translated to Arabic: {total - len(missing)}  ({(total - len(missing)) * 100 / max(total, 1):.1f}%)")
	print(f"Missing Arabic: {len(missing)}")
	print(f"Arabic-only keys (break English UI): {len(arabic_keys)}")
	print(f"Bilingual 'ar / en' keys: {len(bilingual)}")
	if out:
		with open(out, "w", encoding="utf-8") as fh:
			json.dump(
				{"missing": missing, "arabic_keys": arabic_keys, "bilingual": bilingual},
				fh,
				ensure_ascii=False,
				indent=1,
			)
		print(f"Details written to {out}")
	frappe.destroy()


if __name__ == "__main__":
	main()
