"""
Performance Evaluation metrics (Step 9 of the methodology slide):
NPCR, UACI, Shannon entropy, PSNR, and SSIM.
"""

from __future__ import annotations

import numpy as np
from skimage.metrics import structural_similarity as sk_ssim


def npcr(img1: np.ndarray, img2: np.ndarray) -> float:
    """Number of Pixels Change Rate (%). Compares two same-sized images
    (typically two cipher images produced from two plaintexts that differ
    by a single pixel). ~99.6% is considered strong resistance to
    differential attacks for 8-bit images.
    """
    diff = (img1 != img2)
    return 100.0 * np.count_nonzero(diff) / diff.size


def uaci(img1: np.ndarray, img2: np.ndarray) -> float:
    """Unified Average Changing Intensity (%). ~33% is the ideal reference
    value for 8-bit images.
    """
    a = img1.astype(np.float64)
    b = img2.astype(np.float64)
    return 100.0 * np.mean(np.abs(a - b)) / 255.0


def shannon_entropy(img: np.ndarray) -> float:
    """Shannon entropy in bits (per channel, averaged). A fully random 8-bit
    channel has entropy 8.0; a good cipher image should sit very close to 8.
    """
    if img.ndim == 2:
        img = img[:, :, None]
    entropies = []
    for c in range(img.shape[2]):
        hist, _ = np.histogram(img[:, :, c], bins=256, range=(0, 256))
        p = hist / hist.sum()
        p = p[p > 0]
        entropies.append(-np.sum(p * np.log2(p)))
    return float(np.mean(entropies))


def psnr(img1: np.ndarray, img2: np.ndarray) -> float:
    """Peak Signal-to-Noise Ratio (dB). High (e.g. > 40 dB, or inf) between
    original and decrypted image is what you want (lossless recovery). Low
    (e.g. < 10 dB) between original and cipher image indicates strong
    encryption.
    """
    a = img1.astype(np.float64)
    b = img2.astype(np.float64)
    mse = np.mean((a - b) ** 2)
    if mse == 0:
        return float("inf")
    return 20.0 * np.log10(255.0 / np.sqrt(mse))


def ssim(img1: np.ndarray, img2: np.ndarray) -> float:
    """Structural Similarity Index. ~1.0 between original and decrypted
    (identical), close to 0 between original and cipher (structurally
    unrelated).
    """
    return float(sk_ssim(img1, img2, channel_axis=2))
