"""
生成 week08 報告要用的兩張圖：
  1. figures/sample_per_class.png  - 每類拿 5 張拼成一張 grid
  2. figures/class_distribution.png - 類別樣本數長條圖
"""

import base64
import io
import json
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

# matplotlib 中文字型 (macOS)
plt.rcParams["font.sans-serif"] = ["Heiti TC", "PingFang TC", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "reports/week08-pic-digits/assets/pic_digits_dataset_v2.zip"
FIGDIR = ROOT / "reports/week08-pic-digits/figures"
FIGDIR.mkdir(parents=True, exist_ok=True)


def load_dataset() -> dict[str, list[bytes]]:
    with zipfile.ZipFile(DATASET) as zf:
        raw = json.loads(zf.read("images.json"))
    out = {}
    for label, urls in raw.items():
        out[label] = [base64.b64decode(u.split(",", 1)[1]) for u in urls]
    return out


def build_sample_grid(data: dict[str, list[bytes]], per_class: int = 5) -> None:
    labels = list(data.keys())
    rows = len(labels)
    fig, axes = plt.subplots(rows, per_class, figsize=(per_class * 1.5, rows * 1.6))
    fig.suptitle("每類樣本 (各 5 張)", fontsize=14, y=0.995)

    for r, label in enumerate(labels):
        samples = data[label][:per_class]
        for c in range(per_class):
            ax = axes[r, c]
            ax.axis("off")
            if c < len(samples):
                img = Image.open(io.BytesIO(samples[c]))
                ax.imshow(img)
            if c == 0:
                ax.set_title(f"class: {label}", loc="left",
                             fontsize=10, x=-0.1, y=0.35)

    plt.tight_layout()
    out = FIGDIR / "sample_per_class.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[ok] {out}")
    plt.close(fig)


def build_distribution_chart(data: dict[str, list[bytes]]) -> None:
    labels = list(data.keys())
    counts = [len(data[k]) for k in labels]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, counts, color=["#4C78A8"] * (len(labels) - 1) + ["#E45756"])
    ax.set_title("資料集類別分布")
    ax.set_ylabel("樣本數")
    ax.set_xlabel("類別")
    ax.bar_label(bars, padding=3)
    ax.set_ylim(0, max(counts) * 1.2)

    # 加一條「理想最低線」
    ax.axhline(y=50, color="gray", linestyle="--", alpha=0.6,
               label="建議最低 50 張")
    ax.legend(loc="upper right")

    plt.tight_layout()
    out = FIGDIR / "class_distribution.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[ok] {out}")
    plt.close(fig)


if __name__ == "__main__":
    data = load_dataset()
    build_sample_grid(data)
    build_distribution_chart(data)
