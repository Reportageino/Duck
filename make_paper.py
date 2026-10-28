"""Generate a seamless kraft-paper texture (assets/backgrounds/paper.jpg).
Colour and grain statistics are sampled from the photographed drawings."""
import numpy as np, sys
from PIL import Image
rng = np.random.default_rng(7)
N = 512
src = np.asarray(Image.open(sys.argv[1]).convert('RGB').crop((40, 20, 552, 276))).astype(float)
base = src.reshape(-1, 3).mean(0) * np.array([0.96, 0.95, 0.93])
def tile_noise(sigma):  # periodic (seamless) band-limited noise via FFT
    f = np.fft.fft2(rng.standard_normal((N, N)))
    ky = np.fft.fftfreq(N)[:, None]; kx = np.fft.fftfreq(N)[None, :]
    k = np.sqrt(kx**2 + ky**2)
    n = np.real(np.fft.ifft2(f * np.exp(-(k * sigma) ** 2)))
    return n / n.std()
lum = 0.55 * tile_noise(3) + 0.35 * tile_noise(1.2) + 0.25 * tile_noise(30)
img = base[None, None, :] + lum[..., None] * np.array([13.0, 11.5, 10.0])
# fibres: short slightly lighter / darker strokes (wrapped => seamless)
for _ in range(1400):
    x, y = rng.integers(0, N, 2); a = rng.uniform(0, np.pi); L = rng.integers(4, 14)
    c = rng.choice([-14, 12]) * rng.uniform(0.4, 1)
    for t in range(L):
        img[int(y + np.sin(a) * t) % N, int(x + np.cos(a) * t) % N] += c
# dark speckles
for _ in range(90):
    x, y = rng.integers(0, N, 2); r = rng.uniform(0.6, 1.6)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx * dx + dy * dy <= r * r: img[(y + dy) % N, (x + dx) % N] = img[(y + dy) % N, (x + dx) % N] * 0.45
img = np.clip(img, 0, 255).astype(np.uint8)
Image.fromarray(img).save(sys.argv[2], quality=86)
print('paper base colour', base.round())
