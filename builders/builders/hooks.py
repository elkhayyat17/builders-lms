import frappe

from . import __version__ as app_version

app_name = "builders"
app_title = "Handastech"
app_publisher = "Handastech Team"
app_description = "Handastech - Engineering & Tech Solutions LMS Platform"
app_icon = "octicon octicon-tools"
app_color = "#0066CC"
app_email = "info@handastech.sa"
app_license = "MIT"
required_apps = ["lms"]

# Fixtures — export category seed data and custom fields
fixtures = [
    {
        "dt": "LMS Category",
        "filters": [],
    },
    {
        "dt": "Custom Field",
        "filters": [
            ["module", "=", "Builders"],
        ],
    },
]

# --------------------------------------------------------------------------
# Includes in <head>
# --------------------------------------------------------------------------

# CSS injected into every web page (portal / website)
web_include_css = [
    "/assets/builders/css/builders-theme.css",
    "/assets/builders/css/builders-rtl.css",
]

# JS injected into every web page
web_include_js = [
    "/assets/builders/js/language-toggle.js",
]

# --------------------------------------------------------------------------
# Installation hooks
# --------------------------------------------------------------------------

after_install = "builders.setup.after_install"
after_migrate = "builders.setup.after_install"

# --------------------------------------------------------------------------
# Jinja helpers — extend LMS templates with builders utilities
# --------------------------------------------------------------------------

jinja = {
    "methods": [
        "builders.utils.get_featured_courses",
        "builders.utils.get_categories_with_count",
    ],
}

# --------------------------------------------------------------------------
# Website context — inject builders variables into website context
# --------------------------------------------------------------------------

update_website_context = [
    "builders.utils.update_website_context",
]
