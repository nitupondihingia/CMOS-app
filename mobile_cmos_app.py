import streamlit as st
import pandas as pd

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="CMOS Explorer",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# CUSTOM DARK MOBILE UI
# =====================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #0f1115;
    color: white;
    font-family: Inter, sans-serif;
}

/* Main */
.block-container {
    padding-top: 1rem;
    padding-bottom: 5rem;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #161a22;
}

/* Search box */
.stTextInput input {
    background-color: #1b1f27;
    color: white;
    border-radius: 12px;
    border: 1px solid #2f3542;
}

/* Dropdown */
.stSelectbox div[data-baseweb="select"] {
    background-color: #1b1f27;
    border-radius: 12px;
}

/* Cards */
.process-card {
    background-color: #1a1d24;
    border: 1px solid #00d4aa;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 16px;
}

/* Metric cards */
.metric-card {
    background-color: #1a1d24;
    border-radius: 14px;
    padding: 12px;
    text-align: center;
    border: 1px solid #2f3542;
}

/* Expander */
.streamlit-expanderHeader {
    font-size: 18px;
    font-weight: bold;
    color: white;
}

/* Table */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Buttons */
.stButton button {
    background-color: #00d4aa;
    color: black;
    border-radius: 12px;
    border: none;
    font-weight: bold;
}

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD EXCEL
# =====================================================

EXCEL_FILE = "CMOS_350_Process_Flow_Advanced.xlsx"

@st.cache_data
def load_data():

    df = pd.read_excel(EXCEL_FILE)

    df.columns = [
        str(col).strip().replace("\n", " ")
        for col in df.columns
    ]

    return df

df = load_data()

# =====================================================
# AUTO DETECT IMPORTANT COLUMNS
# =====================================================

module_col = None
phase_col = None
step_col = None
equipment_col = None

for col in df.columns:

    lower = col.lower()

    if "module" in lower and module_col is None:
        module_col = col

    if "phase" in lower and phase_col is None:
        phase_col = col

    if "process step" in lower and step_col is None:
        step_col = col

    if "equipment" in lower and equipment_col is None:
        equipment_col = col

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.title("CMOS Filters")

search = st.sidebar.text_input(
    "Search"
)

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

# =====================================================
# FILTER LOGIC
# =====================================================

filtered_df = df.copy()

if selected_module != "All" and module_col:
    filtered_df = filtered_df[
        filtered_df[module_col].astype(str) == selected_module
    ]

if selected_phase != "All" and phase_col:
    filtered_df = filtered_df[
        filtered_df[phase_col].astype(str) == selected_phase
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

# =====================================================
# HEADER
# =====================================================

st.title("🧪 CMOS Process Explorer")

st.caption("Mobile Fab Process Dashboard")

# =====================================================
# METRICS
# =====================================================

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

# =====================================================
# PROCESS CARDS
# =====================================================

for _, row in filtered_df.iterrows():

    title = "CMOS Step"

    if step_col:
        title = str(row.get(step_col, "CMOS Step"))

    module = ""

    if module_col:
        module = str(row.get(module_col, ""))

    equipment = ""

    if equipment_col:
        equipment = str(row.get(equipment_col, ""))

    with st.expander(
        f"{title}",
        expanded=False
    ):

        st.markdown(f"""
        <div class='process-card'>
            <h4>{module}</h4>
            <p><b>Equipment:</b> {equipment}</p>
        </div>
        """, unsafe_allow_html=True)

        for col in df.columns:

            value = row.get(col, "")

            if pd.notna(value):

                st.write(f"**{col}**")

                st.info(str(value))

# =====================================================
# RAW TABLE
# =====================================================

with st.expander("Full Table"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=500
    )
