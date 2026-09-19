#!/usr/bin/env python3
"""Download the public LLMDrift repository for local replay (requires internet)."""
from pathlib import Path
from urllib.request import urlopen
import zipfile, io

OUT=Path(__file__).resolve().parents[1]/"data"/"llmdrift_repo"
URL="https://github.com/lchen001/LLMDrift/archive/refs/heads/main.zip"

def main():
    OUT.parent.mkdir(exist_ok=True)
    print("Downloading:",URL)
    with urlopen(URL, timeout=60) as r:
        data=r.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extractall(OUT.parent)
    print("Extracted under", OUT.parent)
    print("Look for generation/*.csv and adapt src/real_data.py for the chosen dataset.")

if __name__=="__main__": main()
