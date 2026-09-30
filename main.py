"""
Secure Image Encryption Using 5D Hyper-chaotic Keystream and 3D Pixel Scrambling
==================================================================================
Run this file in VS Code (or any terminal) to encrypt an image, decrypt it
back, and print/plot the Phase-1 performance-evaluation metrics
(NPCR, UACI, Entropy, PSNR, SSIM).

Usage
-----
    python main.py --image path/to/your_image.jpg --key "MySecretKey123"

If you omit --image, a built-in sample photo (skimage's "astronaut") is used
so the script runs immediately with zero setup.

Outputs (written to the ./output folder):
    original.png, cipher.png, decrypted.png, histograms.png, summary.png
"""

from __future__ import annotations

import argparse
import os
import sys

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")  # safe for headless runs; VS Code will still show saved PNGs
import matplotlib.pyplot as plt

from chaos_image_cipher import IMG_SIZE, encrypt_image, decrypt_image
import metrics as M


def load_image(path: str | None) -> np.ndarray:
    """Load an image as BGR uint8 and resize to IMG_SIZE x IMG_SIZE.
    Falls back to a bundled sample photo if no path is given / file missing.
    """
    if path and os.path.isfile(path):
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Could not read image at: {path}")
    else:
        if path:
            print(f'[!] Could not find "{path}" — using the built-in sample image instead.')
        else:
            print("[i] No --image given — using the built-in sample image.")
        from skimage import data
        rgb = data.astronaut()  # 512x512x3 RGB sample image, ships with scikit-image
        img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)
    return img.astype(np.uint8)


def flip_one_pixel(img: np.ndarray) -> np.ndarray:
    """Return a copy of img with the least-significant bit of one pixel
    flipped — used for the NPCR / UACI differential-attack test.
    """
    modified = img.copy()
    modified[0, 0, 0] ^= 1
    return modified


def save_side_by_side(original, cipher, decrypted, out_path):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
    for ax, img, title in zip(
        axes, [original, cipher, decrypted], ["Original", "Encrypted (Cipher)", "Decrypted"]
    ):
        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        ax.set_title(title)
        ax.axis("off")
    fig.suptitle("Secure Image Encryption — 5D Hyper-chaotic Keystream + 3D Pixel Scrambling")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def save_histograms(original, cipher, out_path):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, img, title in zip(axes, [original, cipher], ["Original histogram", "Cipher histogram"]):
        colors = ("b", "g", "r")
        for c, col in enumerate(colors):
            hist = cv2.calcHist([img], [c], None, [256], [0, 256]).flatten()
            ax.plot(hist, color=col, linewidth=0.8)
        ax.set_title(title)
        ax.set_xlim(0, 255)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="5D Hyper-chaotic + 3D Pixel Scrambling image cipher demo")
    parser.add_argument("--image", type=str, default=None, help="Path to an input image (any size/format)")
    parser.add_argument("--key", type=str, default="EWCE-CSE-Phase1-DemoKey", help="Secret key / passphrase")
    parser.add_argument("--outdir", type=str, default="output", help="Folder to write results into")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    print("=" * 70)
    print(" Secure Image Encryption — 5D Hyper-chaotic Keystream")
    print(" + 3D Pixel Scrambling")
    print("=" * 70)

    # Step 1: Input Image ---------------------------------------------------
    original = load_image(args.image)
    print(f"[1] Loaded image, resized to {original.shape[1]}x{original.shape[0]}")

    # Steps 2-6: Encrypt ------------------------------------------------------
    print("[2-6] Encrypting (2D->3D, 5D keystream, Fisher-Yates scramble, chained diffusion)...")
    cipher = encrypt_image(original, args.key)

    # Step 7: Decrypt -----------------------------------------------------
    print("[7] Decrypting with the same secret key...")
    decrypted = decrypt_image(cipher, args.key)

    lossless = np.array_equal(original, decrypted)
    print(f"    Lossless recovery: {'YES ' if lossless else 'NO '}")

    # Wrong-key sanity check ------------------------------------------------
    wrong_key_decrypt = decrypt_image(cipher, args.key + "x")
    wrong_key_matches = np.array_equal(original, wrong_key_decrypt)
    print(f"    Decryption with a WRONG key reproduces the original: {wrong_key_matches} (should be False)")

    # Step 9: Performance Evaluation ----------------------------------------
    print("\n[9] Performance evaluation")
    print("-" * 70)

    entropy_plain = M.shannon_entropy(original)
    entropy_cipher = M.shannon_entropy(cipher)
    print(f"  Entropy  original : {entropy_plain:.4f} bits/pixel  (ideal max = 8.0)")
    print(f"  Entropy  cipher   : {entropy_cipher:.4f} bits/pixel  (closer to 8.0 = better)")

    psnr_orig_cipher = M.psnr(original, cipher)
    psnr_orig_decrypted = M.psnr(original, decrypted)
    print(f"  PSNR original vs cipher    : {psnr_orig_cipher:.4f} dB  (lower = better encryption)")
    print(f"  PSNR original vs decrypted : {psnr_orig_decrypted if psnr_orig_decrypted != float('inf') else 'inf'} dB  (should be very high / infinite)")

    ssim_orig_cipher = M.ssim(original, cipher)
    ssim_orig_decrypted = M.ssim(original, decrypted)
    print(f"  SSIM  original vs cipher    : {ssim_orig_cipher:.4f}  (closer to 0 = better encryption)")
    print(f"  SSIM  original vs decrypted : {ssim_orig_decrypted:.4f}  (should be 1.0)")

    # Differential attack resistance: NPCR / UACI between two ciphers
    # produced from plaintexts differing by a single pixel.
    original_plus_one = flip_one_pixel(original)
    cipher_plus_one = encrypt_image(original_plus_one, args.key)
    npcr_val = M.npcr(cipher, cipher_plus_one)
    uaci_val = M.uaci(cipher, cipher_plus_one)
    print(f"  NPCR (1-pixel change test) : {npcr_val:.4f} %   (ideal ~99.6094%)")
    print(f"  UACI (1-pixel change test) : {uaci_val:.4f} %   (ideal ~33.4635%)")
    print("-" * 70)

    # Save images + plots -----------------------------------------------------
    cv2.imwrite(os.path.join(args.outdir, "original.png"), original)
    cv2.imwrite(os.path.join(args.outdir, "cipher.png"), cipher)
    cv2.imwrite(os.path.join(args.outdir, "decrypted.png"), decrypted)
    save_side_by_side(original, cipher, decrypted, os.path.join(args.outdir, "summary.png"))
    save_histograms(original, cipher, os.path.join(args.outdir, "histograms.png"))

    print(f"\nSaved images and plots to: {os.path.abspath(args.outdir)}")
    print("  - original.png, cipher.png, decrypted.png")
    print("  - summary.png      (side-by-side comparison)")
    print("  - histograms.png   (pixel-value distribution, original vs cipher)")


if __name__ == "__main__":
    sys.exit(main())
