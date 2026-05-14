# =========================================================
# GUT-BRAIN MULTIMODAL AI PLATFORM
# VS CODE FINAL VERSION
# TABNET + XGBOOST + MULTIMODAL FUSION
# =========================================================

# =========================================================
# IMPORTS
# =========================================================

from pytorch_tabnet.tab_model import (
    TabNetClassifier
)
from xgboost import (
    XGBClassifier
)
from sklearn.linear_model import (
    LogisticRegression
)
from sklearn.utils import (
    resample
)
from sklearn.model_selection import (
    train_test_split
)
from sklearn.preprocessing import (
    StandardScaler
)
from sklearn.metrics import (
    roc_auc_score
)
from scipy.io.wavfile import write
import torch
import parselmouth
import pandas as pd
import numpy as np
import librosa
import joblib
import os
import warnings
warnings.filterwarnings("ignore")


# =========================================================
# OPTIONAL MICROPHONE SUPPORT
# =========================================================

try:

    import sounddevice as sd

    SOUNDDEVICE_AVAILABLE = True

except:

    SOUNDDEVICE_AVAILABLE = False

# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# =========================================================
# OUTPUT DIRECTORIES
# =========================================================

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

RESULT_DIR = os.path.join(
    BASE_DIR,
    "results"
)

FEATURE_IMPORTANCE_DIR = os.path.join(
    BASE_DIR,
    "feature_importance"
)

DASHBOARD_DIR = os.path.join(
    BASE_DIR,
    "dashboard"
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploads"
)

# =========================================================
# CREATE FOLDERS
# =========================================================

os.makedirs(MODEL_DIR, exist_ok=True)

os.makedirs(RESULT_DIR, exist_ok=True)

os.makedirs(
    FEATURE_IMPORTANCE_DIR,
    exist_ok=True
)

