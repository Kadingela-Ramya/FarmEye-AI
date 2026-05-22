import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile, os, time, io, json, datetime
from pathlib import Path
from collections import Counter

# -- YOUR PERSONAL INFO -- edit these -----------------------------------------
YOUR_NAME     = "Kadingela Ramya"
YOUR_LINKEDIN = "linkedin.com/in/ramya-kadingela"
YOUR_GITHUB   = "github.com/Kadingela-Ramya"
YOUR_COLLEGE  = "Siddhartha Institute of Technology and Sciences"
YOUR_YEAR     = "4th Year · AI & ML"
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="FarmEye -- AI Precision Agriculture",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": f"FarmEye | Built by {YOUR_NAME} | {YOUR_COLLEGE}"}
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=IBM+Plex+Mono:wght@400;500&family=Lato:wght@300;400;700&display=swap');

:root {
    --soil:   #1a120b;
    --bark:   #2d1e0f;
    --moss:   #2d4a1e;
    --leaf:   #4a7c2f;
    --sprout: #7cb842;
    --wheat:  #d4a843;
    --cream:  #f5efe0;
    --fog:    #c8bfaf;
    --danger: #c0392b;
    --sky:    #5b8fa8;
}
html, body, [class*="css"] { font-family: 'Lato', sans-serif; background-color: var(--soil) !important; }
.stApp { background: var(--soil) !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a120b 0%, #0f0a05 100%) !important;
    border-right: 1px solid #3a2a15 !important;
}
[data-testid="stSidebar"] * { color: var(--cream) !important; }

