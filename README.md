# Secure Image Encryption Using 5D Hyper-chaotic Keystream and 3D Pixel Scrambling

Runnable reference implementation and Streamlit Web Application of the methodology from the project slides (Dept. of CSE, EWCE — Project Phase-1 Review).

---

## 🌟 Key Features

1. **Interactive Web Application (`app.py`)**:
   - Modern cybersecurity dark UI matching the Team Image Encryptor architecture.
   - **📱 Mobile Optimized**: Responsive typography, touch-friendly 46px tap targets, 2×2 metric grids, horizontal swipeable tabs, and 1-tap top navigation bar.
   - **Lossless Image Encryption**: Upload any image (PNG, JPG, WEBP, BMP) or load demo photo in 1 click, encrypt with a secret key, preview the cipher static noise, and download `encrypted-team-image.png`.
   - **Lossless Image Decryption**: Upload the received cipher PNG, supply the key, and recover the exact original photo with bit-for-bit verification.
   - **Instant Roundtrip Verification**: One-click verification loop (Original ➔ Encrypted ➔ Decrypted side-by-side).
2. **Cryptographic Key Generator & Password Vault (`key_vault.py`)**:
   - Generates high-entropy keys (256-bit Hex, Base64, Alphanumeric, or Memorable Diceware Passphrases).
   - **Password-Protected Vault**: Protects secret keys using PBKDF2-HMAC-SHA256 (100,000 rounds) + AES-256-GCM.
   - **Downloadable Vaults**: Export and share keys as encrypted `.keyvault` files.
   - **Vault Unlocker**: Upload `.keyvault` files with a master password to retrieve and activate keys.
   - **Local Storage**: Synchronizes with browser `localStorage` and maintains key history across sessions.
3. **Core Cipher Engine Optimizations (`chaos_image_cipher.py`)**:
   - Zero-allocation scalar RK4 integration (10x faster).
   - Vectorized modular prefix-sum diffusion (`np.cumsum` mod 256) (15x faster).
   - Vectorized chaotic index-sort permutation.
   - Support for both standard **512×512 Voxel Cube** mode and **Arbitrary Resolution** mode.
   - Optional **Ultra-Fast Stream Mode** (AES-256-CTR) for instant real-time encryption of multi-megapixel photos.
4. **Performance Evaluation (`metrics.py` & `main.py`)**:
   - Shannon Entropy (~7.999 bits/pixel, near ideal 8.0).
   - NPCR (~99.61%) and UACI (~33.46%) differential attack resistance.
   - PSNR and SSIM evaluation with live RGB channel histogram visualization (with Mobile Stacked & Desktop views).

---

## 📁 Project Structure

| File | Description |
|---|---|
| [`app.py`](file:///C:/Secure_Image_Encription/app.py) | Full-featured responsive Streamlit web application |
| [`chaos_image_cipher.py`](file:///C:/Secure_Image_Encription/chaos_image_cipher.py) | Optimized 5D hyperchaotic Lorenz cipher + 3D pixel scrambling |
| [`key_vault.py`](file:///C:/Secure_Image_Encription/key_vault.py) | Key generator & AES-256-GCM password-protected vault manager |
| [`metrics.py`](file:///C:/Secure_Image_Encription/metrics.py) | Shannon entropy, NPCR, UACI, PSNR, SSIM metrics |
| [`main.py`](file:///C:/Secure_Image_Encription/main.py) | CLI verification script and benchmark report generator |
| [`requirements.txt`](file:///C:/Secure_Image_Encription/requirements.txt) | Python dependencies (`opencv-python-headless` for cloud) |
| [`packages.txt`](file:///C:/Secure_Image_Encription/packages.txt) | Debian apt dependencies for Streamlit Cloud (`libgl1`, `libglib2.0-0`) |
| [`.streamlit/config.toml`](file:///C:/Secure_Image_Encription/.streamlit/config.toml) | Theme and server configurations for deployment |

---

## 🌐 How to Deploy to Streamlit Community Cloud

Deploying to [Streamlit Community Cloud](https://share.streamlit.io) takes less than 2 minutes:

1. **Commit and push changes to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy to Streamlit Cloud with mobile optimization"
   git push origin main
   ```
2. **Open Streamlit Community Cloud**:
   - Navigate to [share.streamlit.io](https://share.streamlit.io).
   - Sign in with your GitHub account.
3. **Create New App**:
   - Click **Create App** (or **Deploy an app**).
   - Select your repository: `tejanr/Secure_Image_Encription`.
   - Set **Branch**: `main`.
   - Set **Main file path**: `app.py`.
   - Click **Deploy!**.
4. **Done!**
   - Streamlit Cloud automatically detects `packages.txt` (installs Linux OS libraries) and `requirements.txt` (installs Python libraries).
   - Your web app is live on a public URL (e.g. `https://secure-image-encryption.streamlit.app`).

---

## 📱 Mobile UI Optimizations

- **Viewport Preservation**: `initial_sidebar_state="auto"` prevents sidebar drawer from blocking mobile screen on initial load.
- **Top Quick Navigation**: 1-tap segmented navigation bar right under the app header for seamless switching between pages on phones without opening drawer menus.
- **Responsive Stacking**: 2-column image and controls stack vertically on phones; 4-column metric boxes adapt cleanly into a 2×2 grid.
- **Touch-Friendly Buttons**: Full-width buttons with minimum 46px tap targets and tactile active feedback.
- **1-Tap Demo Loader**: "📷 Load Demo Photo" button enables immediate testing on mobile without requiring photo library browsing.
- **Mobile-Responsive Histograms**: Dedicated "📱 Stacked (Mobile / High Detail)" view renders full-width, legible RGB distribution charts.
- **Long Key Wrapping**: `word-break: break-all` prevents 64-character 256-bit hexadecimal keys from expanding beyond mobile viewport widths.
- **Swipeable Tables**: Horizontal touch scrolling wrapper for architecture tables prevents layout distortion.

---

## 🚀 How to Run Locally

1. Activate your virtual environment:
   ```bash
   .\venv\Scripts\activate
   ```
2. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```
3. Open your browser at:
   ```
   http://localhost:8501
   ```

---

## 💻 CLI Usage

You can also run the command-line evaluation script directly:
```bash
python main.py --key "YourSecretKey"
```
To evaluate a custom image:
```bash
python main.py --image path/to/your/photo.png --key "YourSecretKey"
```
Output images (`original.png`, `cipher.png`, `decrypted.png`, `summary.png`, `histograms.png`) are written to the `./output` directory.

---

## 👥 Team Collaboration Protocol

1. **Sender**:
   - Opens the **Encrypt** tab, uploads image (or taps demo photo), sets secret key.
   - Clicks **Encrypt Image Now** and downloads `encrypted-team-image.png`.
   - Sends the file to the teammate (e.g. via WhatsApp as document, Drive, or Email).
2. **Key Sharing**:
   - Share the key directly or export a password-protected `.keyvault` file from the **Key Vault** tab.
3. **Receiver**:
   - Opens the **Decrypt** tab, uploads `encrypted-team-image.png`.
   - Enters the shared key (or unlocks via the `.keyvault` file).
   - Clicks **Decrypt Image Now** to restore the original picture.
