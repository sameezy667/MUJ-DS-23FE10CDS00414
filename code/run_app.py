"""
@file run_app.py
@description Launcher script for the Streamlit interactive dashboard
@module code
"""

import subprocess
import sys

if __name__ == "__main__":
    print("Launching Orto Streamlit Dashboard ...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
