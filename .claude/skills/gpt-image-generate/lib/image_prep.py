#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""输入参考图预处理：质量优先编码压缩，默认不固定长边缩放。

仅作用于上传前的参考图，不处理模型输出 png。
"""
from __future__ import annotations

import io
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PREP_CHOICES = ("off", "light", "medium", "heavy")


@dataclass
class PrepOptions:
    prep: str = "medium"  # off|light|medium|heavy
    jpeg_quality: Optional[int] = None
    target_bytes: Optional[int] = None
    max_edge: int = 0  # 0 = 关闭固定长边；>0 才允许等比缩边兜底


def mime_for(path: str) -> str:
    ext = Path(path).suffix.lower()
    mapping = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    if ext in mapping:
        return mapping[ext]
    guess, _ = mimetypes.guess_type(path)
    return guess or "image/png"


def _has_pillow() -> bool:
    try:
        import PIL  # noqa: F401

        return True
    except ImportError:
        return False


def _resolve_quality_ladder(opt: PrepOptions) -> List[int]:
    if opt.jpeg_quality is not None:
        q = max(1, min(100, int(opt.jpeg_quality)))
        return [q]
    prep = (opt.prep or "medium").lower()
    if prep == "light":
        return [92]
    if prep == "heavy":
        return [85, 80, 75, 70, 65]
    # medium
    return [90, 88, 85, 82, 80]


def _default_target_bytes(opt: PrepOptions) -> Optional[int]:
    if opt.target_bytes is not None:
        return max(1024, int(opt.target_bytes))
    prep = (opt.prep or "medium").lower()
    if prep == "light":
        return None  # 只做一次高质转码，不逼近体积
    if prep == "heavy":
        return 400_000
    if prep == "medium":
        return 700_000
    return None


def _encode_jpeg(img: Any, quality: int) -> bytes:
    from PIL import Image

    if img.mode in ("RGBA", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        alpha = img.split()[-1]
        background.paste(img, mask=alpha)
        work = background
    elif img.mode == "P":
        work = img.convert("RGBA")
        background = Image.new("RGB", work.size, (255, 255, 255))
        if "A" in work.getbands():
            background.paste(work, mask=work.split()[-1])
        else:
            background.paste(work)
        work = background
    elif img.mode != "RGB":
        work = img.convert("RGB")
    else:
        work = img

    buf = io.BytesIO()
    work.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def _scale_to_max_edge(img: Any, max_edge: int) -> Tuple[Any, bool]:
    from PIL import Image

    if max_edge <= 0:
        return img, False
    w, h = img.size
    long_edge = max(w, h)
    if long_edge <= max_edge:
        return img, False
    scale = max_edge / float(long_edge)
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    return img.resize((nw, nh), Image.Resampling.LANCZOS), True


def prepare_image(path: str, opt: Optional[PrepOptions] = None) -> Tuple[str, bytes, Dict[str, Any]]:
    """返回 (mime, raw_bytes, meta)。"""
    opt = opt or PrepOptions()
    prep = (opt.prep or "medium").lower()
    if prep not in PREP_CHOICES:
        raise ValueError(f"无效 --prep: {opt.prep}（可选: {', '.join(PREP_CHOICES)}）")

    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"参考图不存在: {path}")
    raw = p.read_bytes()
    if not raw:
        raise ValueError(f"参考图为空文件: {path}")

    original_mime = mime_for(str(p))
    meta: Dict[str, Any] = {
        "path": str(p.resolve()),
        "prep": prep,
        "original_bytes": len(raw),
        "final_bytes": len(raw),
        "original_wh": None,
        "final_wh": None,
        "scaled": False,
        "jpeg_quality": None,
        "mime": original_mime,
    }

    if prep == "off":
        return original_mime, raw, meta

    if not _has_pillow():
        # 已是较小 JPEG 可原样；否则无法做质量压缩
        if original_mime == "image/jpeg" and len(raw) <= 2_000_000:
            meta["note"] = "no_pillow_passthrough_jpeg"
            return original_mime, raw, meta
        raise RuntimeError(
            "需要 Pillow 才能对参考图做编码压缩。"
            "请执行: pip install pillow"
            " 或使用 --prep off 原样上传（大图可能超时）。"
        )

    from PIL import Image

    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        original_wh = (im.size[0], im.size[1])
        meta["original_wh"] = f"{original_wh[0]}x{original_wh[1]}"
        work = im.copy()

    scaled = False
    # 仅 heavy 且未指定 max_edge 时，不在一开始缩边；先靠 quality
    # 显式 max_edge>0 时，可先缩到上限（兜底/用户意图）
    if opt.max_edge and opt.max_edge > 0:
        work, scaled = _scale_to_max_edge(work, opt.max_edge)

    ladder = _resolve_quality_ladder(opt)
    target = _default_target_bytes(opt)
    best_bytes = raw
    best_q = ladder[0]
    best_wh = work.size

    for q in ladder:
        encoded = _encode_jpeg(work, q)
        best_bytes = encoded
        best_q = q
        best_wh = work.size
        if target is None or len(encoded) <= target:
            break

    # heavy：quality 用尽仍超 target，且允许缩边时，逐步降低长边
    if (
        prep == "heavy"
        and target is not None
        and len(best_bytes) > target
    ):
        edge_caps: List[int] = []
        if opt.max_edge and opt.max_edge > 0:
            edge_caps.append(opt.max_edge)
        # 自动兜底阶梯（仅 heavy）
        long0 = max(work.size)
        for frac in (0.85, 0.7, 0.55, 0.4):
            edge_caps.append(max(512, int(long0 * frac)))
        # 去重保持顺序
        seen = set()
        uniq_caps: List[int] = []
        for e in edge_caps:
            if e not in seen:
                seen.add(e)
                uniq_caps.append(e)

        base = work
        for edge in uniq_caps:
            candidate, did = _scale_to_max_edge(base, edge)
            if did:
                scaled = True
            for q in ladder:
                encoded = _encode_jpeg(candidate, q)
                best_bytes = encoded
                best_q = q
                best_wh = candidate.size
                if len(encoded) <= target:
                    work = candidate
                    break
            else:
                work = candidate
                continue
            break

    mime = "image/jpeg"
    meta.update(
        {
            "final_bytes": len(best_bytes),
            "final_wh": f"{best_wh[0]}x{best_wh[1]}",
            "scaled": scaled,
            "jpeg_quality": best_q,
            "mime": mime,
            "target_bytes": target,
        }
    )
    return mime, best_bytes, meta
