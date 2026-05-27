import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
import io

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="CMOS Flow Mobile",
    page_icon="🧪",
    layout="wide"
)

# =========================================================
# THEME
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    background: #0f1117;
    color: #f5f5f5;
    font-family: Inter, sans-serif;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #30363d;
}

.card {
    background: linear-gradient(180deg,#1c2128,#11161c);
    border: 1px solid #30363d;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}

.metric {
    background: #161b22;
    border-radius: 16px;
    padding: 16px;
    text-align:center;
    border:1px solid #30363d;
}

.metric h2 {
    color:#58a6ff;
    margin:0;
}

.metric p {
    margin:0;
    color:#8b949e;
}

.phase {
    display:inline-block;
    padding:6px 12px;
    border-radius:20px;
    background:#21262d;
    border:1px solid #30363d;
    margin-right:8px;
    margin-bottom:8px;
    color:#58a6ff;
    font-size:12px;
    font-weight:bold;
}

img {
    border-radius:14px;
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
# LOAD EXCEL
# =========================================================

@st.cache_data
def load_excel():

    df = pd.read_excel(EXCEL_FILE)

    df.columns = [
        str(c).strip().replace("\n", " ")
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

process_col = find_col(["process #", "process"])
phase_col = find_col(["phase"])
module_col = find_col(["module"])
step_col = find_col(["process step"])
equipment_col = find_col(["equipment"])
location_col = find_col(["location"])
substep_col = find_col(["substep"])

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
# FILTER
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

st.title("🧪 CMOS Mobile Process Explorer")

st.caption(
    "Semiconductor fabrication flow with schematics"
)

# =========================================================
# METRICS
# =========================================================

c1, c2, c3 = st.columns(3)

with c1:

    st.markdown(f"""
    <div class='metric'>
        <h2>{len(filtered_df)}</h2>
        <p>Rows</p>
    </div>
    """, unsafe_allow_html=True)

with c2:

    modules = 0

    if module_col:
        modules = filtered_df[module_col].nunique()

    st.markdown(f"""
    <div class='metric'>
        <h2>{modules}</h2>
        <p>Modules</p>
    </div>
    """, unsafe_allow_html=True)

with c3:

    phases = 0

    if phase_col:
        phases = filtered_df[phase_col].nunique()

    st.markdown(f"""
    <div class='metric'>
        <h2>{phases}</h2>
        <p>Phases</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================================================
# PHASE CHIPS
# =========================================================

if phase_col:

    chips = ""

    for p in filtered_df[phase_col].dropna().astype(str).unique():

        chips += f"<span class='phase'>{p}</span>"

    st.markdown(chips, unsafe_allow_html=True)

# =========================================================
# PDF IMAGE EXTRACTION
# =========================================================

@st.cache_data
def extract_pdf_pages():

    pages = []

    try:

        doc = fitz.open(PDF_FILE)

        for i in range(len(doc)):

            page = doc.load_page(i)

            pix = page.get_pixmap(matrix=fitz.Matrix(2,2))

            img_bytes = pix.tobytes("png")

            pages.append(img_bytes)

        return pages

    except:
        return []

pdf_images = extract_pdf_pages()

# =========================================================
# PROCESS FLOW
# =========================================================

for idx, (_, row) in enumerate(filtered_df.iterrows()):

    process_no = ""
    step = "CMOS Step"
    module = ""
    phase = ""
    equipment = ""
    location = ""
    substep = ""

    if process_col:
        process_no = str(row.get(process_col, ""))

    if step_col:
        step = str(row.get(step_col, ""))

    if module_col:
        module = str(row.get(module_col, ""))

    if phase_col:
        phase = str(row.get(phase_col, ""))

    if equipment_col:
        equipment = str(row.get(equipment_col, ""))

    if location_col:
        location = str(row.get(location_col, ""))

    if substep_col:
        substep = str(row.get(substep_col, ""))

    with st.expander(f"Process {process_no} — {step}"):

        st.markdown(f"""
        <div class='card'>
            <h3>{step}</h3>

            <p><b>Phase:</b> {phase}</p>

            <p><b>Module:</b> {module}</p>

            <p><b>Equipment:</b> {equipment}</p>

            <p><b>Location:</b> {location}</p>

            <p><b>Substep:</b> {substep}</p>
        </div>
        """, unsafe_allow_html=True)

        # PDF IMAGE MAPPING
        if pdf_images:

            image_index = idx % len(pdf_images)

            st.image(
                pdf_images[image_index],
                caption=f"Schematic Page {image_index + 1}",
                use_container_width=True
            )

        st.subheader("Process Details")

        for col in df.columns:

            value = row.get(col, "")

            if pd.notna(value):

                st.write(f"**{col}**")
                st.info(str(value))

# =========================================================
# FULL PDF GALLERY
# =========================================================

st.divider()

st.header("🖼 CMOS Schematic Gallery")

if pdf_images:

    for i, img in enumerate(pdf_images):

        st.image(
            img,
            caption=f"PDF Page {i+1}",
            use_container_width=True
        )

else:

    st.warning("Could not extract images from PDF")

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

# =========================================================
# DEBUG
# =========================================================

with st.expander("🛠 Detected Columns"):

    st.write(df.columns.tolist())