.header-wrap {
    background: linear-gradient(135deg, #2d4a1e 0%, #1a2e10 60%, #1a120b 100%);
    border: 1px solid #4a7c2f44; border-radius: 4px;
    padding: 2rem 2.5rem 1.8rem; margin-bottom: 1.5rem;
    position: relative; overflow: hidden;
}
.header-wrap::after {
    content: '';
    position: absolute; left: 0; top: 0; bottom: 0; width: 6px;
    background: var(--sprout); border-radius: 4px 0 0 4px;
}
.header-title { font-family: 'Playfair Display', serif; font-size: 2.1rem; font-weight: 700; color: var(--cream); margin: 0; }
.header-sub { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: var(--sprout); margin-top: 0.5rem; letter-spacing: 2px; text-transform: uppercase; }
.header-meta { font-size: 0.78rem; color: var(--fog); margin-top: 0.8rem; }
.header-meta a { color: var(--wheat); text-decoration: none; }

.stats-row { display: flex; gap: 1rem; margin: 1.2rem 0; flex-wrap: wrap; }
.stat-pill { background: #2d1e0f; border: 1px solid #3a2a15; border-radius: 3px; padding: 0.9rem 1.4rem; min-width: 120px; flex: 1; }
.stat-pill-top { font-family: 'IBM Plex Mono', monospace; font-size: 1.8rem; font-weight: 500; line-height: 1; }
.stat-pill-label { font-size: 0.72rem; color: var(--fog); text-transform: uppercase; letter-spacing: 1.5px; margin-top: 0.3rem; }
.stat-pill.crop  { border-top: 3px solid var(--sprout); }
.stat-pill.crop  .stat-pill-top { color: var(--sprout); }
.stat-pill.weed  { border-top: 3px solid var(--danger); }
.stat-pill.weed  .stat-pill-top { color: #e74c3c; }
.stat-pill.total { border-top: 3px solid var(--wheat); }
.stat-pill.total .stat-pill-top { color: var(--wheat); }
.stat-pill.speed { border-top: 3px solid var(--sky); }
.stat-pill.speed .stat-pill-top { color: var(--sky); }

.health-band { background: #2d1e0f; border: 1px solid #3a2a15; border-radius: 3px; padding: 1rem 1.4rem; margin: 0.8rem 0; display: flex; align-items: center; gap: 1.2rem; }
.health-label { font-size: 0.78rem; color: var(--fog); min-width: 110px; }
.health-bar-bg { flex: 1; height: 8px; background: #3a2a15; border-radius: 2px; overflow: hidden; }
.health-bar-fill { height: 100%; border-radius: 2px; }
.health-value { font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; color: var(--cream); min-width: 42px; text-align: right; }

.suggestion-box { padding: 0.9rem 1.2rem; border-radius: 3px; margin-top: 1rem; border-left: 4px solid; font-size: 0.87rem; line-height: 1.5; }
.suggestion-box.good   { background:#1a2e10; border-color:var(--sprout); color:#a8d488; }
.suggestion-box.warn   { background:#2e1f0a; border-color:var(--wheat);  color:#e8c57a; }
.suggestion-box.danger { background:#2e0f0f; border-color:var(--danger); color:#e88a8a; }
.suggestion-box.neutral{ background:#1a1a2e; border-color:var(--sky);    color:#93c5fd; }

.det-row { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0.9rem; margin: 0.25rem 0; background: #2d1e0f; border-radius: 2px; font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; }
.det-row.crop-row { border-left: 3px solid var(--sprout); color: #a8d488; }
.det-row.weed-row { border-left: 3px solid var(--danger); color: #e88a8a; }
.det-row.other-row{ border-left: 3px solid var(--wheat);  color: #e8c57a; }
.det-conf { color: var(--fog); font-size: 0.72rem; }

.field-note { background: #23160a; border: 1px dashed #4a3520; border-radius: 2px; padding: 1rem 1.2rem; font-size: 0.83rem; color: var(--fog); margin: 1rem 0; line-height: 1.6; }
.field-note strong { color: var(--cream); }

.sidebar-section { font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; color: var(--wheat); text-transform: uppercase; letter-spacing: 2px; margin: 1.2rem 0 0.5rem; padding-bottom: 0.3rem; border-bottom: 1px solid #3a2a15; }

.stButton > button { background: var(--leaf) !important; color: var(--cream) !important; border: none !important; border-radius: 2px !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.85rem !important; font-weight: 500 !important; padding: 0.55rem 1.4rem !important; }
.stButton > button:hover { background: var(--sprout) !important; }

[data-testid="stFileUploader"] { border: 2px dashed #4a3520 !important; border-radius: 3px !important; background: #1f150a !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--soil); }
::-webkit-scrollbar-thumb { background: #3a2a15; border-radius: 2px; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# -- Model loader --------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_model(path):
    try:
        from ultralytics import YOLO
        return YOLO(path), None
    except Exception as e:
        return None, str(e)

def find_model():
    for p in ["models/best.pt", "best.pt", "../models/best.pt"]:
        if Path(p).exists():
            return p
    return None


# -- Class normaliser ----------------------------------------------------------
CROP_KEYWORDS = ["crop", "maize", "corn", "wheat", "rice", "plant", "soybean", "cotton", "sugarcane"]
WEED_KEYWORDS = ["weed", "grass", "invasive", "unwanted", "broadleaf", "nutsedge", "thistle"]

def normalise_class(raw_name: str, cls_id: int = -1) -> str:
    name = raw_name.lower().strip()

    # Keyword matching
    for kw in CROP_KEYWORDS:
        if kw in name:
            return "crop"
    for kw in WEED_KEYWORDS:
        if kw in name:
            return "weed"

    # Your model uses numeric names ("0", "1") — map by index
    # Standard Roboflow crop/weed datasets: 0 = crop, 1 = weed
    idx = int(name) if name.isdigit() else cls_id
    if idx == 0:
        return "crop"
    elif idx == 1:
        return "weed"

    return "other"


# -- Detection colors ----------------------------------------------------------
COLORS = {
    "crop":  (116, 184, 66),
    "weed":  (192, 57, 43),
    "other": (212, 168, 67),
}

def run_detect(model, bgr_img, conf, iou):
    results = model.predict(bgr_img, conf=conf, iou=iou, verbose=False)[0]
    out     = bgr_img.copy()
    found   = []

    if results.boxes:
        for box in results.boxes:
            cls_id   = int(box.cls[0])
            raw_name = model.names.get(cls_id, str(cls_id))
            cls      = normalise_class(raw_name, cls_id)
            score    = float(box.conf[0])
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            rgb      = COLORS.get(cls, COLORS["other"])
            bgr_c    = (rgb[2], rgb[1], rgb[0])

            cv2.rectangle(out, (x1,y1), (x2,y2), bgr_c, 2)
            cv2.rectangle(out, (x1,y1), (x1+12,y1+12), bgr_c, -1)
            cv2.rectangle(out, (x2-12,y2-12), (x2,y2), bgr_c, -1)

            label = "CROP" if cls=="crop" else ("WEED" if cls=="weed" else raw_name.upper())
            tag   = f"{label}  {score:.0%}"
            tw,th = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)[0]
            cv2.rectangle(out,(x1,y1-th-10),(x1+tw+8,y1), bgr_c, -1)
            cv2.putText(out, tag, (x1+4,y1-4), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (15,10,5), 1, cv2.LINE_AA)

            found.append({"class": cls, "raw_name": raw_name, "conf": score, "box": (x1,y1,x2,y2)})

    return out, found


# -- Field health suggestion ---------------------------------------------------
def field_suggestion(n_crops, n_weeds):
    total = n_crops + n_weeds
    if total == 0:
        return "neutral", "No plants detected -- try a clearer image or lower the confidence threshold."
    pct = n_weeds / total * 100
    if pct < 15:
        return "good",   f"Field looks healthy. Weed density is only {pct:.0f}% -- spot treatment is sufficient."
    elif pct < 40:
        return "warn",   f"Moderate weed presence ({pct:.0f}%). Targeted herbicide application recommended."
    else:
        return "danger", f"High weed infestation ({pct:.0f}%). Immediate intervention advised."


# -- Session state -------------------------------------------------------------
if "scan_log" not in st.session_state:
    st.session_state.scan_log = []


# -- Load model BEFORE sidebar so it is available everywhere ------------------
model_path = find_model()
model, merr = None, "No model -- upload best.pt in the sidebar."
if model_path:
    model, merr = load_model(model_path)


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown(f"""
    <div style="padding:1rem 0 0.5rem">
        <div style="font-family:'Playfair Display',serif;font-size:1.25rem;color:#f5efe0">
            🌾 FarmEye
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                    color:#7cb842;letter-spacing:2px;margin-top:2px">
            AI-POWERED PRECISION AGRICULTURE
        </div>
    </div>
    <hr style="border-color:#3a2a15;margin:0.5rem 0 1rem">
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Detection Settings</div>', unsafe_allow_html=True)
    conf_thresh = st.slider("Confidence", 0.10, 0.90, 0.30, 0.05,
                            help="How certain the model must be before reporting a detection")
    iou_thresh  = st.slider("IOU overlap", 0.10, 0.90, 0.45, 0.05,
                            help="Controls how much boxes can overlap before being merged")

    st.markdown('<div class="sidebar-section">Model</div>', unsafe_allow_html=True)
    if model_path:
        st.success(f"Loaded: `{Path(model_path).name}`")
    else:
        up = st.file_uploader("Upload best.pt", type=["pt"])
        if up:
            tmp = tempfile.mkdtemp()
            model_path = os.path.join(tmp, "best.pt")
            open(model_path, "wb").write(up.read())
            model, merr = load_model(model_path)
            st.success("Model ready!")

    # Show actual class names from loaded model
    if model:
        st.markdown('<div class="sidebar-section">Model Classes</div>', unsafe_allow_html=True)
        for idx, name in model.names.items():
            mapped = normalise_class(name, idx)
            color  = "#7cb842" if mapped=="crop" else ("#c0392b" if mapped=="weed" else "#d4a843")
            st.markdown(
                f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;'
                f'color:#c8bfaf;padding:2px 0">'
                f'<span style="color:#0a0a0a;background:{color};padding:1px 6px;'
                f'border-radius:2px;margin-right:6px">{idx}</span>'
                f'{name} <span style="color:{color}">({mapped})</span></div>',
                unsafe_allow_html=True
            )

    st.markdown('<div class="sidebar-section">About</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:0.78rem;color:#c8bfaf;line-height:1.7">
        Built by <strong style="color:#f5efe0">{YOUR_NAME}</strong><br>
        {YOUR_YEAR}<br>
        {YOUR_COLLEGE}<br><br>
        <a href="https://{YOUR_LINKEDIN}" style="color:#d4a843">LinkedIn</a> &nbsp;·&nbsp;
        <a href="https://{YOUR_GITHUB}"   style="color:#d4a843">GitHub</a>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.scan_log:
        st.markdown('<div class="sidebar-section">Session Log</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#c8bfaf">
            Scans: <strong style="color:#f5efe0">{len(st.session_state.scan_log)}</strong><br>
            Weeds found: <strong style="color:#e74c3c">{sum(s['weeds'] for s in st.session_state.scan_log)}</strong><br>
            Crops found: <strong style="color:#7cb842">{sum(s['crops'] for s in st.session_state.scan_log)}</strong>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Clear log"):
            st.session_state.scan_log = []
            st.rerun()


# =============================================================================
# MAIN AREA
# =============================================================================
st.markdown(f"""
<div class="header-wrap">
    <div class="header-title">🌾 FarmEye</div>
    <div class="header-sub">AI-Powered Crop & Weed Detection System</div>
    <div class="header-meta">
        Built by <strong style="color:#f5efe0">{YOUR_NAME}</strong> &nbsp;·&nbsp;
        {YOUR_COLLEGE} &nbsp;·&nbsp; {YOUR_YEAR}
        &nbsp;|&nbsp;
        <a href="https://{YOUR_GITHUB}">GitHub</a> &nbsp;·&nbsp;
        <a href="https://{YOUR_LINKEDIN}">LinkedIn</a>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📷  Image Scan", "📋  Scan History", "ℹ️  How It Works"])


# ----------------------------- TAB 1: Image Scan -----------------------------
with tab1:
    uploaded = st.file_uploader(
        "Drop a field photo here -- JPG, PNG, or WEBP",
        type=["jpg","jpeg","png","webp"]
    )

    if not uploaded:
        st.markdown("""
        <div class="field-note">
            <strong>Quick instructions:</strong><br>
            1. Upload any farm / field image above<br>
            2. Adjust confidence in the sidebar if needed<br>
            3. Click Run Field Scan and read the field health report
        </div>
        """, unsafe_allow_html=True)

    if uploaded:
        raw_bytes = np.frombuffer(uploaded.read(), np.uint8)
        bgr       = cv2.imdecode(raw_bytes, cv2.IMREAD_COLOR)
        rgb       = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        h, w      = bgr.shape[:2]

        col_orig, col_result = st.columns(2)
        with col_orig:
            st.markdown("**Original**")
            st.image(rgb, use_container_width=True)
            st.caption(f"{uploaded.name} · {w}x{h}px · {len(raw_bytes)//1024} KB")

        if not model:
            st.warning(f"Model not loaded: {merr}")
        else:
            if st.button("🔍  Run Field Scan", use_container_width=True):
                with st.spinner("Scanning field..."):
                    t0           = time.time()
                    out_bgr, dets = run_detect(model, bgr, conf_thresh, iou_thresh)
                    elapsed      = time.time() - t0

                out_rgb = cv2.cvtColor(out_bgr, cv2.COLOR_BGR2RGB)
                with col_result:
                    st.markdown("**Detection Result**")
                    st.image(out_rgb, use_container_width=True)
                    st.caption(f"Inference: {elapsed*1000:.0f} ms · conf >= {conf_thresh}")

                crops  = sum(1 for d in dets if d["class"] == "crop")
                weeds  = sum(1 for d in dets if d["class"] == "weed")
                w_pct  = weeds / len(dets) * 100 if dets else 0
                c_pct  = 100 - w_pct

                st.markdown(f"""
                <div class="stats-row">
                    <div class="stat-pill total">
                        <div class="stat-pill-top">{len(dets)}</div>
                        <div class="stat-pill-label">Total detected</div>
                    </div>
                    <div class="stat-pill crop">
                        <div class="stat-pill-top">{crops}</div>
                        <div class="stat-pill-label">Crop plants</div>
                    </div>
                    <div class="stat-pill weed">
                        <div class="stat-pill-top">{weeds}</div>
                        <div class="stat-pill-label">Weeds</div>
                    </div>
                    <div class="stat-pill speed">
                        <div class="stat-pill-top">{elapsed*1000:.0f}<span style="font-size:0.9rem">ms</span></div>
                        <div class="stat-pill-label">Inference time</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("#### Field Composition")
                st.markdown(f"""
                <div class="health-band">
                    <div class="health-label">🌱 Crop coverage</div>
                    <div class="health-bar-bg">
                        <div class="health-bar-fill" style="width:{c_pct:.0f}%;background:#4a7c2f"></div>
                    </div>
                    <div class="health-value">{c_pct:.0f}%</div>
                </div>
                <div class="health-band">
                    <div class="health-label">🌿 Weed density</div>
                    <div class="health-bar-bg">
                        <div class="health-bar-fill" style="width:{w_pct:.0f}%;background:#c0392b"></div>
                    </div>
                    <div class="health-value">{w_pct:.0f}%</div>
                </div>
                """, unsafe_allow_html=True)

                stype, smsg = field_suggestion(crops, weeds)
                st.markdown(f"""
                <div class="suggestion-box {stype}">
                    <strong>Field Health Assessment:</strong> {smsg}
                </div>
                """, unsafe_allow_html=True)

                if dets:
                    st.markdown("#### Detection Log")
                    for i, d in enumerate(dets[:20]):
                        x1,y1,x2,y2 = d["box"]
                        row_cls = "crop-row" if d["class"]=="crop" else ("weed-row" if d["class"]=="weed" else "other-row")
                        icon    = "🌱" if d["class"]=="crop" else ("🌿" if d["class"]=="weed" else "🔶")
                        raw_hint = f' <span style="color:#6a5a3a;font-size:0.7rem">[{d["raw_name"]}]</span>' \
                                   if d["raw_name"].lower() not in ("crop","weed") else ""
                        st.markdown(
                            f'<div class="det-row {row_cls}">'
                            f'<span>{icon} #{i+1:02d} {d["class"].upper()}{raw_hint}</span>'
                            f'<span class="det-conf">conf {d["conf"]:.2%} | [{x1},{y1} to {x2},{y2}]</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    if len(dets) > 20:
                        st.caption(f"... and {len(dets)-20} more")

                st.session_state.scan_log.append({
                    "time":     datetime.datetime.now().strftime("%H:%M:%S"),
                    "file":     uploaded.name,
                    "crops":    crops,
                    "weeds":    weeds,
                    "speed_ms": f"{elapsed*1000:.0f}",
                    "weed_pct": f"{w_pct:.0f}"
                })

                buf = io.BytesIO()
                Image.fromarray(out_rgb).save(buf, format="PNG")
                st.download_button(
                    "Download annotated image",
                    buf.getvalue(),
                    file_name=f"farmeye_{uploaded.name}",
                    mime="image/png",
                    use_container_width=True
                )


# ----------------------------- TAB 2: Scan History ---------------------------
with tab2:
    st.markdown("#### Session Scan History")
    if not st.session_state.scan_log:
        st.markdown('<div class="field-note">No scans yet. Run a scan in the Image Scan tab.</div>', unsafe_allow_html=True)
    else:
        total_scans = len(st.session_state.scan_log)
        total_weeds = sum(s["weeds"] for s in st.session_state.scan_log)
        total_crops = sum(s["crops"] for s in st.session_state.scan_log)
        st.markdown(f"""
        <div class="stats-row">
            <div class="stat-pill total"><div class="stat-pill-top">{total_scans}</div><div class="stat-pill-label">Images scanned</div></div>
            <div class="stat-pill crop"><div class="stat-pill-top">{total_crops}</div><div class="stat-pill-label">Crops found</div></div>
            <div class="stat-pill weed"><div class="stat-pill-top">{total_weeds}</div><div class="stat-pill-label">Weeds found</div></div>
        </div>
        """, unsafe_allow_html=True)
        for s in reversed(st.session_state.scan_log):
            rc = "#c0392b" if int(s["weed_pct"]) > 40 else "#4a7c2f"
            st.markdown(
                f'<div class="det-row" style="border-left:3px solid {rc}">'
                f'<span style="color:#f5efe0">[{s["time"]}] {s["file"]}</span>'
                f'<span class="det-conf">🌱 {s["crops"]}  🌿 {s["weeds"]} | weed {s["weed_pct"]}% | {s["speed_ms"]}ms</span>'
                f'</div>', unsafe_allow_html=True
            )
        log_json = json.dumps(st.session_state.scan_log, indent=2)
        st.download_button("Export scan log (JSON)", log_json, "farmeye_log.json", "application/json")


# ----------------------------- TAB 3: How It Works ---------------------------
with tab3:
    st.markdown("#### How This System Works")
    st.markdown("""
    <div class="field-note">
        <strong>Why I built this:</strong><br>
        Traditional farming applies herbicides across entire fields without knowing where weeds actually are.
        This wastes money, harms soil health, and pollutes groundwater. I wanted to see if a lightweight
        AI model could distinguish crops from weeds well enough to guide targeted spraying.
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("01", "Image Input",    "User uploads a field photograph -- any angle, any crop type."),
        ("02", "Preprocessing",  "OpenCV decodes and resizes the image to 640x640 px before inference."),
        ("03", "YOLOv8 Inference","The fine-tuned model predicts bounding boxes and class probabilities."),
        ("04", "NMS Filtering",  "Non-Maximum Suppression removes overlapping boxes below the IOU threshold."),
        ("05", "Field Report",   "The app counts crops vs weeds, computes weed density, and gives a health recommendation."),
        ("06", "Download",       "Annotated image saved as PNG for use in field reports or spraying maps."),
    ]
    for num, title, desc in steps:
        st.markdown(f"""
        <div style="display:flex;gap:1.2rem;align-items:flex-start;margin:0.7rem 0">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#7cb842;min-width:26px;padding-top:2px">{num}</div>
            <div>
                <strong style="color:#f5efe0;font-size:0.88rem">{title}</strong>
                <div style="color:#c8bfaf;font-size:0.82rem;margin-top:2px">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    stack = [
        ("Model",    "YOLOv8n -- Ultralytics (fine-tuned on CropAndWeed dataset)"),
        ("Training", "Google Colab T4 GPU · 50 epochs · 640px input"),
        ("Vision",   "OpenCV 4.8 for image decode and annotation"),
        ("App",      "Streamlit 1.32 -- chosen for fast deployment without a backend"),
        ("Dataset",  "Roboflow CropAndWeed -- ~2,000 annotated field images"),
        ("Language", "Python 3.10"),
    ]
    for label, val in stack:
        st.markdown(
            f'<div class="det-row" style="border-left:3px solid #4a7c2f">'
            f'<span style="color:#d4a843;min-width:90px">{label}</span>'
            f'<span style="color:#c8bfaf">{val}</span>'
            f'</div>', unsafe_allow_html=True
        )

    st.markdown(f"""
    <div style="font-size:0.78rem;color:#c8bfaf;text-align:center;padding:1.5rem 0 0.5rem">
        Built by <strong style="color:#f5efe0">{YOUR_NAME}</strong> · {YOUR_COLLEGE} · {YOUR_YEAR}<br>
        <a href="https://{YOUR_GITHUB}" style="color:#d4a843">GitHub</a> &nbsp;·&nbsp;
        <a href="https://{YOUR_LINKEDIN}" style="color:#d4a843">LinkedIn</a>
    </div>
    """, unsafe_allow_html=True)
