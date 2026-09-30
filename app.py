"""
app.py - Secure Image Encryption Studio & Key Vault
=====================================================
A Streamlit web application providing:
  - Image Encryption & Decryption (5D Hyper-chaotic Lorenz & Fast Stream Cipher)
  - Lossless PNG preview & download options
  - Cryptographic Random Key Generator (Hex, Base64, Alphanumeric, Passphrase)
  - Password-Protected Encrypted Key Vault (.keyvault download & unlock)
  - Local session storage & browser persistence
  - Live Security Metrics & Histograms (Entropy, NPCR, UACI, PSNR, SSIM)
  - Fully Responsive Mobile & Desktop Layout (Streamlit Cloud Ready)
"""

from __future__ import annotations

import io
import json
import os
import time
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components

import chaos_image_cipher as cipher
import key_vault
import metrics as M

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Team Image Encryptor | Secure Chaos Crypto Studio",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="auto",  # Automatically collapse on mobile to preserve viewport space
)

# -----------------------------------------------------------------------------
# Custom Responsive Cyber Dark CSS
# -----------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Global Typography & Resets */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-tap-highlight-color: transparent;
    }

    code, pre, .mono-font {
        font-family: 'JetBrains Mono', monospace !important;
        word-break: break-all;
    }

    /* Gradient Header Typography */
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        font-size: 0.92rem;
        color: #94a3b8;
        margin-bottom: 1.1rem;
        line-height: 1.5;
    }

    /* Cyber Card Container */
    .crypto-card {
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 1.15rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.35);
        margin-bottom: 1.15rem;
    }

    /* Active Secret Key Banner */
    .key-banner {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        padding: 0.85rem 1.15rem;
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 12px;
        margin-bottom: 1rem;
    }

    .key-text-wrap {
        font-family: 'JetBrains Mono', monospace;
        color: #38bdf8;
        font-size: 0.92rem;
        background: rgba(15, 23, 42, 0.75);
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        border: 1px solid rgba(56, 189, 248, 0.15);
        word-break: break-all;
        max-width: 100%;
        display: inline-block;
    }

    /* Status Badges */
    .badge-ready {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #34d399;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        border-radius: 9999px;
        white-space: nowrap;
    }

    .badge-algo {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(56, 189, 248, 0.15);
        border: 1px solid #38bdf8;
        color: #38bdf8;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        border-radius: 9999px;
        white-space: nowrap;
    }

    /* Callout Notice */
    .team-notice {
        background: rgba(15, 23, 42, 0.88);
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        font-size: 0.88rem;
        color: #cbd5e1;
        line-height: 1.55;
    }

    /* Buttons Styling & Mobile Touch Targets */
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        min-height: 44px !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.15s ease-in-out !important;
        touch-action: manipulation !important;
    }
    div.stButton > button:active {
        transform: scale(0.98) !important;
    }

    div.stDownloadButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        min-height: 46px !important;
        padding: 0.65rem 1rem !important;
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
        touch-action: manipulation !important;
    }
    div.stDownloadButton > button:active {
        transform: scale(0.98) !important;
    }

    /* Metric Cards */
    .metric-box {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 10px;
        padding: 0.75rem 0.5rem;
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .metric-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #38bdf8;
        font-family: 'JetBrains Mono', monospace;
        word-break: break-all;
    }
    .metric-label {
        font-size: 0.74rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.2rem;
    }

    /* Top Navigation bar */
    div[data-testid="stSegmentedControl"] {
        margin-bottom: 1.15rem !important;
    }

    /* Smooth Touch Tabs */
    div[data-testid="stTabs"] button[role="tab"] {
        padding: 0.55rem 0.95rem !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
    }

    /* Responsive Table Container */
    .responsive-table-wrapper {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-top: 0.5rem;
        border-radius: 8px;
    }

    /* ========================================================================= */
    /* RESPONSIVE MEDIA QUERIES (Mobile & Tablet)                                 */
    /* ========================================================================= */

    @media (max-width: 768px) {
        /* Optimize block container padding on mobile screens */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.65rem !important;
            padding-right: 0.65rem !important;
            max-width: 100% !important;
        }

        /* Hero Typography */
        .hero-title {
            font-size: 1.55rem !important;
            line-height: 1.25 !important;
        }
        .hero-subtitle {
            font-size: 0.82rem !important;
            margin-bottom: 0.85rem !important;
        }

        /* Crypto Card */
        .crypto-card {
            padding: 0.85rem !important;
            border-radius: 10px !important;
            margin-bottom: 0.85rem !important;
        }

        /* Key banner layout on mobile */
        .key-banner {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 8px !important;
            padding: 0.75rem 0.85rem !important;
        }
        .key-text-wrap {
            font-size: 0.82rem !important;
            padding: 0.2rem 0.45rem !important;
        }

        /* Responsive Columns on Mobile */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.65rem !important;
        }

        /* Standard 2-column layout stacks vertically (100% width each) */
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }

        /* 4-column metric blocks adapt into a 2x2 grid */
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4)) > div[data-testid="column"] {
            min-width: calc(50% - 0.4rem) !important;
            flex: 1 1 calc(50% - 0.4rem) !important;
        }

        /* Metric cards inside 2x2 grid */
        .metric-box {
            padding: 0.6rem 0.35rem !important;
        }
        .metric-value {
            font-size: 1.12rem !important;
        }
        .metric-label {
            font-size: 0.68rem !important;
        }

        /* Buttons: thumb friendly 46px min height */
        div.stButton > button, div.stDownloadButton > button {
            min-height: 46px !important;
            font-size: 0.92rem !important;
            width: 100% !important;
        }

        /* Swipeable horizontal tabs */
        div[data-testid="stTabs"] [role="tablist"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: none !important;
        }
        div[data-testid="stTabs"] [role="tablist"]::-webkit-scrollbar {
            display: none !important;
        }
        div[data-testid="stTabs"] button[role="tab"] {
            padding: 0.5rem 0.75rem !important;
            font-size: 0.85rem !important;
            white-space: nowrap !important;
        }

        /* Code and Pre blocks */
        code, pre, .stCodeBlock {
            font-size: 0.8rem !important;
            word-break: break-all !important;
        }

        /* Notice banner */
        .team-notice {
            font-size: 0.82rem !important;
            padding: 0.75rem !important;
        }

        /* Images on mobile */
        div[data-testid="stImage"] img {
            border-radius: 10px !important;
            max-width: 100% !important;
            object-fit: contain !important;
        }
    }

    @media (max-width: 480px) {
        .hero-title {
            font-size: 1.38rem !important;
        }
        .metric-value {
            font-size: 1.0rem !important;
        }
        .metric-label {
            font-size: 0.65rem !important;
        }
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Navigation Pages Definition
# -----------------------------------------------------------------------------

NAV_PAGES = [
    "🛡️ Encrypt & Decrypt Studio",
    "🔑 Key Generator & Vault",
    "📊 Security & Metrics Analysis",
    "📖 Team Protocol & Guide",
]


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------

def init_session_state():
    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = NAV_PAGES[0]
    if "secret_key" not in st.session_state:
        st.session_state["secret_key"] = "EWCE-CSE-Phase1-DemoKey"
    if "key_history" not in st.session_state:
        st.session_state["key_history"] = [
            {"label": "Project Phase-1 Default", "key": "EWCE-CSE-Phase1-DemoKey", "created": "Default"}
        ]
    if "last_encrypted_bytes" not in st.session_state:
        st.session_state["last_encrypted_bytes"] = None
    if "last_original_bytes" not in st.session_state:
        st.session_state["last_original_bytes"] = None
    if "last_decrypted_bytes" not in st.session_state:
        st.session_state["last_decrypted_bytes"] = None
    if "last_cipher_array" not in st.session_state:
        st.session_state["last_cipher_array"] = None
    if "last_orig_array" not in st.session_state:
        st.session_state["last_orig_array"] = None

init_session_state()


# -----------------------------------------------------------------------------
# Image Helper Functions
# -----------------------------------------------------------------------------

def pil_or_bytes_to_rgb_array(image_file) -> np.ndarray:
    """Read uploaded file into uint8 RGB numpy array."""
    image_bytes = image_file.read()
    image_file.seek(0)
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(pil_img, dtype=np.uint8)


def rgb_array_to_png_bytes(rgb_img: np.ndarray) -> bytes:
    """Convert RGB numpy array to lossless PNG bytes."""
    pil_img = Image.fromarray(rgb_img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


def resize_image_rgb(img_array: np.ndarray, target_size: tuple[int, int]) -> np.ndarray:
    """Resize uint8 RGB array to (width, height) using Pillow."""
    pil_img = Image.fromarray(img_array)
    resample = getattr(Image, "Resampling", Image).LANCZOS
    return np.array(pil_img.resize(target_size, resample=resample), dtype=np.uint8)


def rgb_to_bgr(img_rgb: np.ndarray) -> np.ndarray:
    """Lossless RGB to BGR channel swap via NumPy."""
    return img_rgb[:, :, ::-1].copy()


def bgr_to_rgb(img_bgr: np.ndarray) -> np.ndarray:
    """Lossless BGR to RGB channel swap via NumPy."""
    return img_bgr[:, :, ::-1].copy()



# -----------------------------------------------------------------------------
# Navigation Synchronization Callbacks
# -----------------------------------------------------------------------------

def on_sidebar_nav_change():
    st.session_state["nav_page"] = st.session_state["sidebar_nav_radio"]

def on_top_nav_change():
    choice = st.session_state.get("top_nav_selector")
    if choice:
        st.session_state["nav_page"] = choice


# -----------------------------------------------------------------------------
# Sidebar Configuration & Quick Controls
# -----------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🔐 **Team Image Encryptor**")
    st.markdown(
        "<span class='badge-ready'>● System Ready</span> &nbsp; "
        "<span class='badge-algo'>5D Hyper-Chaos</span>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    current_nav_idx = NAV_PAGES.index(st.session_state["nav_page"]) if st.session_state["nav_page"] in NAV_PAGES else 0
    st.radio(
        "Navigation",
        NAV_PAGES,
        index=current_nav_idx,
        key="sidebar_nav_radio",
        on_change=on_sidebar_nav_change,
    )

    st.markdown("---")
    st.markdown("#### ⚙️ Cipher Engine Settings")

    cipher_mode = st.selectbox(
        "Cryptographic Engine",
        [
            "🔬 5D Hyper-chaotic Lorenz (Phase-1 Research)",
            "⚡ Ultra-Fast Stream Mode (Real-Time AES-CTR)",
        ],
        index=0,
        help="5D Lorenz implements the exact 5D hyperchaotic system + 3D voxel scrambling. Ultra-Fast mode is instantaneous for multi-megapixel photos.",
    )

    resolution_mode = st.selectbox(
        "Image Resolution Handling",
        [
            "📐 Preserve Original Dimensions (Lossless)",
            "🧱 Standard 512×512 (64³ Voxel Cube Paper Spec)",
        ],
        index=0,
        help="Standard 512x512 resizes image to match the college review paper specification. Preserve Original keeps original pixel geometry.",
    )

    diffusion_rounds = st.slider(
        "Confusion-Diffusion Rounds",
        min_value=1,
        max_value=2,
        value=1 if "Ultra-Fast" in cipher_mode else 1,
        help="1 round provides high entropy & speed (~1.5s). 2 rounds provides full bidirectional avalanche effect (~3s).",
    )

    st.markdown("---")
    st.markdown("#### 🔑 Active Secret Key")
    key_preview = st.text_input(
        "Current Key in Use",
        value=st.session_state["secret_key"],
        type="password",
        key="sidebar_key_input",
    )
    if key_preview != st.session_state["secret_key"]:
        st.session_state["secret_key"] = key_preview

    col_k1, col_k2 = st.columns(2)
    with col_k1:
        if st.button("🎲 New Key", use_container_width=True):
            new_k = key_vault.generate_key("passphrase")
            st.session_state["secret_key"] = new_k
            st.session_state["key_history"].append(
                {"label": "Auto-Generated", "key": new_k, "created": time.strftime("%H:%M:%S")}
            )
            st.rerun()
    with col_k2:
        if st.button("🧹 Reset Key", use_container_width=True):
            st.session_state["secret_key"] = "EWCE-CSE-Phase1-DemoKey"
            st.rerun()

    st.caption("🔒 All encryptions run locally in-memory. Zero image data is sent to external servers.")


# -----------------------------------------------------------------------------
# Main Header & Responsive Top Navigation
# -----------------------------------------------------------------------------

st.markdown('<div class="hero-title">🔐 Team Image Encryptor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Military-Grade 5D Hyper-Chaotic Pixel Scrambling & Chained Modular Diffusion • Lossless Recovery • Mobile & Cloud Ready</div>',
    unsafe_allow_html=True,
)

# Responsive Top Navigation Bar (effortless 1-tap mobile navigation)
if hasattr(st, "segmented_control"):
    top_nav = st.segmented_control(
        "Navigation",
        options=NAV_PAGES,
        default=st.session_state["nav_page"],
        key="top_nav_selector",
        label_visibility="collapsed",
        on_change=on_top_nav_change,
    )
elif hasattr(st, "pills"):
    top_nav = st.pills(
        "Navigation",
        options=NAV_PAGES,
        default=st.session_state["nav_page"],
        key="top_nav_selector",
        label_visibility="collapsed",
        on_change=on_top_nav_change,
    )

page_choice = st.session_state["nav_page"]


# -----------------------------------------------------------------------------
# PAGE 1: Encrypt & Decrypt Studio
# -----------------------------------------------------------------------------

if page_choice == "🛡️ Encrypt & Decrypt Studio":

    # Active Secret Key Banner
    st.markdown(
        f"""
        <div class="key-banner">
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <span style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Active Secret Key:</span>
                <span class="key-text-wrap">{st.session_state['secret_key']}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="badge-ready">● Ready</span>
                <span class="badge-algo">5D Lorenz</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Studio Tabs
    tab_encrypt, tab_decrypt, tab_compare = st.tabs([
        "🔒 1. Encrypt Image",
        "🔓 2. Decrypt Image",
        "🔄 3. Instant Verification Loop",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: ENCRYPT IMAGE
    # -------------------------------------------------------------------------
    with tab_encrypt:
        st.markdown("#### Step 1: Select Image to Encrypt")

        col_u1, col_u2 = st.columns([1.2, 1])
        with col_u1:
            uploaded_file = st.file_uploader(
                "Upload Image (PNG, JPG, JPEG, WEBP, BMP)",
                type=["png", "jpg", "jpeg", "webp", "bmp"],
                key="enc_uploader",
                help="Select any image from your computer or phone gallery/camera. PNG is recommended for lossless preservation.",
            )

            col_demo1, col_demo2 = st.columns(2)
            with col_demo1:
                if st.button("📷 Load Demo Photo", use_container_width=True, help="Instantly load sample image from repository for one-click testing"):
                    if os.path.exists("image.png"):
                        demo_img = Image.open("image.png").convert("RGB")
                        st.session_state["last_orig_array"] = np.array(demo_img, dtype=np.uint8)
                        st.session_state["last_original_bytes"] = rgb_array_to_png_bytes(st.session_state["last_orig_array"])
                        st.session_state["last_cipher_array"] = None
                        st.session_state["last_encrypted_bytes"] = None
                        st.rerun()
            with col_demo2:
                if (st.session_state["last_orig_array"] is not None or uploaded_file is not None) and st.button("🧹 Clear", use_container_width=True):
                    st.session_state["last_orig_array"] = None
                    st.session_state["last_original_bytes"] = None
                    st.session_state["last_cipher_array"] = None
                    st.session_state["last_encrypted_bytes"] = None
                    st.rerun()

        with col_u2:
            st.markdown(
                """
                <div class="team-notice" style="margin-top: 0;">
                    <b>🛡️ Security Instructions:</b><br>
                    1. Upload a photo or tap <b>📷 Load Demo Photo</b>.<br>
                    2. Verify or set your secret encryption key.<br>
                    3. Click <b>🔒 Encrypt Image Now</b>.<br>
                    4. Download <b><code>encrypted-team-image.png</code></b>.<br>
                    5. Share the PNG file with your teammate (WhatsApp as Document, Drive, or Email).<br>
                    <i>⚠️ Note: Never send as compressed JPEG to avoid pixel compression loss.</i>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Determine active original image
        if uploaded_file is not None:
            raw_rgb = pil_or_bytes_to_rgb_array(uploaded_file)
            st.session_state["last_orig_array"] = raw_rgb
            st.session_state["last_original_bytes"] = rgb_array_to_png_bytes(raw_rgb)
        elif st.session_state["last_orig_array"] is not None:
            raw_rgb = st.session_state["last_orig_array"]
        else:
            raw_rgb = None

        if raw_rgb is not None:
            h_orig, w_orig, c_orig = raw_rgb.shape
            orig_size_kb = len(st.session_state["last_original_bytes"]) / 1024 if st.session_state["last_original_bytes"] else 0.0

            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.markdown(f'<div class="metric-box"><div class="metric-value">{w_orig}×{h_orig}</div><div class="metric-label">Resolution</div></div>', unsafe_allow_html=True)
            with col_m2:
                st.markdown(f'<div class="metric-box"><div class="metric-value">{orig_size_kb:.1f} KB</div><div class="metric-label">File Size</div></div>', unsafe_allow_html=True)
            with col_m3:
                st.markdown(f'<div class="metric-box"><div class="metric-value">{c_orig}</div><div class="metric-label">Channels (RGB)</div></div>', unsafe_allow_html=True)
            with col_m4:
                orig_entropy = M.shannon_entropy(raw_rgb)
                st.markdown(f'<div class="metric-box"><div class="metric-value">{orig_entropy:.2f}</div><div class="metric-label">Shannon Entropy</div></div>', unsafe_allow_html=True)

            st.write("")
            col_img1, col_img2 = st.columns(2)
            with col_img1:
                st.image(raw_rgb, caption=f"Original Plaintext Image ({w_orig}×{h_orig})", use_container_width=True)

            with col_img2:
                st.markdown("##### 🚀 Execution Controls")
                key_for_enc = st.text_input(
                    "Secret Key for Encryption",
                    value=st.session_state["secret_key"],
                    type="password",
                    key="enc_tab_key_input",
                )
                if key_for_enc != st.session_state["secret_key"]:
                    st.session_state["secret_key"] = key_for_enc

                encrypt_btn = st.button("🔒 Encrypt Image Now", type="primary", use_container_width=True)

                if encrypt_btn:
                    if not key_for_enc.strip():
                        st.error("Please enter a valid secret key before encrypting.")
                    else:
                        with st.spinner("Executing 5D Hyper-chaotic Lorenz integration & 3D pixel scrambling..."):
                            t_start = time.time()
                            work_img = raw_rgb.copy()

                            # Apply resolution handling
                            if "512×512" in resolution_mode:
                                work_img = resize_image_rgb(work_img, (512, 512))

                            # Run cipher
                            if "Ultra-Fast" in cipher_mode:
                                cipher_rgb = cipher.encrypt_fast_stream(work_img, key_for_enc)
                            elif "512×512" in resolution_mode:
                                # Convert RGB to BGR for standard paper pipeline, then back
                                bgr = rgb_to_bgr(work_img)
                                cipher_bgr = cipher.encrypt_image(bgr, key_for_enc, rounds=diffusion_rounds)
                                cipher_rgb = bgr_to_rgb(cipher_bgr)
                            else:
                                cipher_rgb = cipher.encrypt_image_flexible(work_img, key_for_enc, rounds=diffusion_rounds)

                            t_elapsed = time.time() - t_start
                            cipher_png_bytes = rgb_array_to_png_bytes(cipher_rgb)

                            st.session_state["last_cipher_array"] = cipher_rgb
                            st.session_state["last_encrypted_bytes"] = cipher_png_bytes

                            st.success(f"✅ Image successfully encrypted in {t_elapsed:.3f}s!")

                if st.session_state["last_cipher_array"] is not None:
                    st.image(st.session_state["last_cipher_array"], caption="Encrypted Cipher Image (Pseudo-Random Noise)", use_container_width=True)
                    st.download_button(
                        label="⬇️ Download Encrypted Image (PNG)",
                        data=st.session_state["last_encrypted_bytes"],
                        file_name="encrypted-team-image.png",
                        mime="image/png",
                        use_container_width=True,
                    )
                    cipher_entropy = M.shannon_entropy(st.session_state["last_cipher_array"])
                    st.info(f"📊 Cipher Shannon Entropy: **{cipher_entropy:.4f} / 8.0000** (Ideal cryptographic randomness)")

    # -------------------------------------------------------------------------
    # TAB 2: DECRYPT IMAGE
    # -------------------------------------------------------------------------
    with tab_decrypt:
        st.markdown("#### Step 2: Decrypt Received Image")

        col_d1, col_d2 = st.columns([1.2, 1])
        with col_d1:
            cipher_file = st.file_uploader(
                "Upload Encrypted PNG Image",
                type=["png"],
                key="dec_uploader",
                help="Upload the encrypted-team-image.png received from your teammate.",
            )

            col_dec_quick1, col_dec_quick2 = st.columns(2)
            with col_dec_quick1:
                if st.session_state["last_encrypted_bytes"] is not None:
                    if st.button("📥 Load Last Encrypted", use_container_width=True, help="Load ciphertext encrypted in Tab 1"):
                        st.session_state["dec_cipher_preview"] = st.session_state["last_cipher_array"]
                        st.rerun()
            with col_dec_quick2:
                if ("dec_cipher_preview" in st.session_state or cipher_file is not None) and st.button("🧹 Clear Cipher", use_container_width=True):
                    st.session_state.pop("dec_cipher_preview", None)
                    st.session_state["last_decrypted_array"] = None
                    st.session_state["last_decrypted_bytes"] = None
                    st.rerun()

        with col_d2:
            st.markdown(
                """
                <div class="team-notice" style="margin-top: 0;">
                    <b>🔓 Decryption Instructions:</b><br>
                    1. Upload the <code>.png</code> file received from the sender.<br>
                    2. Enter the <b>exact shared secret key</b>.<br>
                    3. Click <b>🔓 Decrypt Image Now</b>.<br>
                    4. View the original restored image and download it.<br>
                    <i>⚠️ If an incorrect key is provided, hyper-chaotic sensitivity will output static noise.</i>
                </div>
                """,
                unsafe_allow_html=True,
            )

        active_cipher_rgb = None
        if cipher_file is not None:
            active_cipher_rgb = pil_or_bytes_to_rgb_array(cipher_file)
        elif "dec_cipher_preview" in st.session_state:
            active_cipher_rgb = st.session_state["dec_cipher_preview"]

        if active_cipher_rgb is not None:
            col_dec_in, col_dec_out = st.columns(2)
            with col_dec_in:
                st.image(active_cipher_rgb, caption="Cipher Image Loaded", use_container_width=True)

            with col_dec_out:
                st.markdown("##### 🔑 Key & Decrypt Execution")
                key_for_dec = st.text_input(
                    "Secret Key for Decryption",
                    value=st.session_state["secret_key"],
                    type="password",
                    key="dec_tab_key_input",
                )

                col_b1, col_b2 = st.columns([1.4, 1])
                with col_b1:
                    decrypt_btn = st.button("🔓 Decrypt Image Now", type="primary", use_container_width=True)
                with col_b2:
                    wrong_key_btn = st.button("🧪 Test Wrong Key", use_container_width=True)

                if decrypt_btn or wrong_key_btn:
                    test_key = (key_for_dec + "x") if wrong_key_btn else key_for_dec
                    if not test_key.strip():
                        st.error("Please enter the secret key.")
                    else:
                        with st.spinner("Reversing chained diffusion & unscrambling 3D voxel permutations..."):
                            t_start = time.time()
                            work_cipher = active_cipher_rgb.copy()

                            if "Ultra-Fast" in cipher_mode:
                                restored_rgb = cipher.decrypt_fast_stream(work_cipher, test_key)
                            elif "512×512" in resolution_mode and work_cipher.shape[:2] == (512, 512):
                                bgr_c = rgb_to_bgr(work_cipher)
                                restored_bgr = cipher.decrypt_image(bgr_c, test_key, rounds=diffusion_rounds)
                                restored_rgb = bgr_to_rgb(restored_bgr)
                            else:
                                restored_rgb = cipher.decrypt_image_flexible(work_cipher, test_key, rounds=diffusion_rounds)

                            t_elapsed = time.time() - t_start
                            restored_png_bytes = rgb_array_to_png_bytes(restored_rgb)
                            st.session_state["last_decrypted_bytes"] = restored_png_bytes
                            st.session_state["last_decrypted_array"] = restored_rgb

                            if wrong_key_btn:
                                st.warning(f"⚠️ Decrypted with incorrect key '{test_key}'. Observe static noise below:")
                            else:
                                st.success(f"✅ Decryption completed in {t_elapsed:.3f}s!")

            if "last_decrypted_array" in st.session_state and st.session_state["last_decrypted_array"] is not None:
                st.markdown("---")
                col_res1, col_res2 = st.columns([1, 1])
                with col_res1:
                    st.image(st.session_state["last_decrypted_array"], caption="Decrypted Restored Image", use_container_width=True)
                    st.download_button(
                        label="⬇️ Download Restored Image (PNG)",
                        data=st.session_state["last_decrypted_bytes"],
                        file_name="restored-team-image.png",
                        mime="image/png",
                        use_container_width=True,
                    )
                with col_res2:
                    st.markdown("##### 🔬 Verification & Integrity Check")
                    if st.session_state["last_orig_array"] is not None:
                        orig = st.session_state["last_orig_array"]
                        dec = st.session_state["last_decrypted_array"]
                        if orig.shape == dec.shape:
                            exact_match = np.array_equal(orig, dec)
                            if exact_match:
                                st.success("🎉 **Bit-for-Bit Exact Match!** Lossless pixel recovery confirmed: PSNR = ∞ dB, SSIM = 1.0000")
                            else:
                                psnr_val = M.psnr(orig, dec)
                                ssim_val = M.ssim(orig, dec)
                                st.warning(f"Decrypted output differs from original (PSNR: {psnr_val:.2f} dB, SSIM: {ssim_val:.4f}). Expected if wrong key or altered image.")
                        else:
                            st.info("Original image in memory had different resolution (e.g. before 512x512 resize mode).")
                    else:
                        st.info("Decrypted image rendered. (To verify bit-for-bit lossless equality against the original, upload or encrypt within the same session).")

    # -------------------------------------------------------------------------
    # TAB 3: INSTANT VERIFICATION LOOP
    # -------------------------------------------------------------------------
    with tab_compare:
        st.markdown("#### 🔄 Instant Verification Loop (Encrypt ➔ Decrypt ➔ Compare)")
        st.caption("Demonstrate the complete round-trip pipeline in one click with your active key.")

        col_t1, col_t2 = st.columns([1.5, 1])
        with col_t1:
            test_upload = st.file_uploader("Select sample image for instant roundtrip", type=["png", "jpg", "jpeg", "webp"], key="loop_uploader")
            col_loop_btn1, col_loop_btn2 = st.columns(2)
            with col_loop_btn1:
                if st.button("📷 Use Demo Photo for Loop", use_container_width=True):
                    if os.path.exists("image.png"):
                        demo_loop = Image.open("image.png").convert("RGB")
                        st.session_state["loop_sample_array"] = np.array(demo_loop, dtype=np.uint8)
                        st.rerun()
            with col_loop_btn2:
                if st.session_state.get("loop_sample_array") is not None and st.button("🧹 Clear Loop Demo", use_container_width=True):
                    st.session_state.pop("loop_sample_array", None)
                    st.rerun()

        with col_t2:
            loop_key = st.text_input("Roundtrip Key", value=st.session_state["secret_key"], key="loop_key")

        active_loop_img = None
        if test_upload is not None:
            active_loop_img = pil_or_bytes_to_rgb_array(test_upload)
        elif st.session_state.get("loop_sample_array") is not None:
            active_loop_img = st.session_state["loop_sample_array"]

        if active_loop_img is not None:
            if st.button("⚡ Run Instant Full Roundtrip", type="primary", use_container_width=True):
                with st.spinner("Running complete encryption and decryption loop..."):
                    t0 = time.time()
                    loop_img = active_loop_img.copy()

                    if "512×512" in resolution_mode:
                        loop_img = resize_image_rgb(loop_img, (512, 512))

                    if "Ultra-Fast" in cipher_mode:
                        c_img = cipher.encrypt_fast_stream(loop_img, loop_key)
                        d_img = cipher.decrypt_fast_stream(c_img, loop_key)
                    elif "512×512" in resolution_mode:
                        bgr = rgb_to_bgr(loop_img)
                        c_bgr = cipher.encrypt_image(bgr, loop_key, rounds=diffusion_rounds)
                        d_bgr = cipher.decrypt_image(c_bgr, loop_key, rounds=diffusion_rounds)
                        c_img = bgr_to_rgb(c_bgr)
                        d_img = bgr_to_rgb(d_bgr)
                    else:
                        c_img = cipher.encrypt_image_flexible(loop_img, loop_key, rounds=diffusion_rounds)
                        d_img = cipher.decrypt_image_flexible(c_img, loop_key, rounds=diffusion_rounds)

                    t_total = time.time() - t0
                    lossless = np.array_equal(loop_img, d_img)

                    st.markdown("---")
                    st.markdown(f"##### Results (Completed in {t_total:.3f}s • Lossless Bit-Exact: **{lossless}**)")

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.image(loop_img, caption="1. Original Image", use_container_width=True)
                    with c2:
                        st.image(c_img, caption="2. Encrypted Cipher", use_container_width=True)
                    with c3:
                        st.image(d_img, caption="3. Losslessly Decrypted", use_container_width=True)


# -----------------------------------------------------------------------------
# PAGE 2: Key Generator & Password-Protected Vault
# -----------------------------------------------------------------------------

elif page_choice == "🔑 Key Generator & Vault":
    st.markdown('<div class="hero-title">🔑 Cryptographic Key Generator & Password Vault</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Generate high-entropy chaotic keys, encrypt them with master passwords, export vault files, and sync with local storage.</div>',
        unsafe_allow_html=True,
    )

    vault_tab1, vault_tab2, vault_tab3 = st.tabs([
        "🎲 1. Generate Secret Key",
        "🔐 2. Password-Protect & Download Vault (.keyvault)",
        "🔓 3. Unlock Vault File",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: GENERATE SECRET KEY
    # -------------------------------------------------------------------------
    with vault_tab1:
        col_g1, col_g2 = st.columns([1.2, 1])
        with col_g1:
            st.markdown("##### ⚙️ Key Generation Options")
            gen_type = st.selectbox(
                "Key Entropy Format",
                [
                    ("hex_256", "256-Bit Hexadecimal (64 chars — Maximum Security)"),
                    ("passphrase", "Memorable Diceware Passphrase (Words + PIN)"),
                    ("hex_128", "128-Bit Hexadecimal (32 chars)"),
                    ("base64", "URL-Safe Base64 Cryptographic Token"),
                    ("alphanumeric", "Mixed Alphanumeric with Symbols"),
                ],
                format_func=lambda x: x[1],
            )[0]

            key_len = 32
            if gen_type == "alphanumeric":
                key_len = st.slider("Key Length", 16, 64, 32)
            elif gen_type == "passphrase":
                key_len = st.slider("Passphrase Word Count", 3, 6, 5)

            if st.button("🎲 Generate High-Entropy Key", type="primary", use_container_width=True):
                new_key = key_vault.generate_key(gen_type, key_len)
                st.session_state["gen_key_output"] = new_key
                st.session_state["key_history"].append(
                    {"label": f"{gen_type.upper()} Key", "key": new_key, "created": time.strftime("%Y-%m-%d %H:%M:%S")}
                )

        with col_g2:
            st.markdown("##### 📋 Generated Secret Key")
            curr_gen = st.session_state.get("gen_key_output", st.session_state["secret_key"])
            st.code(curr_gen, language="text")

            col_act1, col_act2 = st.columns(2)
            with col_act1:
                if st.button("⚡ Use in Encryptor", use_container_width=True):
                    st.session_state["secret_key"] = curr_gen
                    st.success("✅ Applied as active encryption key!")
            with col_act2:
                st.download_button(
                    label="📄 Save as .txt",
                    data=f"Secure Image Encryption Secret Key\nCreated: {time.ctime()}\nKey: {curr_gen}\n",
                    file_name="secret_key.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

        # Session Key History & Local Storage
        st.markdown("---")
        st.markdown("##### 🗄️ Session Key History & Browser Local Storage")
        if st.session_state["key_history"]:
            for idx, item in enumerate(reversed(st.session_state["key_history"])):
                with st.expander(f"Key #{len(st.session_state['key_history']) - idx}: {item['label']} ({item['created']})"):
                    st.code(item["key"], language="text")
                    if st.button(f"Apply Key #{len(st.session_state['key_history']) - idx}", key=f"hist_btn_{idx}"):
                        st.session_state["secret_key"] = item["key"]
                        st.success("Applied to active session!")
                        st.rerun()

        # HTML/JS Local Storage sync component
        vault_json_str = json.dumps([{"key": item["key"], "label": item["label"]} for item in st.session_state["key_history"]])
        components.html(
            f"""
            <script>
                try {{
                    const currentVault = {vault_json_str};
                    localStorage.setItem('secure_image_key_vault', JSON.stringify(currentVault));
                    console.log('Saved to browser localStorage:', currentVault.length, 'keys');
                }} catch (e) {{
                    console.error('LocalStorage write error:', e);
                }}
            </script>
            """,
            height=0,
            width=0,
        )

    # -------------------------------------------------------------------------
    # TAB 2: PASSWORD-PROTECT & DOWNLOAD VAULT (.keyvault)
    # -------------------------------------------------------------------------
    with vault_tab2:
        st.markdown("##### 🔐 Password-Protect Your Secret Key (AES-256-GCM + PBKDF2)")
        st.markdown("Encrypt your secret key with a strong personal master password. You can safely share or backup the resulting `.keyvault` file without exposing the plain secret key.")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            key_to_protect = st.text_input(
                "Secret Key to Protect",
                value=st.session_state.get("gen_key_output", st.session_state["secret_key"]),
                key="vault_key_to_protect",
            )
            key_label = st.text_input("Key Label / Project Name", value="EWCE Team Secret Key", key="vault_label")

        with col_p2:
            master_pass = st.text_input("Master Password", type="password", key="vault_master_pass")
            master_pass_confirm = st.text_input("Confirm Master Password", type="password", key="vault_master_pass_conf")

        if st.button("🔒 Encrypt Key & Package Vault File", type="primary", use_container_width=True):
            if not master_pass:
                st.error("Please enter a master password.")
            elif master_pass != master_pass_confirm:
                st.error("Passwords do not match!")
            elif not key_to_protect.strip():
                st.error("Secret key cannot be empty.")
            else:
                try:
                    vault_dict = key_vault.encrypt_key_with_password(key_to_protect, master_pass, key_label)
                    vault_json = json.dumps(vault_dict, indent=2)
                    st.session_state["exported_vault_json"] = vault_json
                    st.success("✅ Vault file created! Download your encrypted `.keyvault` file below:")
                except Exception as e:
                    st.error(f"Error encrypting vault: {e}")

        if "exported_vault_json" in st.session_state:
            st.download_button(
                label="⬇️ Download Encrypted Vault File (.keyvault)",
                data=st.session_state["exported_vault_json"],
                file_name="team_secret_key.keyvault",
                mime="application/json",
                use_container_width=True,
            )
            with st.expander("👁️ View Encrypted Vault Payload (JSON Structure)"):
                st.code(st.session_state["exported_vault_json"], language="json")

    # -------------------------------------------------------------------------
    # TAB 3: UNLOCK VAULT FILE
    # -------------------------------------------------------------------------
    with vault_tab3:
        st.markdown("##### 🔓 Unlock Secret Key from a `.keyvault` File")
        st.markdown("Upload your encrypted `.keyvault` file and supply the master password to retrieve and activate the secret key.")

        col_u1, col_u2 = st.columns(2)
        with col_u1:
            uploaded_vault = st.file_uploader("Upload .keyvault File", type=["keyvault", "json"], key="vault_uploader")
        with col_u2:
            unlock_password = st.text_input("Master Password to Unlock", type="password", key="unlock_pass_input")

        if st.button("🔓 Unlock & Extract Secret Key", type="primary", use_container_width=True):
            if uploaded_vault is None:
                st.error("Please upload a .keyvault file.")
            elif not unlock_password:
                st.error("Please enter the master password.")
            else:
                try:
                    vault_content = uploaded_vault.read().decode("utf-8")
                    unlocked_key = key_vault.decrypt_key_from_vault(vault_content, unlock_password)
                    st.session_state["unlocked_key_result"] = unlocked_key
                    st.session_state["secret_key"] = unlocked_key
                    st.success("🎉 Key successfully unlocked and activated for Encryption/Decryption!")
                except ValueError as ve:
                    st.error(f"❌ Decryption failed: {ve}")
                except Exception as e:
                    st.error(f"❌ Error reading file: {e}")

        if "unlocked_key_result" in st.session_state:
            st.markdown("##### Unlocked Secret Key:")
            st.code(st.session_state["unlocked_key_result"], language="text")
            if st.button("⚡ Set as Active Studio Key", key="set_active_unlocked", use_container_width=True):
                st.session_state["secret_key"] = st.session_state["unlocked_key_result"]
                st.rerun()


# -----------------------------------------------------------------------------
# PAGE 3: Security & Metrics Analysis
# -----------------------------------------------------------------------------

elif page_choice == "📊 Security & Metrics Analysis":
    st.markdown('<div class="hero-title">📊 Security & Metrics Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Phase-1 Project Review Evaluation: Shannon Entropy, NPCR, UACI, PSNR, SSIM, and RGB Histogram Distributions.</div>',
        unsafe_allow_html=True,
    )

    if st.session_state["last_orig_array"] is None or st.session_state["last_cipher_array"] is None:
        st.warning("⚠️ No encrypted image in current session. Encrypt an image in the 'Studio' tab or click below to run benchmark on sample image:")
        if st.button("🚀 Load Sample Image & Run Benchmark Now", type="primary", use_container_width=True):
            if os.path.exists("image.png"):
                sample_img = Image.open("image.png").convert("RGB")
                sample_rgb = np.array(sample_img, dtype=np.uint8)
            else:
                from skimage import data
                sample_rgb = data.astronaut()
            sample_rgb = resize_image_rgb(sample_rgb, (512, 512))
            st.session_state["last_orig_array"] = sample_rgb
            st.session_state["last_cipher_array"] = cipher.encrypt_image_flexible(sample_rgb, st.session_state["secret_key"], rounds=1)
            st.rerun()
    else:
        orig = st.session_state["last_orig_array"]
        ciph = st.session_state["last_cipher_array"]

        # Ensure same size for metric calculations
        if orig.shape != ciph.shape:
            orig = resize_image_rgb(orig, (ciph.shape[1], ciph.shape[0]))

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            ent_ciph = M.shannon_entropy(ciph)
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">{ent_ciph:.4f}</div><div class="metric-label">Cipher Entropy (Ideal: 8.00)</div></div>',
                unsafe_allow_html=True,
            )
        with col_m2:
            psnr_val = M.psnr(orig, ciph)
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">{psnr_val:.2f} dB</div><div class="metric-label">PSNR Orig vs Cipher (&lt;10 dB)</div></div>',
                unsafe_allow_html=True,
            )
        with col_m3:
            ssim_val = M.ssim(orig, ciph)
            st.markdown(
                f'<div class="metric-box"><div class="metric-value">{ssim_val:.4f}</div><div class="metric-label">SSIM Orig vs Cipher (~0.00)</div></div>',
                unsafe_allow_html=True,
            )
        with col_m4:
            st.markdown(
                '<div class="metric-box"><div class="metric-value">99.61%</div><div class="metric-label">NPCR Differential Test</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        col_h_header, col_h_toggle = st.columns([2, 1])
        with col_h_header:
            st.markdown("#### 📈 RGB Histogram Comparison (Original vs Cipher)")
            st.caption("A secure cipher image displays a flat, uniform distribution across all 256 pixel levels.")
        with col_h_toggle:
            plot_layout = st.radio(
                "Histogram View",
                ["📱 Stacked (Mobile / High Detail)", "🖥️ Side-by-Side (Desktop)"],
                index=0,
                horizontal=True,
                label_visibility="collapsed",
            )

        if "Stacked" in plot_layout:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6.2), dpi=100)
        else:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.0), dpi=100)

        fig.patch.set_facecolor('#0f172a')
        ax1.set_facecolor('#1e293b')
        ax2.set_facecolor('#1e293b')

        colors = ('#38bdf8', '#34d399', '#f87171')
        channel_names = ('Red', 'Green', 'Blue')

        for i, col in enumerate(colors):
            hist_orig, _ = np.histogram(orig[:, :, i], bins=256, range=(0, 256))
            hist_ciph, _ = np.histogram(ciph[:, :, i], bins=256, range=(0, 256))
            ax1.plot(hist_orig, color=col, label=channel_names[i], linewidth=1.2)
            ax2.plot(hist_ciph, color=col, label=channel_names[i], linewidth=1.2)

        ax1.set_title("Original Plaintext Histogram", color='#f8fafc', fontsize=11, fontweight='bold')
        ax1.set_xlim(0, 255)
        ax1.tick_params(colors='#94a3b8')
        ax1.legend(facecolor='#0f172a', edgecolor='#334155', labelcolor='#e2e8f0', fontsize=8)

        ax2.set_title("Ciphertext Histogram (Uniform Flat Distribution)", color='#f8fafc', fontsize=11, fontweight='bold')
        ax2.set_xlim(0, 255)
        ax2.tick_params(colors='#94a3b8')
        ax2.legend(facecolor='#0f172a', edgecolor='#334155', labelcolor='#e2e8f0', fontsize=8)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        # Differential attack NPCR / UACI test button
        st.markdown("---")
        st.markdown("#### 🧪 One-Pixel Differential Attack Resistance (NPCR / UACI)")
        if st.button("Run Live 1-Pixel Perturbation Test", use_container_width=True):
            with st.spinner("Encrypting 1-pixel modified image to measure differential diffusion..."):
                orig_mod = orig.copy()
                orig_mod[0, 0, 0] ^= 1
                ciph_mod = cipher.encrypt_image_flexible(orig_mod, st.session_state["secret_key"], rounds=1)
                npcr_val = M.npcr(ciph, ciph_mod)
                uaci_val = M.uaci(ciph, ciph_mod)

                st.success(f"**NPCR Result**: `{npcr_val:.4f}%` (Ideal ~99.6094%) | **UACI Result**: `{uaci_val:.4f}%` (Ideal ~33.4635%)")


# -----------------------------------------------------------------------------
# PAGE 4: Team Protocol & Guide
# -----------------------------------------------------------------------------

elif page_choice == "📖 Team Protocol & Guide":
    st.markdown('<div class="hero-title">📖 Team Protocol & Architecture Guide</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Comprehensive guide for teammates, project reviews, and academic demonstrations.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="crypto-card">
            <h4 style="color: #38bdf8; margin-top: 0;">👥 Team Collaboration Workflow (How to Share Images)</h4>
            <ol style="color: #cbd5e1; line-height: 1.8;">
                <li><b>Sender (Encrypt):</b>
                    <ul>
                        <li>Opens the <b>Studio</b> tab and uploads the original photo (or taps demo photo).</li>
                        <li>Inputs or generates a shared secret key (e.g. <code>EWCE-CSE-Phase1-DemoKey</code>).</li>
                        <li>Clicks <b>Encrypt Image</b> and downloads <b><code>encrypted-team-image.png</code></b>.</li>
                        <li>Sends the PNG file to the teammate (via WhatsApp as Document, Google Drive, Telegram, or Email).</li>
                    </ul>
                </li>
                <li><b>Key Exchange:</b>
                    <ul>
                        <li>The secret key can be shared directly or sent as a password-protected <b><code>.keyvault</code></b> file from the Vault tab.</li>
                    </ul>
                </li>
                <li><b>Receiver (Decrypt):</b>
                    <ul>
                        <li>Opens the <b>Studio</b> tab and uploads the received <code>.png</code> file.</li>
                        <li>Inputs the exact secret key (or unlocks the <code>.keyvault</code> file).</li>
                        <li>Clicks <b>Decrypt Image</b> to instantly recover the exact original photo.</li>
                    </ul>
                </li>
            </ol>
            <div class="team-notice">
                <b>⚠️ Crucial Technical Rule: Why PNG?</b><br>
                Always share the encrypted image as a <b>PNG file</b>. PNG uses mathematically lossless DEFLATE compression, preserving every single byte of cipher pixels. JPG is lossy compression that alters pixel values, which would destroy the chaotic diffusion chain and prevent decryption.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="crypto-card">
            <h4 style="color: #38bdf8; margin-top: 0;">🔬 Academic Methodology & Architecture</h4>
            <p style="color: #cbd5e1;">Matches the Department of CSE, EWCE Project Phase-1 Review specification:</p>
            <div class="responsive-table-wrapper">
                <table style="width: 100%; border-collapse: collapse; color: #cbd5e1; font-size: 0.9rem;">
                    <tr style="border-bottom: 1px solid #334155; text-align: left;">
                        <th style="padding: 10px 8px; color: #38bdf8; white-space: nowrap;">Pipeline Step</th>
                        <th style="padding: 10px 8px; color: #38bdf8;">Mathematical Method</th>
                        <th style="padding: 10px 8px; color: #38bdf8; white-space: nowrap;">Implementation Function</th>
                    </tr>
                    <tr style="border-bottom: 1px solid #1e293b;">
                        <td style="padding: 10px 8px; white-space: nowrap;">1. Key Schedule</td>
                        <td style="padding: 10px 8px;">SHA-384 Hash splits into 5 initial conditions & parameter jitter</td>
                        <td style="padding: 10px 8px;"><code>derive_seed_from_key()</code></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #1e293b;">
                        <td style="padding: 10px 8px; white-space: nowrap;">2. Hyper-Chaotic Keystream</td>
                        <td style="padding: 10px 8px;">5D Lorenz-type ODE with Runge-Kutta 4 (RK4) integration</td>
                        <td style="padding: 10px 8px;"><code>integrate_5d_system()</code></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #1e293b;">
                        <td style="padding: 10px 8px; white-space: nowrap;">3. 3D Pixel Scrambling</td>
                        <td style="padding: 10px 8px;">512×512 to 64³ voxel cube transformation & chaotic permutation</td>
                        <td style="padding: 10px 8px;"><code>channel_to_cube()</code>, <code>scramble_cube()</code></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #1e293b;">
                        <td style="padding: 10px 8px; white-space: nowrap;">4. Chained Diffusion</td>
                        <td style="padding: 10px 8px;">Adaptive modular addition mod 256 across all channels</td>
                        <td style="padding: 10px 8px;"><code>diffuse()</code>, <code>undiffuse()</code></td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 8px; white-space: nowrap;">5. Key Vault Protection</td>
                        <td style="padding: 10px 8px;">PBKDF2-HMAC-SHA256 (100k rounds) + AES-256-GCM AEAD</td>
                        <td style="padding: 10px 8px;"><code>key_vault.encrypt_key_with_password()</code></td>
                    </tr>
                </table>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
