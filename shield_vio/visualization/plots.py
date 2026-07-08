"""Publication-oriented plotting utilities."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

def plot_risk_timeline(time, risk, visual_quality, threshold, out: str | Path) -> Path:
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True); fig, ax = plt.subplots(figsize=(7,3)); ax.plot(time, risk, label="risk"); ax.plot(time, visual_quality, label="visual quality"); ax.axhline(threshold, linestyle="--", label="shield threshold"); ax.set_xlabel("time [s]"); ax.set_ylabel("normalized score"); ax.set_ylim(0,1.05); ax.legend(); fig.tight_layout(); fig.savefig(out, dpi=180); plt.close(fig); return out

def plot_trajectory(est: np.ndarray, gt: np.ndarray | None, out: str | Path) -> Path:
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True); fig, ax = plt.subplots(figsize=(4,4)); ax.plot(est[:,0], est[:,1], label="estimated");
    if gt is not None: ax.plot(gt[:,0], gt[:,1], label="ground truth")
    ax.set_aspect("equal", adjustable="box"); ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.legend(); fig.tight_layout(); fig.savefig(out, dpi=180); plt.close(fig); return out
