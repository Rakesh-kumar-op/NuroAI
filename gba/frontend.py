import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# =========================================================
# PAGE
# =========================================================

st.set_page_config(

    page_title="GutBrain AI",

    layout="wide"
)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "🧠 GutBrain AI"
)

page = st.sidebar.radio(

    "Navigation",

    [

        "Dashboard",

        "Upload Data",

        "Voice Analysis",

        "Microbiome",

        "Autonomic",

        "Inflammation",

        "Explainability"
    ]
)

# =========================================================
# TITLE
# =========================================================

st.title(
    "Gut-Brain Neurodegenerative Vulnerability Assessment"
)

# =========================================================
# INPUT FORM
# =========================================================

st.sidebar.subheader("Symptoms")

bloating = st.sidebar.slider(
    "Bloating",
    0,
    10,
    0
)

constipation = st.sidebar.slider(
    "Constipation",
    0,
    10,
    0
)

diarrhea = st.sidebar.slider(
    "Diarrhea",
    0,
    10,
    0
)

antibiotics = st.sidebar.slider(
    "Antibiotic Usage",
    0,
    10,
    0
)

fatigue = st.sidebar.slider(
    "Fatigue",
    0,
    10,
    0
)

tremors = st.sidebar.slider(
    "Tremors",
    0,
    10,
    0
)

stress_level = st.sidebar.slider(
    "Stress",
    0,
    10,
    5
)

sleep_quality = st.sidebar.slider(
    "Sleep Quality",
    0,
    10,
    5
)

# =========================================================
# AUDIO
# =========================================================

voice_file = st.sidebar.file_uploader(

    "Upload Voice WAV",

    type=["wav"]
)

# =========================================================
# RUN
# =========================================================

if st.sidebar.button("Run Analysis"):

    files = {}

    if voice_file:

        files["voice_file"] = (

            voice_file.name,

            voice_file,

            "audio/wav"
        )

    data = {

        "bloating":
            bloating,

        "constipation":
            constipation,

        "diarrhea":
            diarrhea,

        "antibiotics":
            antibiotics,

        "fatigue":
            fatigue,

        "tremors":
            tremors,

        "stress_level":
            stress_level,

        "sleep_quality":
            sleep_quality
    }

    response = requests.post(

        "http://127.0.0.1:8000/predict",

        files=files,

        data=data
    )

    result = response.json()

    # =====================================================
    # TOP CARDS
    # =====================================================

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Overall",
        f"{result['overall_score']}/100"
    )

    c2.metric(
        "Microbiome",
        f"{result['microbiome_score']}/100"
    )

    c3.metric(
        "Voice",
        f"{result['voice_score']}/100"
    )

    c4.metric(
        "Autonomic",
        f"{result['autonomic_score']}/100"
    )

    c5.metric(
        "Inflammation",
        f"{result['inflammation_score']}/100"
    )

    c6.metric(
        "AMR",
        f"{result['amr_score']}/100"
    )

    st.divider()

    # =====================================================
    # RADAR CHART
    # =====================================================

    radar_categories = [

        "Microbiome",

        "Voice",

        "Autonomic",

        "Inflammation",

        "AMR"
    ]

    radar_values = [

        result['microbiome_score'],

        result['voice_score'],

        result['autonomic_score'],

        result['inflammation_score'],

        result['amr_score']
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(

        r=radar_values,

        theta=radar_categories,

        fill='toself'
    ))

    fig.update_layout(

        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),

        showlegend=False
    )

    col1, col2 = st.columns([1, 1])

    with col1:

        st.subheader("Risk Radar")

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        st.subheader(
            "Risk Interpretation"
        )

        st.error(
            result["risk"]
        )

        st.write("""

        Elevated neurodegenerative
        vulnerability based on:

        • gut dysbiosis
        • inflammatory burden
        • autonomic dysfunction
        • voice biomarkers
        """)

    st.divider()

    # =====================================================
    # PIE CHART
    # =====================================================

    pie_df = pd.DataFrame({

        "Taxa": [

            "Prevotella",

            "Bacteroides",

            "Faecalibacterium",

            "Roseburia",

            "Others"
        ],

        "Value": [

            18,

            15,

            12,

            8,

            47
        ]
    })

    pie_fig = px.pie(

        pie_df,

        names="Taxa",

        values="Value"
    )

    st.subheader(
        "Microbiome Composition"
    )

    st.plotly_chart(
        pie_fig,
        use_container_width=True
    )

    # =====================================================
    # EXPLAINABILITY
    # =====================================================

    st.subheader(
        "Explainability"
    )

    explain_df = pd.DataFrame(
        result["explainability"]
    )

    st.dataframe(
        explain_df,
        use_container_width=True
    )
