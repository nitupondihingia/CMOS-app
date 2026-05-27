# Full preserved-theme CMOS mobile app
# Save as app4.py

import streamlit as st
import pandas as pd
import base64
from pathlib import Path

st.set_page_config(
    page_title="CMOS Advanced Flow V2",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    padding-left: 0.7rem;
    padding-right: 0.7rem;
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

.phase-chip {
    display:inline-block;
    padding:8px 14px;
    border-radius:20px;
    background:#18211f;
    margin-right:8px;
    margin-bottom:8px;
    border:1px solid #2b3531;
    color:#5eead4;
    font-size:13px;
    font-weight:bold;
}

.pdf-box {
    border-radius:18px;
    overflow:hidden;
    border:1px solid #2b3531;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

</style>
""", unsafe_allow_html=True)

EXCEL_FILE = "CMOS_350_Process_Flow_Advanced.xlsx"
PDF_FILE = "manual_cmos_process_flow.pdf"

@st.cache_data
def load_excel():

    df = pd.read_excel(EXCEL_FILE)

    df.columns = [
        str(c).strip().replace("\n", " ")
        for c in df.columns
    ]

    return df

df = load_excel()

def find_column(keywords):

    for col in df.columns:

        lower = col.lower()

        if any(keyword in lower for keyword in keywords):
            return col

    return None

process_col = find_column(["process #", "process"])
step_col = find_column(["process step"])
module_col = find_column(["module"])
phase_col = find_column(["phase"])
equipment_col = find_column(["equipment"])
location_col = find_column(["location"])
substep_col = find_column(["substep"])

st.sidebar.title("⚙ CMOS Controls")

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
    "Operational Module",
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

st.title("🧪 CMOS Advanced Flow Explorer")

st.caption(
    "Mobile Semiconductor Process Dashboard"
)

m1, m2, m3 = st.columns(3)

with m1:

    st.markdown(f'''
    <div class='metric-card'>
        <h2>{len(filtered_df)}</h2>
        <p>Rows</p>
    </div>
    ''', unsafe_allow_html=True)

with m2:

    count_modules = 0

    if module_col:
        count_modules = filtered_df[module_col].nunique()

    st.markdown(f'''
    <div class='metric-card'>
        <h2>{count_modules}</h2>
        <p>Modules</p>
    </div>
    ''', unsafe_allow_html=True)

with m3:

    count_tools = 0

    if equipment_col:
        count_tools = filtered_df[equipment_col].nunique()

    st.markdown(f'''
    <div class='metric-card'>
        <h2>{count_tools}</h2>
        <p>Tools</p>
    </div>
    ''', unsafe_allow_html=True)

st.divider()

if phase_col:

    unique_phases = filtered_df[
        phase_col
    ].dropna().astype(str).unique().tolist()

    chips = ""

    for p in unique_phases:
        chips += f"<span class='phase-chip'>{p}</span>"

    st.markdown(chips, unsafe_allow_html=True)

for _, row in filtered_df.iterrows():

    process_no = ""
    step = "CMOS Step"
    module = ""
    equipment = ""
    location = ""
    phase = ""
    substep = ""

    if process_col:
        process_no = str(row.get(process_col, ""))

    if step_col:
        step = str(row.get(step_col, ""))

    if module_col:
        module = str(row.get(module_col, ""))

    if equipment_col:
        equipment = str(row.get(equipment_col, ""))

    if location_col:
        location = str(row.get(location_col, ""))

    if phase_col:
        phase = str(row.get(phase_col, ""))

    if substep_col:
        substep = str(row.get(substep_col, ""))

    title = f"Process {process_no} — {step}"

    with st.expander(title):

        st.markdown(f'''
        <div class='process-card'>
            <h3>{step}</h3>

            <p><b>Phase:</b> {phase}</p>
            <p><b>Module:</b> {module}</p>
            <p><b>Equipment:</b> {equipment}</p>
            <p><b>Location:</b> {location}</p>
            <p><b>Substep:</b> {substep}</p>
        </div>
        ''', unsafe_allow_html=True)

        for col in df.columns:

            value = row.get(col, "")

            if pd.notna(value):

                st.write(f"**{col}**")
                st.info(str(value))

st.divider()

st.header("🖼 CMOS Manual & Schematics")

if Path(PDF_FILE).exists():

    with open(PDF_FILE, "rb") as pdf_file:

        base64_pdf = base64.b64encode(
            pdf_file.read()
        ).decode("utf-8")

    pdf_display = f'''
    <div class="pdf-box">
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            width="100%"
            height="1000"
            type="application/pdf">
        </iframe>
    </div>
    '''

    st.markdown(
        pdf_display,
        unsafe_allow_html=True
    )

else:

    st.warning(
        "manual_cmos_process_flow.pdf not found"
    )

st.divider()

with st.expander("📊 Complete CMOS Process Table"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=700
    )

with st.expander("🛠 Detected Excel Columns"):

    st.write(df.columns.tolist())
