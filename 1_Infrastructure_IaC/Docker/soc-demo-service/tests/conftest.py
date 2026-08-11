import os
import sys

# Make ``main`` importable when tests run from the repo root. We add the app
# directory directly (rather than the service root) to avoid clashing with the
# unrelated ``GUI/app.py`` module that also lives on the test path.
APP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"
)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
