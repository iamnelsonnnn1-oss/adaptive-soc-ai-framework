"""Shared pytest fixtures for the GUI service unit tests.

Streamlit reads ``st.secrets`` lazily from a ``secrets.toml`` file and raises
``StreamlitSecretNotFoundError`` when no such file exists. The GUI modules touch
``st.secrets`` at import time, so we replace it with a plain dict for the whole
test session to keep imports deterministic and file-system independent.
"""

import streamlit as st

# Replace the lazy Secrets object with a plain mapping so ``.get`` never raises
# and never depends on a real secrets.toml being present on disk.
st.secrets = {}
