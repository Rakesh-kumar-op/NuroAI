from pydantic import BaseModel


class Microbiome(BaseModel):
    shannon_index: float
    proteobacteria: float


class Voice(BaseModel):
    jitter: float
    shimmer: float


class HRV(BaseModel):
    rmssd: float
    sdnn: float


class Inflammation(BaseModel):
    il6: float
    tnf_alpha: float


class PatientInput(BaseModel):
    microbiome: Microbiome
    voice: Voice
    hrv: HRV
    inflammation: Inflammation