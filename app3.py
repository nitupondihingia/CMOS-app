import streamlit as st
import pandas as pd
import base64

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="CMOS Advanced Explorer",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# THEME
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    background:
        linear-gradient(180deg,#161c1a 0,#0e1211 360px),
        #0e1211;

    color: #edf3f0;

    font-family: Inter, sans-serif;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 5rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            rgba(94,234,212,0.13),
            transparent 190px
        ),
        #101513;

    border-right: 1px solid #2a342f;
}

.stTextInput input {

    background: #111614;

    color: white;

    border-radius: 12px;

    border: 1px solid #2b3531;
}

.stSelectbox div[data-baseweb="select"] {

    background: #111614;

    border-radius: 12px;

    border: 1px solid #2b3531;
}

.metric-card {

    background:
        linear-gradient(
            180deg,
            #1b2220,
            #141a18
        );

    border: 1px solid #2b3531;

    border-radius: 18px;

    padding: 18px;

    text-align: center;

    box-shadow:
        0 18px 44px rgba(0,0,0,0.35);
}

.metric-card h2 {

    color: #5eead4;

    margin: 0;
}

.metric-card p {

    color: #9aa8a2;

    margin: 0;
}

.process-card {

    background:
        linear-gradient(
            180deg,
            rgba(94,234,212,0.08),
            #141a18 48%
        );

    border-left: 5px solid #5eead4;

    border-radius: 20px;

    padding: 18px;

    margin-bottom: 20px;

    border: 1px solid #2d3834;

    box-shadow:
        0 12px 28px rgba(0,0,0,0.30);
}

.streamlit-expanderHeader {

    background: #171d1b;

    border-radius: 14px;

    border: 1px solid #2b3531;

    font-size: 18px;

    font-weight: bold;

    color: white;
}

[data-testid="stDataFrame"] {

    border-radius: 18px;

    overflow: hidden;

    border: 1px solid #2b3531;
}

.pdf-box {

    border-radius: 18px;

    overflow: hidden;

    border: 1px solid #2b3531;

    box-shadow:
        0 12px 28px rgba(0,0,0,0.30);
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD EXCEL
# =========================================================

EXCEL_FILE = "CMOS_350_Process_Flow_Advanced.xlsx"

@st.cache_data
def load_excel():

    df = pd.read_excel(EXCEL_FILE)

    # CLEAN COLUMN NAMES
    df.columns = [
        str(c).strip().replace("\n", " ")
        for c in df.columns
    ]

    return df

df = load_excel()

# =========================================================
# AUTO DETECT COLUMNS
# =========================================================

def find_column(keyword):

    for col in df.columns:

        if keyword.lower() in col.lower():
            return col

    return None

module_col = find_column("module")
phase_col = find_column("phase")
step_col = find_column("process step")
equipment_col = find_column("equipment")
location_col = find_column("location")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("CMOS Controls")

search = st.sidebar.text_input("Search")

modules = ["All"]

if module_col:

    modules += sorted(
        df[module_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

selected_module = st.sidebar.selectbox(
    "Module",
    modules
)

phases = ["All"]

if phase_col:

    phases += sorted(
        df[phase_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

selected_phase = st.sidebar.selectbox(
    "Phase",
    phases
)

# =========================================================
# FILTER
# =========================================================

filtered_df = df.copy()

if module_col and selected_module != "All":

    filtered_df = filtered_df[
        filtered_df[module_col]
        .astype(str)
        == selected_module
    ]

if phase_col and selected_phase != "All":

    filtered_df = filtered_df[
        filtered_df[phase_col]
        .astype(str)
        == selected_phase
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

st.title("🧪 CMOS Advanced Explorer")

st.caption(
    "Semiconductor Process Flow Dashboard"
)

# =========================================================
# METRICS
# =========================================================

m1, m2, m3 = st.columns(3)

with m1:

    st.markdown(f"""
    <div class='metric-card'>
        <h2>{len(filtered_df)}</h2>
        <p>Rows</p>
    </div>
    """, unsafe_allow_html=True)

with m2:

    module_count = 0

    if module_col:
        module_count = filtered_df[module_col].nunique()

    st.markdown(f"""
    <div class='metric-card'>
        <h2>{module_count}</h2>
        <p>Modules</p>
    </div>
    """, unsafe_allow_html=True)

with m3:

    equipment_count = 0

    if equipment_col:
        equipment_count = filtered_df[equipment_col].nunique()

    st.markdown(f"""
    <div class='metric-card'>
        <h2>{equipment_count}</h2>
        <p>Tools</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================================================
# PROCESS FLOW
# =========================================================

for _, row in filtered_df.iterrows():

    title = "CMOS Step"

    if step_col:
        title = str(
            row.get(step_col, "CMOS Step")
        )

    module = ""

    if module_col:
        module = str(
            row.get(module_col, "")
        )

    equipment = ""

    if equipment_col:
        equipment = str(
            row.get(equipment_col, "")
        )

    location = ""

    if location_col:
        location = str(
            row.get(location_col, "")
        )

    with st.expander(title):

        st.markdown(f"""
        <div class='process-card'>
            <h3>{module}</h3>
            <p><b>Equipment:</b> {equipment}</p>
            <p><b>Location:</b> {location}</p>
        </div>
        """, unsafe_allow_html=True)

        for col in df.columns:

            value = row.get(col, "")

            if pd.notna(value):

                st.write(f"**{col}**")
                st.info(str(value))

# =========================================================
# PDF VIEWER
# =========================================================

st.divider()

st.subheader(
    "CMOS Process Flow Manual"
)

try:

    with open(
        "manual_cmos_process_flow.pdf",
        "rb"
    ) as pdf_file:

        base64_pdf = base64.b64encode(
            pdf_file.read()
        ).decode("utf-8")

    pdf_display = f"""
    <div class='pdf-box'>
    <iframe
    src="data:application/pdf;base64,{base64_pdf}"
    width="100%"
    height="900"
    type="application/pdf">
    </iframe>
    </div>
    """

    st.markdown(
        pdf_display,
        unsafe_allow_html=True
    )

except:

    st.warning(
        "manual_cmos_process_flow.pdf not found"
    )

# =========================================================
# DEBUG COLUMNS
# =========================================================

with st.expander("Detected Excel Columns"):

    st.write(df.columns.tolist())

# =========================================================
# FULL TABLE
# =========================================================

with st.expander("Full Process Table"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=600
    )
