"""
Visualisation des fuites de données détectées.

Génère des PNG dans data/models/plots/ :
  - leakage_corr_bars.png     : |corrélation| feature ↔ label
  - leakage_issues_severity.png : répartition sévérité des issues
  - class_balance.png         : distribution des classes
  - leakage_dashboard.png     : vue synthétique
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from ml.config import CLASSES, MODELS_DIR
from ml.indicators import INDICATOR_IDS

PLOTS_DIR = MODELS_DIR / "plots"


def _save(fig, path: Path) -> str:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120, bbox_inches="tight", facecolor="white")
    return str(path)


def plot_label_correlations(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: Optional[Sequence[str]] = None,
    top_k: int = 20,
    corr_threshold: float = 0.98,
) -> Optional[str]:
    """Barres des |corrélations| feature–label (rouge si ≥ seuil fuite)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[viz] matplotlib absent — skip corr plot")
        return None

    from ml.leakage import _label_codes, _point_biserial_like

    feature_names = list(feature_names or INDICATOR_IDS)
    X = np.asarray(X, dtype=np.float64)
    y_code = _label_codes(np.asarray(y))
    d = X.shape[1]
    pairs = []
    for j in range(d):
        name = feature_names[j] if j < len(feature_names) else f"f{j}"
        r = abs(_point_biserial_like(X[:, j], y_code))
        pairs.append((name, r))
    pairs.sort(key=lambda x: -x[1])
    pairs = pairs[:top_k]
    if not pairs:
        return None

    names = [p[0] for p in pairs][::-1]
    vals = [p[1] for p in pairs][::-1]
    colors = ["#DC2626" if v >= corr_threshold else ("#F59E0B" if v >= 0.9 else "#2563EB") for v in vals]

    fig, ax = plt.subplots(figsize=(9, max(4, len(names) * 0.35)))
    ax.barh(names, vals, color=colors)
    ax.axvline(corr_threshold, color="#DC2626", ls="--", lw=1.2, label=f"seuil fuite {corr_threshold}")
    ax.axvline(0.90, color="#F59E0B", ls=":", lw=1, label="seuil élevé 0.90")
    ax.set_xlabel("|corrélation| avec le label")
    ax.set_title("Fuites potentielles — corrélation feature ↔ label")
    ax.set_xlim(0, 1.05)
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="x", alpha=0.3)
    path = PLOTS_DIR / "leakage_corr_bars.png"
    out = _save(fig, path)
    plt.close(fig)
    print(f"[viz] {out}")
    return out


