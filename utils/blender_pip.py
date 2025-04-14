import sys
import subprocess
import os
try:
    from PIL import Image
except:
    python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    # upgrade pip
    subprocess.call([python_exe, "-m", "ensurepip"])
    subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
    # install required packages
    subprocess.call([python_exe, "-m", "pip", "install", "pillow"])