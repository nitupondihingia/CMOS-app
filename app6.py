import streamlit as st
import pandas as pd
import fitz
import tempfile
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="CMOS 3D Wafer Flow",
    page_icon="🧪",
    layout="wide"
)

# =========================================================
# THEME - OPTION 6 FUTURISTIC
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    background:
        radial-gradient(circle at top left,#12322d 0,#0b0f14 35%),
        linear-gradient(180deg,#111827,#05070a);
    color:#f8fafc;
    font-family:Inter,sans-serif;
}

.block-container {
    padding-top:1rem;
    padding-bottom:4rem;
}

section[data-testid="stSidebar"] {
    background:#0b1017;
    border-right:1px solid #1f2937;
}

.main-title {
    font-size:42px;
    font-weight:900;
    color:#67e8f9;
    text-shadow:0 0 20px rgba(103,232,249,0.5);
}

.wafer-card {

    background:
        linear-gradient(
            145deg,
            rgba(22,28,36,0.95),
            rgba(10,14,20,0.95)
        );

    border:1px solid #334155;

    border-left:6px solid #67e8f9;

    border-radius:24px;

    padding:20px;

    margin-bottom:22px;

    box-shadow:
        0 20px 50px rgba(0,0,0,0.55),
        0 0 25px rgba(103,232,249,0.08);

    backdrop-filter: blur(8px);
}

.metric-box {

    background:
        linear-gradient(145deg,#111827,#0b1220);

    border-radius:22px;

    border:1px solid #334155;

    padding:20px;

    text-align:center;
}

.metric-box h1 {
    color:#67e8f9;
    margin:0;
}

.metric-box p {
    color:#94a3b8;
    margin:0;
}

.phase-tag {
    display:inline-block;
    padding:6px 14px;
    border-radius:999px;
    background:#0f172a;
    border:1px solid #334155;
    color:#67e8f9;
    margin-right:6px;
    margin-bottom:6px;
    font-size:12px;
    font-weight:700;
}

.flow-line {
    height:2px;
    background:linear-gradient(90deg,#67e8f9,transparent);
    margin-top:10px;
    margin-bottom:14px;
}

.image-frame {
    border-radius:18px;
    overflow:hidden;
    border:1px solid #334155;
    box-shadow:
        0 12px 30px rgba(0,0,0,0.45);
}

.stExpander {
    border:none !important;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

</style>
""", unsafe_allow_html=True)

# =========================================================
# FILES
# =========================================================

EXCEL_FILE = "CMOS_350_Process_Flow_Advanced.xlsx"
PDF_FILE = "manual_cmos_process_flow.pdf"

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_excel():

    df = pd.read_excel(EXCEL_FILE)

    df.columns = [
        str(c).strip().replace("\n"," ")
        for c in df.columns
    ]

    return df

df = load_excel()

# =========================================================
# COLUMN DETECTION
# =========================================================

def find_col(keys):

    for col in df.columns:

        lower = col.lower()

        for key in keys:

            if key in lower:
                return col

    return None

process_col = find_col(["process #","process"])
step_col = find_col(["process step"])
module_col = find_col(["operational module","module"])
phase_col = find_col(["phase"])
equipment_col = find_col(["equipment"])
location_col = find_col(["location"])
substep_col = find_col(["substep"])

# =========================================================
# CORRECT PDF PAGE MAPPING
# Based on original desktop version
# =========================================================

SCHEMATIC_REF_MAP = {
    0: 1,
    1: 2,
    2: 3,
    3: 4,
    4: 8,
    5: 9,
    6: 10,
    7: 11,
    8: 12,
    9: 13,
    10: 14,
    11: 15,
    12: 16,
    13: 17,
    14: 18,
    15: 20,
    16: 21,
    17: 22,
    18: 24,
    19: 25,
    20: 27,
    21: 28,
    22: 29,
    23: 31,
    24: 32,
    25: 33,
    26: 35,
    27: 36,
    28: 38,
    29: 40,
    30: 41,
    31: 42,
    32: 43,
    33: 45,
    34: 46,
    35: 48,
    36: 49,
    37: 50,
    38: 51,
    39: 52,
    40: 53
}

# =========================================================
# PDF IMAGE EXTRACTION
# =========================================================

@st.cache_data
def extract_pdf_pages():

    pages = {}

    try:

        doc = fitz.open(PDF_FILE)

        for i in range(len(doc)):

            page = doc.load_page(i)

            pix = page.get_pixmap(matrix=fitz.Matrix(2,2))

            img = pix.tobytes("png")

            pages[i + 1] = img

        return pages

    except Exception as e:

        st.error(str(e))

        return {}

pdf_pages = extract_pdf_pages()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙ CMOS Controls")

search = st.sidebar.text_input("Search")

phase_options = ["All"]

if phase_col:
    phase_options += sorted(
        df[phase_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

selected_phase = st.sidebar.selectbox(
    "Phase",
    phase_options
)

module_options = ["All"]

if module_col:
    module_options += sorted(
        df[module_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

selected_module = st.sidebar.selectbox(
    "Module",
    module_options
)

# =========================================================
# FILTERING
# =========================================================

filtered_df = df.copy()

if phase_col and selected_phase != "All":

    filtered_df = filtered_df[
        filtered_df[phase_col].astype(str)
        == selected_phase
    ]

if module_col and selected_module != "All":

    filtered_df = filtered_df[
        filtered_df[module_col].astype(str)
        == selected_module
    ]

if search:

    filtered_df = filtered_df[
        filtered_df.astype(str).apply(
            lambda row: row.str.contains(
                search,
                case=False
            ).any(),
            axis=1
        )
    ]

# =========================================================
# HEADER
# =========================================================

st.markdown(
    "<div class='main-title'>🧪 CMOS 3D Wafer Flow Explorer</div>",
    unsafe_allow_html=True
)

st.caption(
    "Futuristic semiconductor fabrication mobile dashboard"
)

# =========================================================
# METRICS
# =========================================================

c1, c2, c3 = st.columns(3)

with c1:

    st.markdown(f"""
    <div class='metric-box'>
        <h1>{len(filtered_df)}</h1>
        <p>Process Rows</p>
    </div>
    """, unsafe_allow_html=True)

with c2:

    modules = 0

    if module_col:
        modules = filtered_df[module_col].nunique()

    st.markdown(f"""
    <div class='metric-box'>
        <h1>{modules}</h1>
        <p>Modules</p>
    </div>
    """, unsafe_allow_html=True)

with c3:

    phases = 0

    if phase_col:
        phases = filtered_df[phase_col].nunique()

    st.markdown(f"""
    <div class='metric-box'>
        <h1>{phases}</h1>
        <p>Phases</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================================================
# PROCESS FLOW
# =========================================================

for _, row in filtered_df.iterrows():

    process_no = ""

    if process_col:
        process_no = str(row.get(process_col,""))

    try:
        process_int = int(float(process_no))
    except:
        process_int = None

    step = str(row.get(step_col,"CMOS Step")) if step_col else "CMOS Step"

    module = str(row.get(module_col,"")) if module_col else ""

    phase = str(row.get(phase_col,"")) if phase_col else ""

    equipment = str(row.get(equipment_col,"")) if equipment_col else ""

    location = str(row.get(location_col,"")) if location_col else ""

    substep = str(row.get(substep_col,"")) if substep_col else ""

    with st.expander(f"⚡ Process {process_no} — {step}"):

        st.markdown(f"""
        <div class='wafer-card'>

            <h2>{step}</h2>

            <div class='flow-line'></div>

            <span class='phase-tag'>{phase}</span>
            <span class='phase-tag'>{module}</span>

            <p><b>Equipment:</b> {equipment}</p>

            <p><b>Location:</b> {location}</p>

            <p><b>Substep:</b> {substep}</p>

        </div>
        """, unsafe_allow_html=True)

        # =====================================================
        # CORRECT SCHEMATIC MAPPING
        # =====================================================

        if process_int in SCHEMATIC_REF_MAP:

            page_no = SCHEMATIC_REF_MAP[process_int]

            if page_no in pdf_pages:

                st.markdown(
                    "<div class='image-frame'>",
                    unsafe_allow_html=True
                )

                st.image(
                    pdf_pages[page_no],
                    caption=f"Schematic Page {page_no}",
                    use_container_width=True
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

        st.subheader("📋 Process Details")

        for col in df.columns:

            value = row.get(col,"")

            if pd.notna(value):

                st.write(f"**{col}**")

                st.info(str(value))

# =========================================================
# FULL GALLERY
# =========================================================

st.divider()

st.header("🖼 Full Schematic Gallery")

for page_no, img in pdf_pages.items():

    st.image(
        img,
        caption=f"PDF Page {page_no}",
        use_container_width=True
    )

# =========================================================
# FULL TABLE
# =========================================================

st.divider()

with st.expander("📊 Full CMOS Process Table"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=700
    )
