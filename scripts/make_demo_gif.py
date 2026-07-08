"""Generate the SHIELD-VIO demo GIF from deterministic synthetic data."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter

def main() -> None:
    assets=Path("assets"); videos=Path("results/videos"); assets.mkdir(parents=True, exist_ok=True); videos.mkdir(parents=True, exist_ok=True); n=80; t=np.linspace(0,8,n); rng=np.random.default_rng(4); gt=np.c_[0.25*t,np.sin(t)*0.25]; est=gt+rng.normal(0,0.015,gt.shape)+np.c_[np.maximum(t-4,0)*0.03,np.zeros(n)]; risk=np.clip(0.15+0.11*np.maximum(t-3,0),0,1); visual=np.clip(0.9-0.12*np.maximum(t-2.5,0),0.1,1); fig,(ax0,ax1)=plt.subplots(1,2,figsize=(8,3.6))
    def draw(i):
        ax0.clear(); ax1.clear(); pts=rng.uniform([0,0],[640,480],size=(70,2)); pts=pts[:int(max(8,70*visual[i]))]; ax0.scatter(pts[:,0],pts[:,1],s=8); ax0.set_xlim(0,640); ax0.set_ylim(480,0); ax0.set_title("synthetic tracked features"); ax1.plot(gt[:i+1,0],gt[:i+1,1],label="ground truth"); ax1.plot(est[:i+1,0],est[:i+1,1],label="estimated"); ax1.text(0.02,0.95,f"risk={risk[i]:.2f}\nvisual={visual[i]:.2f}\nSHIELD={'ON' if risk[i]>0.45 else 'OFF'}",transform=ax1.transAxes,va="top"); ax1.set_xlim(-0.1,2.2); ax1.set_ylim(-0.5,0.5); ax1.legend(loc="lower right"); ax1.set_title("risk-aware VIO monitor"); fig.tight_layout()
    anim=FuncAnimation(fig,draw,frames=n,interval=80); anim.save(assets/"demo.gif",writer=PillowWriter(fps=12))
    try: anim.save(videos/"demo.mp4",writer=FFMpegWriter(fps=12))
    except Exception: pass
    plt.close(fig)
if __name__ == "__main__": main()