def plot_issues_severity(leakage_report: Dict[str, Any]) -> Optional[str]:
    """Camembert / barres des issues par sévérité."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    issues = leakage_report.get("issues") or []
    counts = {"high": 0, "medium": 0, "low": 0}
    for i in issues:
        s = str(i.get("severity", "low")).lower()
        if s in counts:
            counts[s] += 1
    if sum(counts.values()) == 0:
        counts = {"none": 1}

    labels = list(counts.keys())
    sizes = list(counts.values())
    colors = {"high": "#DC2626", "medium": "#F59E0B", "low": "#64748B", "none": "#10B981"}
    cols = [colors.get(l, "#94A3B8") for l in labels]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].pie(sizes, labels=labels, colors=cols, autopct=lambda p: f"{p:.0f}%" if p > 0 else "",
                startangle=90)
    axes[0].set_title("Issues de fuite par sévérité")
    axes[1].bar(labels, sizes, color=cols)
    axes[1].set_ylabel("Nombre")
    axes[1].set_title(f"Total issues = {sum(sizes) if 'none' not in labels else 0}")
    axes[1].grid(axis="y", alpha=0.3)
    # Liste texte des issues high
    high = [i.get("message", "")[:60] for i in issues if i.get("severity") == "high"]
    if high:
        fig.text(0.5, -0.02, "High: " + " | ".join(high[:3]), ha="center", fontsize=8, color="#DC2626")
    path = PLOTS_DIR / "leakage_issues_severity.png"
    out = _save(fig, path)
    plt.close(fig)
    print(f"[viz] {out}")
    return out


def plot_class_balance(y: np.ndarray, y_balanced: Optional[np.ndarray] = None) -> Optional[str]:
    """Distribution des classes avant / après rééquilibrage."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    def _counts(arr):
        arr = np.asarray(arr)
        return [int(np.sum(arr == c)) for c in CLASSES]

    c0 = _counts(y)
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(CLASSES))
    w = 0.35
    ax.bar(x - (w / 2 if y_balanced is not None else 0), c0, w, label="Avant", color="#6366F1")
    if y_balanced is not None:
        c1 = _counts(y_balanced)
        ax.bar(x + w / 2, c1, w, label="Après rééquilibrage", color="#10B981")
    ax.set_xticks(x)
    ax.set_xticklabels(CLASSES)
    ax.set_ylabel("Effectif")
    ax.set_title("Équilibre des classes (normal / urgent / critique)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    path = PLOTS_DIR / "class_balance.png"
    out = _save(fig, path)
    plt.close(fig)
    print(f"[viz] {out}")
    return out


def plot_leakage_dashboard(
    X: np.ndarray,
    y: np.ndarray,
    leakage_report: Dict[str, Any],
    feature_names: Optional[Sequence[str]] = None,
) -> Optional[str]:
    """Dashboard unique fuites + balance."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    from ml.leakage import _label_codes, _point_biserial_like

    feature_names = list(feature_names or INDICATOR_IDS)
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    y_code = _label_codes(y)

    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)

    # A — top corr
    ax1 = fig.add_subplot(gs[0, :])
    pairs = []
    for j in range(X.shape[1]):
        name = feature_names[j] if j < len(feature_names) else f"f{j}"
        pairs.append((name, abs(_point_biserial_like(X[:, j], y_code))))
    pairs.sort(key=lambda x: -x[1])
    top = pairs[:15]
    names = [p[0] for p in top][::-1]
    vals = [p[1] for p in top][::-1]
    colors = ["#DC2626" if v >= 0.98 else ("#F59E0B" if v >= 0.9 else "#3B82F6") for v in vals]
    ax1.barh(names, vals, color=colors)
    ax1.axvline(0.98, color="#DC2626", ls="--", lw=1)
    ax1.set_title("Corrélation |r| feature ↔ label (rouge = fuite probable)")
    ax1.set_xlim(0, 1.05)

    # B — class counts
    ax2 = fig.add_subplot(gs[1, 0])
    counts = [int(np.sum(y == c)) for c in CLASSES]
    ax2.bar(CLASSES, counts, color=["#22C55E", "#F59E0B", "#EF4444"])
    ax2.set_title("Classes")
    ax2.set_ylabel("n")

    # C — severity
    ax3 = fig.add_subplot(gs[1, 1])
    issues = leakage_report.get("issues") or []
    sev = {"high": 0, "medium": 0, "low": 0}
    for i in issues:
        s = str(i.get("severity", "low")).lower()
        if s in sev:
            sev[s] += 1
    ax3.bar(list(sev.keys()), list(sev.values()), color=["#DC2626", "#F59E0B", "#64748B"])
    ax3.set_title(f"Issues fuite (status={leakage_report.get('status')})")

    status = str(leakage_report.get("status", "?")).upper()
    fig.suptitle(f"Dashboard fuites de données — {status}", fontsize=13, fontweight="bold")
    path = PLOTS_DIR / "leakage_dashboard.png"
    out = _save(fig, path)
    plt.close(fig)
    print(f"[viz] {out}")
    return out


def visualize_all(
    X: np.ndarray,
    y: np.ndarray,
    leakage_report: Optional[Dict[str, Any]] = None,
    y_balanced: Optional[np.ndarray] = None,
    feature_names: Optional[Sequence[str]] = None,
) -> Dict[str, Optional[str]]:
    """Génère toutes les visualisations fuites + balance."""
    if leakage_report is None:
        from ml.leakage import detect_leakage
        leakage_report = detect_leakage(X, y, feature_names=feature_names)

    paths = {
        "corr_bars": plot_label_correlations(X, y, feature_names),
        "issues_severity": plot_issues_severity(leakage_report),
        "class_balance": plot_class_balance(y, y_balanced),
        "dashboard": plot_leakage_dashboard(X, y, leakage_report, feature_names),
    }
    meta = {"plots": paths, "leakage_status": leakage_report.get("status")}
    try:
        (PLOTS_DIR / "viz_index.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    except Exception:
        pass
    return paths
