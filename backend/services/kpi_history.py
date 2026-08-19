"""Séries historiques KPI."""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any, Dict, List, Sequence

def _day_keys(days: int, end=None):
    end = end or datetime.utcnow()
    start = (end - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    keys, cur = [], start
    while cur <= end:
        keys.append(cur.strftime("%Y-%m-%d")); cur += timedelta(days=1)
    return keys

def _ts(item):
    return getattr(item, "detected_at", None) or getattr(item, "sent_at", None) or getattr(item, "created_at", None)

def build_kpi_history(falls: Sequence[Any], alerts: Sequence[Any], *, days: int = 30) -> Dict[str, Any]:
    keys = _day_keys(days)
    falls_c = {k: 0 for k in keys}; fp_c = {k: 0 for k in keys}; alerts_c = {k: 0 for k in keys}
    for f in falls:
        ts = _ts(f)
        if not ts: continue
        k = ts.strftime("%Y-%m-%d")
        if k not in falls_c: continue
        falls_c[k] += 1
        if getattr(f, "is_false_positive", False): fp_c[k] += 1
    for a in alerts:
        ts = _ts(a)
        if not ts: continue
        k = ts.strftime("%Y-%m-%d")
        if k in alerts_c: alerts_c[k] += 1
    def to_line(d):
        return [{"x": i, "y": float(d[k]), "label": k, "value": float(d[k])} for i, k in enumerate(keys)]
    rate, precision, cum_tp, cum_fp = {}, {}, 0, 0
    for k in keys:
        total, fp = falls_c[k], fp_c[k]
        rate[k] = round(100.0 * fp / total, 2) if total else 0.0
        cum_fp += fp; cum_tp += max(0, total - fp)
        precision[k] = round(cum_tp / (cum_tp + cum_fp), 4) if (cum_tp + cum_fp) else 0.0
    return {"days": days, "labels": keys, "series": {
        "falls": to_line(falls_c), "false_positives": to_line(fp_c),
        "false_alert_rate_pct": to_line(rate), "alerts": to_line(alerts_c),
        "precision_running": [{"x": i, "y": float(precision[k]), "label": k, "value": float(precision[k])} for i, k in enumerate(keys)],
    }, "generated_at": datetime.utcnow().isoformat()}
