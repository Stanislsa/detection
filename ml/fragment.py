"""Decoupe videos → data/fragments/raw."""
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import numpy as np
from ml.config import VIDEO_DIR, VIDEO_DIR_ALT, RAW_DIR, METADATA_FILE, CLIP_SECONDS, MAX_FRAMES_PER_CLIP, TARGET_SIZE
try:
    import cv2
except ImportError as e:
    raise SystemExit("opencv-python requis") from e
VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"}

@dataclass
class FragmentMeta:
    id: str; source_video: str; clip_index: int; start_sec: float; end_sec: float
    n_frames: int; motion_score: float; path: str; created_at: str

def discover_videos(video_dir=None):
    dirs = [Path(video_dir)] if video_dir else [VIDEO_DIR, VIDEO_DIR_ALT]
    found = []
    for d in dirs:
        if d.exists():
            found.extend(sorted(p for p in d.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS))
    return found

def _motion_score(frames):
    if len(frames) < 2: return 0.0
    scores, prev = [], cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
    for f in frames[1:]:
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        scores.append(float(np.mean(cv2.absdiff(prev, g)))); prev = g
    return float(np.mean(scores)) if scores else 0.0

def _save_clip(video_path, clip_idx, frames, fps, out_dir):
    step = max(1, len(frames)//MAX_FRAMES_PER_CLIP)
    sampled = frames[::step][:MAX_FRAMES_PER_CLIP]
    motion = _motion_score(sampled)
    fid = f"{video_path.stem.replace(' ','_')}_clip{clip_idx:04d}"
    clip_dir = out_dir / fid; clip_dir.mkdir(parents=True, exist_ok=True)
    for i, fr in enumerate(sampled):
        cv2.imwrite(str(clip_dir / f"f{i:03d}.jpg"), cv2.resize(fr, TARGET_SIZE))
    start = clip_idx * (len(frames)/max(fps,1e-6))
    meta = FragmentMeta(id=fid, source_video=str(video_path), clip_index=clip_idx,
        start_sec=round(start,2), end_sec=round(start+len(frames)/max(fps,1e-6),2),
        n_frames=len(sampled), motion_score=round(motion,3), path=str(clip_dir),
        created_at=datetime.utcnow().isoformat())
    (clip_dir/"meta.json").write_text(json.dumps(asdict(meta), indent=2), encoding="utf-8")
    return meta

def fragment_video(video_path, out_dir=RAW_DIR, clip_seconds=CLIP_SECONDS):
    out_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"[fragment] fail {video_path}"); return []
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    fpc = max(1, int(fps*clip_seconds)); metas, idx, buf = [], 0, []
    while True:
        ok, frame = cap.read()
        if not ok: break
        buf.append(frame)
        if len(buf) >= fpc:
            metas.append(_save_clip(video_path, idx, buf, fps, out_dir)); idx += 1; buf = []
    if buf: metas.append(_save_clip(video_path, idx, buf, fps, out_dir))
    cap.release(); print(f"[fragment] {video_path.name}: {len(metas)} clips"); return metas

def fragment_all(video_dir=None):
    videos = discover_videos(video_dir)
    if not videos:
        print(f"[fragment] Aucune video dans {VIDEO_DIR}"); return []
    all_meta = []
    for vp in videos: all_meta.extend(fragment_video(vp))
    RAW_DIR.parent.mkdir(parents=True, exist_ok=True)
    METADATA_FILE.write_text(json.dumps({"updated_at": datetime.utcnow().isoformat(),
        "count": len(all_meta), "items": [asdict(m) for m in all_meta]}, indent=2, ensure_ascii=False), encoding="utf-8")
    return all_meta
