[app]
# (str) Title of your application
title = ChatbotWithImport

# (str) Package name
package.name = chatbot

# (str) Package domain (unique identifier, reverse domain style)
package.domain = org.chatbot.example

# (str) Source code where your .py files are located
source.dir = .

# (list) Include these file extensions in the APK
source.include_exts = py,txt,db

# (str) Application version
version = 1.0

# (list) Requirements from pip
requirements = python3,kivy,scikit-learn,numpy

# (str) Orientation of the app
orientation = portrait

# (bool) Fullscreen mode
fullscreen = 1

# (str) Entry point, default is main.py, but you can use:
# entrypoint = chatbot_with_import.py
# (optional - your file name must match manually)

[buildozer]
# (int) Verbosity level (0, 1, 2)
log_level = 2

# (bool) Warn if you're building as root (recommended: 1)
warn_on_root = 1

[android]
# (list) Permissions
android.permissions = INTERNET
