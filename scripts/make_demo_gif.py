"""Render SHIELD-VIO Synthetic Demo GIF and MP4 entirely from generated CSV data."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.patches import Ellipse
import numpy as np

from shield_vio.simulation.synthetic_vio import SyntheticVIOConfig, run_synthetic_vio


def read_csv(path: Path) -> dict[str, np.ndarray]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    data: dict[str, list] = {}
    for row in rows:
        for key, value in row.items():
            try:
                data.setdefault(key, []).append(float(value))
            except ValueError:
                data.setdefault(key, []).append(value)
    return {k: np.asarray(v, dtype=object if isinstance(v[0], str) else float) for k, v in data.items()}


def render_demo(results: Path, fps: int = 12) -> dict[str, str]:
    if not (results / "ground_truth.csv").exists():
        run_synthetic_vio(SyntheticVIOConfig(output_dir=str(results)))
    gt = read_csv(results / "ground_truth.csv")
    est = read_csv(results / "estimated_trajectory.csv")
    unc = read_csv(results / "uncertainty.csv")
    vq = read_csv(results / "visual_quality.csv")
    risk = read_csv(results / "risk_score.csv")
    shield = read_csv(results / "shield_events.csv")

    assets_gif = Path("assets/gifs")
    assets_video = Path("assets/videos")
    out_video = Path("results/videos")
    frames_dir = out_video / "frames"
    for path in (assets_gif, assets_video, out_video, frames_dir):
        path.mkdir(parents=True, exist_ok=True)

    step = max(1, len(gt["t"]) // 72)
    idx = list(range(0, len(gt["t"]), step))
    rng = np.random.default_rng(42)
    fig = plt.figure(figsize=(10, 6))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.35, 1.0])
    ax_path = fig.add_subplot(gs[:, 0])
    ax_panel = fig.add_subplot(gs[0, 1])
    ax_series = fig.add_subplot(gs[1, 1])

    def draw(frame_no: int) -> None:
        i = idx[frame_no]
        ax_path.clear(); ax_panel.clear(); ax_series.clear()
        ax_path.plot(gt["x"][: i + 1], gt["y"][: i + 1], label="ground truth")
        ax_path.plot(est["x"][: i + 1], est["y"][: i + 1], label="estimated")
        ax_path.scatter([gt["x"][i]], [gt["y"][i]], s=35, label="robot")
        ellipse = Ellipse(
            (float(est["x"][i]), float(est["y"][i])),
            width=0.18 + float(unc["trace"][i]) * 0.12,
            height=0.10 + float(unc["trace"][i]) * 0.06,
            alpha=0.25,
        )
        ax_path.add_patch(ellipse)
        ax_path.set_title("SHIELD-VIO Safety-Aware Visual-Inertial Odometry\nSynthetic Demo")
        ax_path.set_xlabel("x [m]")
        ax_path.set_ylabel("y [m]")
        ax_path.axis("equal")
        ax_path.grid(True, alpha=0.25)
        ax_path.legend(loc="upper left")

        event = str(risk["event"][i])
        status = str(shield["state"][i])
        features = int(float(vq["feature_count"][i]))
        pts = rng.normal(0, 1, size=(max(features, 1), 2))
        ax_panel.scatter(pts[:, 0], pts[:, 1], s=7, alpha=0.65)
        ax_panel.set_xticks([])
        ax_panel.set_yticks([])
        ax_panel.set_title("status panel")
        ax_panel.text(
            0.02,
            0.96,
            f"time: {float(gt['t'][i]):.1f}s\n"
            f"visual quality: {float(vq['visual_quality'][i]):.2f}\n"
            f"risk score: {float(risk['risk_score'][i]):.2f}\n"
            f"shield: {status}\nevent: {event}\nfeatures: {features}",
            transform=ax_panel.transAxes,
            va="top",
            ha="left",
            fontsize=10,
            bbox={"boxstyle": "round", "fc": "white", "alpha": 0.85},
        )
        if status in {"HALT", "RELOCALIZE_REQUESTED"}:
            ax_panel.text(0.5, 0.08, "HALT / high uncertainty", transform=ax_panel.transAxes, ha="center", fontsize=11, weight="bold")

        ax_series.plot(risk["t"][: i + 1], risk["risk_score"][: i + 1], label="risk")
        ax_series.plot(vq["t"][: i + 1], vq["visual_quality"][: i + 1], label="visual quality")
        ax_series.axhline(0.45, linestyle="--", linewidth=1)
        ax_series.axhline(0.82, linestyle="--", linewidth=1)
        ax_series.set_xlim(float(gt["t"][0]), float(gt["t"][-1]))
        ax_series.set_ylim(0, 1.03)
        ax_series.grid(True, alpha=0.25)
        ax_series.legend(loc="lower left")
        ax_series.set_title("risk / visual quality timeline")
        fig.tight_layout()
        frame_path = frames_dir / f"frame_{frame_no:04d}.png"
        if not frame_path.exists():
            fig.savefig(frame_path, dpi=90)

    anim = FuncAnimation(fig, draw, frames=len(idx), interval=int(1000 / fps), repeat=False)
    paths = {
        "gif": str(assets_gif / "demo.gif"),
        "mp4": str(assets_video / "demo.mp4"),
        "results_gif": str(out_video / "shield_vio_demo.gif"),
        "results_mp4": str(out_video / "shield_vio_demo.mp4"),
    }
    anim.save(paths["gif"], writer=PillowWriter(fps=fps))
    anim.save(paths["results_gif"], writer=PillowWriter(fps=fps))
    try:
        writer = FFMpegWriter(fps=fps, metadata={"title": "SHIELD-VIO Synthetic Demo"})
        anim.save(paths["mp4"], writer=writer)
        anim.save(paths["results_mp4"], writer=writer)
    except Exception as exc:
        (out_video / "mp4_generation_warning.txt").write_text(f"MP4 generation requires ffmpeg: {exc}\n", encoding="utf-8")
    plt.close(fig)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results/synthetic_demo")
    parser.add_argument("--fps", type=int, default=12)
    args = parser.parse_args()
    print(render_demo(Path(args.results), args.fps))


if __name__ == "__main__":
    main()
