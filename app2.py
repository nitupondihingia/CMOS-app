import streamlit as st
import pandas as pd

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="CMOS Process Explorer",
    page_icon="🧪",
    layout="wide"
)

# =========================
# LOAD DATA
# =========================

EXCEL_FILE = "CMOS_350_Process_Flow_Advanced.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_FILE)

df = load_data()

# =========================
# SIDEBAR
# =========================

st.sidebar.title("CMOS Explorer")

modules = ["All"] + sorted(
    df["Operational Module"].dropna().astype(str).unique().tolist()
)

phases = ["All"] + sorted(
    df["Phase"].dropna().astype(str).unique().tolist()
)

selected_module = st.sidebar.selectbox(
    "Operational Module",
    modules
)

selected_phase = st.sidebar.selectbox(
    "Phase",
    phases
)

search = st.sidebar.text_input(
    "Search Process / Equipment / Step"
)

# =========================
# FILTERS
# =========================

filtered_df = df.copy()

if selected_module != "All":
    filtered_df = filtered_df[
        filtered_df["Operational Module"].astype(str) == selected_module
    ]

if selected_phase != "All":
    filtered_df = filtered_df[
        filtered_df["Phase"].astype(str) == selected_phase
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

# =========================
# HEADER
# =========================

st.title("CMOS Process Explorer")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Rows",
        len(filtered_df)
    )

with col2:
    st.metric(
        "Modules",
        filtered_df["Operational Module"].nunique()
    )

with col3:
    st.metric(
        "Equipment",
        filtered_df["Equipment"].nunique()
    )

st.divider()

# =========================
# PROCESS CARDS
# =========================

for _, row in filtered_df.iterrows():

    process_step = str(row.get("Process Step", "Unknown"))
    module = str(row.get("Operational Module", ""))
    step_id = str(row.get("Step ID", ""))
    equipment = str(row.get("Equipment", ""))
    location = str(row.get("Location", ""))
    phase = str(row.get("Phase", ""))

    with st.expander(
        f"{process_step} | {module}",
        expanded=False
    ):

        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"### {process_step}")

            st.write(f"**Step ID:** {step_id}")
            st.write(f"**Phase:** {phase}")
            st.write(f"**Module:** {module}")
            st.write(f"**Equipment:** {equipment}")
            st.write(f"**Location:** {location}")

        with c2:
            st.markdown("### Full Information")

            for col in filtered_df.columns:

                value = row.get(col, "")

                if pd.notna(value):
                    st.write(f"**{col}:** {value}")

# =========================
# RAW TABLE
# =========================

st.divider()

st.subheader("Full Table")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=500
)
