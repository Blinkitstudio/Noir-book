"""Detecta chirridos: imprime los instantes (cada 0.25 s) donde la energía por encima de 6 kHz supera el 8 %.
Uso: python3 chequeo_agudos.py video.mp4   → salida vacía = audio limpio."""
import subprocess, sys
import numpy as np

a = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-ac', '1', '-ar', '32000', '-f', 's16le', '-'], capture_output=True).stdout
x = np.frombuffer(a, np.int16) / 32768; sr = 32000; N = 2048
out = []
for i in range(0, len(x) - N, sr // 4):
    f = np.abs(np.fft.rfft(x[i:i + N] * np.hanning(N))); fr = np.fft.rfftfreq(N, 1 / sr)
    out.append((i / sr, f[fr > 6000].sum() / (f.sum() + 1e-9)))
print(' '.join(f'{t:.1f}:{h:.2f}' for t, h in out if h > 0.08))
