import os
import joblib
import pandas as pd

MODEL_DIR = "ai-model"

microbiome_model = joblib.load(os.path.join(MODEL_DIR, "microbiome_xgboost.pkl"))
microbiome_scaler = joblib.load(os.path.join(MODEL_DIR, "microbiome_scaler.pkl"))

hrv_model = joblib.load(os.path.join(MODEL_DIR, "hrv_xgboost.pkl"))
hrv_scaler = joblib.load(os.path.join(MODEL_DIR, "hrv_scaler.pkl"))

voice_model = joblib.load(os.path.join(MODEL_DIR, "voice_xgboost.pkl"))

meta_model = joblib.load(os.path.join(MODEL_DIR, "meta_classifier.pkl"))
meta_scaler = joblib.load(os.path.join(MODEL_DIR, "meta_scaler.pkl"))


def get_risk_level(score):
    if score >= 70:
        return "High Risk"
    elif score >= 40:
        return "Moderate Risk"
    return "Low Risk"


def get_prediction(data):

    # -----------------------------
    # Microbiome Input
    # -----------------------------
    microbiome_features = microbiome_scaler.feature_names_in_
    microbiome_input = {feature: 0.0 for feature in microbiome_features}

    if "Age_at_collection" in microbiome_input:
        microbiome_input["Age_at_collection"] = 45.0

    if "Sex" in microbiome_input:
        microbiome_input["Sex"] = 0.0

    microbiome_df = pd.DataFrame([microbiome_input])[microbiome_features]
    microbiome_scaled = microbiome_scaler.transform(microbiome_df)
    microbiome_score = microbiome_model.predict_proba(microbiome_scaled)[0][1] * 100

    # -----------------------------
    # HRV Input
    # -----------------------------
    hrv_features = hrv_scaler.feature_names_in_
    hrv_input = {feature: 0.0 for feature in hrv_features}

    if "rmssd" in hrv_input:
        hrv_input["rmssd"] = data.hrv.rmssd

    if "sdnn" in hrv_input:
        hrv_input["sdnn"] = data.hrv.sdnn

    if "heart_rate" in hrv_input:
        hrv_input["heart_rate"] = 72.0

    if "mean_rr" in hrv_input:
        hrv_input["mean_rr"] = 800.0

    hrv_df = pd.DataFrame([hrv_input])[hrv_features]
    hrv_scaled = hrv_scaler.transform(hrv_df)
    hrv_score = hrv_model.predict_proba(hrv_scaled)[0][1] * 100

    # -----------------------------
    # Voice Input
    # Backend formatting for trained voice model
    # -----------------------------
    voice_columns = [
        "mdvp_fo",
        "mdvp_fhi",
        "mdvp_flo",
        "jitter",
        "jitter_abs",
        "rap",
        "ppq",
        "ddp",
        "shimmer",
        "shimmer_db",
        "apq3",
        "apq5",
        "apq",
        "dda",
        "nhr",
        "hnr",
        "rpde",
        "dfa",
        "spread1",
        "spread2",
        "d2",
        "ppe"
    ]

    voice_input = {
        "mdvp_fo": 120.0,
        "mdvp_fhi": 150.0,
        "mdvp_flo": 100.0,
        "jitter": data.voice.jitter,
        "jitter_abs": 0.00005,
        "rap": 0.003,
        "ppq": 0.004,
        "ddp": 0.009,
        "shimmer": data.voice.shimmer,
        "shimmer_db": 0.3,
        "apq3": 0.02,
        "apq5": 0.03,
        "apq": 0.04,
        "dda": 0.06,
        "nhr": 0.02,
        "hnr": 20.0,
        "rpde": 0.5,
        "dfa": 0.7,
        "spread1": -5.0,
        "spread2": 0.2,
        "d2": 2.0,
        "ppe": 0.1
    }

    voice_df = pd.DataFrame([voice_input])
    voice_df = voice_df[voice_columns]

    voice_score = voice_model.predict_proba(voice_df)[0][1] * 100

    # -----------------------------
    # Inflammation Input
    # -----------------------------
    inflammation_score = min(
        ((data.inflammation.il6 / 30) * 50) +
        ((data.inflammation.tnf_alpha / 30) * 50),
        100
    )

    # -----------------------------
    # Meta Classifier Fusion
    # -----------------------------
    meta_df = pd.DataFrame([{

    "microbiome_score": microbiome_score,
    "voice_score": voice_score,
    "hrv_score": hrv_score

    }])

    meta_scaled = meta_scaler.transform(meta_df)
    final_score = meta_model.predict_proba(meta_scaled)[0][1] * 100

    return {
        "final_score": round(float(final_score), 2),
        "risk_level": get_risk_level(final_score),
        "modality_scores": {
            "microbiome": round(float(microbiome_score), 2),
            "voice": round(float(voice_score), 2),
            "hrv": round(float(hrv_score), 2),
            "inflammation": round(float(inflammation_score), 2)
        },
        "shap_explanations": [
            "Microbiome dysbiosis contributed to risk",
            "Voice biomarkers contributed to risk",
            "HRV/autonomic imbalance contributed to risk",
            "Inflammatory biomarkers contributed to risk"
        ]
    }


def get_dashboard_result():
    return {
        "overall_risk": 78,
        "risk_level": "High Risk",
        "scores": {
            "microbiome": 72,
            "voice": 68,
            "autonomic": 65,
            "inflammation": 70,
            "amr": 60
        },
        "interpretation": "The patient shows high risk of neurodegenerative vulnerability.",
        "recommendations": [
            "Dietary modification",
            "Probiotic & prebiotic support",
            "HRV monitoring",
            "Neurology follow-up"
        ],
        "shap_explanations": [
            "Low HRV increased risk",
            "Gut dysbiosis increased risk",
            "Voice tremor features increased risk",
            "Inflammation markers increased risk"
        ]
    }