os.makedirs(
    DASHBOARD_DIR,
    exist_ok=True
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

# =========================================================
# DATASET PATHS
# =========================================================

DATASET_DIR = os.path.join(
    BASE_DIR,
    "datasets"
)

FEATURE_TABLE_PATH = os.path.join(
    DATASET_DIR,
    "feature-table.csv"
)

METADATA_PATH = os.path.join(
    DATASET_DIR,
    "metadata_features.csv"
)

VOICE_PATH = os.path.join(
    DATASET_DIR,
    "parkinsons_voice_dataset.csv"
)

HEALTHY_HRV_PATH = os.path.join(
    DATASET_DIR,
    "healthy_hrv_wesad.csv"
)

PARKINSON_HRV_PATH = os.path.join(
    DATASET_DIR,
    "parkinson_hrv_simulated.csv"
)

# =========================================================
# AUDIO FILES
# =========================================================

VOICE_AUDIO_FILES = [

    os.path.join(
        UPLOAD_DIR,
        "voice.wav"
    ),

    os.path.join(
        UPLOAD_DIR,
        "sample.wav"
    )
]

# =========================================================
# OPTIONAL RECORDING
# =========================================================

if SOUNDDEVICE_AVAILABLE:

    try:

        fs = 44100

        seconds = 5

        print("\nRECORDING AUDIO...")

        audio = sd.rec(

            int(seconds * fs),

            samplerate=fs,

            channels=1,

            dtype=np.int16
        )

        sd.wait()

        recorded_audio_path = os.path.join(
            UPLOAD_DIR,
            "sample.wav"
        )

        write(

            recorded_audio_path,

            fs,

            audio
        )

        print("\nAUDIO SAVED")

    except Exception as e:

        print("\nMIC RECORD FAILED")

        print(str(e))

# =========================================================
# CLEAN DATAFRAME
# =========================================================


def clean_numeric_dataframe(df):

    drop_cols = []

    for col in df.columns:

        if df[col].dtype == "object":

            drop_cols.append(col)

    df = df.drop(
        columns=drop_cols,
        errors="ignore"
    )

    df = df.fillna(0)

    return df

# =========================================================
# VOICE FEATURE EXTRACTION
# =========================================================


def extract_voice_features(audio_path):

    sound = parselmouth.Sound(audio_path)

    pitch = sound.to_pitch()

    harmonicity = sound.to_harmonicity()

    point_process = parselmouth.praat.call(
        sound,
        "To PointProcess (periodic, cc)",
        75,
        500
    )

    jitter = parselmouth.praat.call(
        point_process,
        "Get jitter (local)",
        0,
        0,
        0.0001,
        0.02,
        1.3
    )

    shimmer = parselmouth.praat.call(
        [sound, point_process],
        "Get shimmer (local)",
        0,
        0,
        0.0001,
        0.02,
        1.3,
        1.6
    )

    hnr = parselmouth.praat.call(
        harmonicity,
        "Get mean",
        0,
        0
    )

    mean_pitch = parselmouth.praat.call(
        pitch,
        "Get mean",
        0,
        0,
        "Hertz"
    )

    pitch_std = parselmouth.praat.call(
        pitch,
        "Get standard deviation",
        0,
        0,
        "Hertz"
    )

    return pd.DataFrame([{

        "MDVP:Fo(Hz)":
            mean_pitch,

        "MDVP:Jitter(%)":
            jitter,

        "MDVP:Shimmer":
            shimmer,

        "HNR":
            hnr,

        "pitch_std":
            pitch_std
    }])

# =========================================================
# TRAINING FUNCTION
# =========================================================


def train_modality_pipeline(
    X,
    y,
    model_name,
    feature_names
):

    print(f"\n{'='*60}")
    print(f"TRAINING {model_name.upper()}")
    print(f"{'='*60}")

    X = clean_numeric_dataframe(X)

    feature_names = X.columns

    # =====================================================
    # BOOTSTRAP
    # =====================================================

    X_boot = []
    y_boot = []

    for i in range(5):

        X_resampled, y_resampled = resample(

            X,
            y,

            replace=True,

            random_state=i
        )

        X_boot.append(X_resampled)

        y_boot.append(y_resampled)

    X = pd.concat(X_boot)

    y = pd.concat(y_boot)

    # =====================================================
    # SCALE
    # =====================================================

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    joblib.dump(

        scaler,

        os.path.join(
            MODEL_DIR,
            f"{model_name}_scaler.pkl"
        )
    )

    # =====================================================
    # SPLIT
    # =====================================================

    X_train, X_test, y_train, y_test = (
        train_test_split(

            X_scaled,
            y,

            test_size=0.2,

            stratify=y,

            random_state=42
        )
    )

    # =====================================================
    # XGBOOST
    # =====================================================

    xgb_model = XGBClassifier(

        n_estimators=200,

        max_depth=5,

        learning_rate=0.05,

        use_label_encoder=False,

        eval_metric="logloss",

        random_state=42
    )

    xgb_model.fit(
        X_train,
        y_train
    )

    xgb_proba = xgb_model.predict_proba(
        X_test
    )[:, 1]

    xgb_auc = roc_auc_score(
        y_test,
        xgb_proba
    )

    print(f"\nXGBoost ROC-AUC: {xgb_auc:.4f}")

    # =====================================================
    # TABNET
    # =====================================================

    X_train_np = np.array(
        X_train,
        dtype=np.float32
    )

    X_test_np = np.array(
        X_test,
        dtype=np.float32
    )

    y_train_np = np.array(y_train)

    y_test_np = np.array(y_test)

    tabnet_model = TabNetClassifier(

        n_d=32,

        n_a=32,

        n_steps=5,

        gamma=1.5,

        lambda_sparse=1e-4,

        optimizer_fn=torch.optim.Adam,

        optimizer_params=dict(
            lr=2e-2
        ),

        mask_type='entmax',

        verbose=0
    )

    tabnet_model.fit(

        X_train_np,

        y_train_np,

        eval_set=[
            (
                X_test_np,
                y_test_np
            )
        ],

        eval_metric=['auc'],

        max_epochs=100,

        patience=20
    )

    tabnet_proba = (
        tabnet_model.predict_proba(
            X_test_np
        )[:, 1]
    )

    tabnet_auc = roc_auc_score(
        y_test,
        tabnet_proba
    )

    print(f"\nTabNet ROC-AUC: {tabnet_auc:.4f}")

    # =====================================================
    # SAVE MODELS
    # =====================================================

    joblib.dump(

        xgb_model,

        os.path.join(
            MODEL_DIR,
            f"{model_name}_xgboost.pkl"
        )
    )

    tabnet_model.save_model(

        os.path.join(
            MODEL_DIR,
            f"{model_name}_tabnet"
        )
    )

    # =====================================================
    # FEATURE IMPORTANCE
    # =====================================================

    importance_df = pd.DataFrame({

        "feature":
            feature_names,

        "importance":
            tabnet_model.feature_importances_
    })

    importance_df.to_csv(

        os.path.join(
            FEATURE_IMPORTANCE_DIR,
            f"{model_name}_feature_importance.csv"
        ),

        index=False
    )

    return xgb_model, scaler

# =========================================================
# MICROBIOME MODEL
# =========================================================


print("\nLOADING MICROBIOME")

micro_df = pd.read_csv(
    FEATURE_TABLE_PATH,
    index_col=0
)

n_samples = len(micro_df)

micro_labels = np.array(

    [0] * (n_samples // 2) +

    [1] * (n_samples - n_samples // 2)

)

np.random.shuffle(micro_labels)

y_micro = pd.Series(micro_labels)

X_micro = clean_numeric_dataframe(
    micro_df
)

micro_model, micro_scaler = (
    train_modality_pipeline(

        X_micro,

        y_micro,

        "microbiome",

        X_micro.columns
    )
)

micro_scores = micro_model.predict_proba(

    micro_scaler.transform(
        X_micro
    )

)[:, 1]

# =========================================================
# METADATA MODEL
# =========================================================

print("\nLOADING METADATA")

metadata_df = pd.read_csv(
    METADATA_PATH
)

n_meta = len(metadata_df)

meta_labels = np.array(

    [0] * (n_meta // 2) +

    [1] * (n_meta - n_meta // 2)

)

np.random.shuffle(meta_labels)

y_meta = pd.Series(meta_labels)

X_meta = clean_numeric_dataframe(
    metadata_df
)

metadata_model, metadata_scaler = (
    train_modality_pipeline(

        X_meta,

        y_meta,

        "metadata",

        X_meta.columns
    )
)

metadata_scores = (
    metadata_model.predict_proba(

        metadata_scaler.transform(
            X_meta
        )

    )[:, 1]
)

# =========================================================
# VOICE MODEL
# =========================================================

print("\nLOADING VOICE DATASET")

voice_df = pd.read_csv(
    VOICE_PATH
)

if "name" in voice_df.columns:

    voice_df = voice_df.drop(
        columns=["name"]
    )

X_voice = clean_numeric_dataframe(

    voice_df.drop(
        columns=["status"]
    )
)

y_voice = voice_df["status"]

voice_model, voice_scaler = (
    train_modality_pipeline(

        X_voice,

        y_voice,

        "voice",

        X_voice.columns
    )
)

voice_scores = voice_model.predict_proba(

    voice_scaler.transform(
        X_voice
    )

)[:, 1]

# =========================================================
# DIRECT AUDIO PREDICTION
# =========================================================

print("\nCHECKING AUDIO FILES")

for audio_file in VOICE_AUDIO_FILES:

    if os.path.exists(audio_file):

        try:

            extracted_audio_features = (
                extract_voice_features(
                    audio_file
                )
            )

            extracted_audio_features = (
                extracted_audio_features.reindex(
                    columns=X_voice.columns,
                    fill_value=0
                )
            )

            scaled_audio = (
                voice_scaler.transform(
                    extracted_audio_features
                )
            )

            audio_voice_score = (
                voice_model.predict_proba(
                    scaled_audio
                )[:, 1][0]
            )

            print("\nAUDIO:")
            print(audio_file)

            print("\nVOICE SCORE:")
            print(audio_voice_score)

        except Exception as e:

            print("\nAUDIO FAILED")

            print(str(e))

# =========================================================
# HRV MODEL
# =========================================================

print("\nLOADING HRV")

healthy_df = pd.read_csv(
    HEALTHY_HRV_PATH
)

healthy_df["label"] = 0

parkinson_df = pd.read_csv(
    PARKINSON_HRV_PATH
)

parkinson_df["label"] = 1

hrv_df = pd.concat([
    healthy_df,
    parkinson_df
])

X_hrv = clean_numeric_dataframe(

    hrv_df.drop(
        columns=["label"]
    )
)

y_hrv = hrv_df["label"]

hrv_model, hrv_scaler = (
    train_modality_pipeline(

        X_hrv,

        y_hrv,

        "hrv",

        X_hrv.columns
    )
)

hrv_scores = hrv_model.predict_proba(

    hrv_scaler.transform(
        X_hrv
    )

)[:, 1]

# =========================================================
# META FUSION
# =========================================================

N_META = min(

    len(micro_scores),

    len(metadata_scores),

    len(voice_scores),

    len(hrv_scores)
)

fusion_X = np.column_stack([

    micro_scores[:N_META],

    metadata_scores[:N_META],

    voice_scores[:N_META],

    hrv_scores[:N_META]
])

fusion_y = y_micro.iloc[:N_META]

fusion_scaler = StandardScaler()

fusion_X_scaled = fusion_scaler.fit_transform(
    fusion_X
)

meta_model = LogisticRegression(
    max_iter=1000
)

meta_model.fit(
    fusion_X_scaled,
    fusion_y
)

joblib.dump(

    meta_model,

    os.path.join(
        MODEL_DIR,
        "meta_classifier.pkl"
    )
)

# =========================================================
# DASHBOARD
# =========================================================

gut_brain_scores = meta_model.predict_proba(
    fusion_X_scaled
)[:, 1]

dashboard_df = pd.DataFrame({

    "microbiome_score":
        micro_scores[:N_META],

    "metadata_score":
        metadata_scores[:N_META],

    "voice_score":
        voice_scores[:N_META],

    "hrv_score":
        hrv_scores[:N_META],

    "gut_brain_vulnerability_score":
        gut_brain_scores
})

dashboard_df.to_csv(

    os.path.join(
        DASHBOARD_DIR,
        "gut_brain_dashboard.csv"
    ),

    index=False
)

print("\nPIPELINE COMPLETE")
