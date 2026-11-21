#!/usr/bin/env python3
"""Storyboard ANTES de montar: una lámina con un cuadro por plano, con su título, el subtítulo de lo que se dice,
el segundo en que entra y qué pasa. Se le muestra al usuario y no se monta nada hasta que diga que sí.

Uso:
    python3 storyboard.py plan.json            → <output>_storyboard.jpg  (junto al plan)
Si el plan tiene "color" (calido, oscuro...), también genera <output>_antes_despues.jpg.
En cada segmento del plan podés poner "note": "qué pasa en este plano" para que aparezca en la lámina.
Requiere Pillow (pip install pillow).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render_reel as rr  # noqa: E402

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Falta Pillow: pip install pillow")

TW, TH = 360, 640          # tamaño de cada cuadro
FONTS = HERE.parent / "assets" / "fonts"
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def font(name, size):
    try:
        return ImageFont.truetype(str(FONTS / name), size)
    except OSError:
        return ImageFont.load_default()


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def seg_kind(seg):
    if seg.get("type"):
        return seg["type"]
    return "image" if Path(seg.get("src", "")).suffix.lower() in IMG_EXT else "video"


def seg_duration(seg, base):
    k = seg_kind(seg)
    if k == "image":
        return float(seg.get("duration", 2.5))
    if k == "card":
        return float(seg.get("duration", 3.0))
    src = (base / seg["src"]).resolve()
    end = float(seg["end"]) if seg.get("end") is not None else rr.duration(src)
    return (min(end, rr.duration(src)) - float(seg.get("start", 0))) / float(seg.get("speed", 1.0))


def grab(seg, base, plan, brand, out_png, graded=True, at=None):
    W, H = TW * 2, TH * 2
    k = seg_kind(seg)
    if k == "card":
        img = Image.new("RGB", (W, H), hexrgb(seg.get("bg", brand["color_fondo_cierre"])))
        if seg.get("logo"):
            lg = Image.open(base / seg["logo"]).convert("RGBA")
            lw = int(W * 0.52)
            lg = lg.resize((lw, int(lg.height * lw / lg.width)))
            img.paste(lg, ((W - lw) // 2, int(H * 0.30) - lg.height // 2), lg)
        img.save(out_png)
        return
    src = (base / seg["src"]).resolve()
    t = 0 if k == "image" else (at if at is not None else
                                 float(seg.get("start", 0)) + seg_duration(seg, base) * float(seg.get("speed", 1)) / 2)
    pre, lbl = "", "0:v"
    if k == "video" and rr.is_hdr(src):
        pre, lbl = f"[0:v]{rr.HDR_TO_SDR}[sdr];", "sdr"
    vf = pre + rr.fit_filter(W, H, seg.get("fit", "crop"), seg.get("focus_x", 0.5), seg.get("focus_y", 0.5), lbl, "v")
    cf = rr.color_filter(seg, plan) if graded else ""
    if cf:
        vf = vf[:-3] + f"[f0];[f0]{cf}[v]"
    seek = [] if k == "image" else ["-ss", f"{t:.3f}"]
    cmd = ["ffmpeg", "-hide_banner", "-y", *seek, "-i", str(src), "-filter_complex", vf,
           "-map", "[v]", "-frames:v", "1", str(out_png)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not Path(out_png).exists():
        Image.new("RGB", (W, H), (60, 60, 60)).save(out_png)


def draw_centered(d, text, y, fnt, fill, stroke=0, stroke_fill=(0, 0, 0), max_w=TW - 20):
    while d.textlength(text, font=fnt) > max_w and fnt.size > 10:
        fnt = fnt.font_variant(size=fnt.size - 2)
    w = d.textlength(text, font=fnt)
    d.text(((TW - w) / 2, y), text, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    plan_path = Path(sys.argv[1]).resolve()
    base = plan_path.parent
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    brand = dict(rr.DEFAULT_BRAND)
    bf = HERE.parent / "references" / "marca.json"
    if bf.exists():
        brand.update(json.loads(bf.read_text(encoding="utf-8")))
    brand.update(plan.get("brand", {}))
    acc = hexrgb(brand["color_acento"])

    segs = list(plan["segments"]) + ([{"type": "card", **plan["end_card"]}] if plan.get("end_card") else [])
    durs = [seg_duration(s, base) for s in segs]
    T = float(plan.get("transition", 0.25))
    T = min(T, min(durs) / 2.5) if T > 0 else 0
    starts = [0.0]
    for d in durs[:-1]:
        starts.append(starts[-1] + d - T)
    words = rr.map_words(segs, starts, base, plan) if plan.get("subtitles") == "auto" else []

    # Un cuadro por plano, y uno más cada vez que entra un texto o sticker nuevo dentro del plano
    total = starts[-1] + durs[-1]
    cuts = sorted(set([round(x, 2) for x in starts] +
                      [round(float(t.get("start", 0)), 2) for t in plan.get("texts", []) if t.get("style") != "sub"] +
                      [round(float(k["start"]), 2) for k in plan.get("stickers", [])]))
    cuts = [c for c in cuts if c < total - 0.2]
    moments, carry = [], None
    for c, nxt in zip(cuts, cuts[1:] + [total]):
        si = max(i for i, x in enumerate(starts) if x <= c + 0.01)
        if nxt - c < 0.35 and nxt < total:  # momentos muy cortos se juntan con el siguiente
            carry = c if carry is None else carry
            continue
        moments.append((c if carry is None or starts[si] > carry else carry, si, nxt))
        carry = None

    tiles = []
    tmp = Path(tempfile.mkdtemp(prefix="sb_"))
    for n, (st, si, until) in enumerate(moments):
        seg, d = segs[si], until - st
        tpk = min(st + 0.45, st + d / 2)  # momento que se dibuja
        src_t = float(seg.get("start", 0)) + (tpk - starts[si]) * float(seg.get("speed", 1))
        png = tmp / f"p{n}.png"
        grab(seg, base, plan, brand, png, at=src_t)
        im = Image.open(png).convert("RGB").resize((TW, TH))
        dr = ImageDraw.Draw(im)
        for t in plan.get("texts", []):
            a, b = float(t.get("start", 0)), float(t.get("end", 0))
            if not (a <= tpk + 0.3 < b):
                continue
            style = t.get("style", "hook")
            y = int(TH * float(t["y"])) if t.get("y") is not None else None
            if style == "titulo":
                draw_centered(dr, t["text"].upper(), y or 30, font("Anton-Regular.ttf", 64), acc, 2)
            elif style == "bajada":
                draw_centered(dr, t["text"].upper(), y or 105, font("Oswald-Variable.ttf", 22), acc, 1)
            elif style == "promo":
                draw_centered(dr, t["text"], y or TH // 2 - 50, font("Anton-Regular.ttf", 90), hexrgb("#1E1E1C"), 2,
                              (255, 255, 255))
            elif style == "lista":
                for k, item in enumerate(t.get("items", [])):
                    yy = int(TH * float(t.get("y", 0.30))) + k * 44
                    if tpk + 0.3 < float(t.get("start", 0)) + k * float(t.get("interval", 0.6)):
                        break
                    fw = dr.textlength(item, font=font("Oswald-Variable.ttf", 24))
                    dr.rounded_rectangle([20, yy, 20 + 46 + fw, yy + 36], 8, fill=(255, 255, 255))
                    dr.line([(29, yy + 19), (35, yy + 26), (47, yy + 10)], fill=acc, width=4)  # tilde dibujado
                    dr.text((56, yy + 3), item, font=font("Oswald-Variable.ttf", 24), fill=(30, 30, 28))
            else:
                draw_centered(dr, t["text"], y or 60, font("Oswald-Variable.ttf", 30), (255, 255, 255), 2)
        said = " ".join(w["w"] for w in words if st <= w["start"] < until)
        if said:
            short = said if len(said) < 70 else said[:67] + "…"
            draw_centered(dr, short, int(TH * 0.72), font("Oswald-Variable.ttf", 24), (255, 255, 255), 2)
        if seg_kind(seg) == "card":
            for k, line in enumerate(seg.get("lines", [])):
                last = k == len(seg.get("lines", [])) - 1
                draw_centered(dr, line, int(TH * (float(seg.get("text_y", 0.55)) + k * float(seg.get("line_gap", 0.065)))) - 14,
                              font("Oswald-Variable.ttf", 26), acc if last else hexrgb("#1E1E1C"))
        for stk in plan.get("stickers", []):
            if float(stk["start"]) <= tpk + 0.3 < float(stk["end"]):
                lg = Image.open(base / stk["src"]).convert("RGBA")
                lw = int(TW * float(stk.get("width", 600)) / 1080)
                lg = lg.resize((lw, int(lg.height * lw / lg.width)))
                im.paste(lg, (int(TW * float(stk.get("x", 0.5))) - lw // 2, int(TH * float(stk.get("y", 0.4))) - lg.height // 2), lg)
        # pie con datos del plano
        card = Image.new("RGB", (TW, TH + 110), (250, 247, 240))
        card.paste(im, (0, 0))
        dc = ImageDraw.Draw(card)
        kind = seg_kind(seg)
        what = seg.get("note") or {"card": "Cierre: showroom + WhatsApp", "image": f"Foto {Path(seg.get('src', '')).name}"}.get(
            kind, f"{Path(seg.get('src', '')).name}")
        extra = []
        if seg.get("speed", 1) != 1:
            extra.append(f"x{seg['speed']}")
        if seg.get("jump_zoom", plan.get("jump_zoom")) and kind == "video":
            extra.append("zoom en cortes")
        if seg.get("color", plan.get("color")) and kind != "card":
            extra.append(f"color {seg.get('color', plan.get('color'))}")
        dc.text((10, TH + 8), f"{n + 1} · PLANO {si + 1}  ·  {st:.1f}–{until:.1f}s", font=font("Anton-Regular.ttf", 26), fill=(30, 30, 28))
        dc.text((10, TH + 44), what[:44], font=font("Oswald-Variable.ttf", 22), fill=(60, 60, 60))
        if extra:
            dc.text((10, TH + 74), " · ".join(extra)[:48], font=font("Oswald-Variable.ttf", 20), fill=(150, 110, 0))
        tiles.append(card)

    cols = min(4, len(tiles))
    rows = -(-len(tiles) // cols)
    pad = 16
    sheet = Image.new("RGB", (cols * (TW + pad) + pad, rows * (TH + 110 + pad) + pad + 60), (30, 30, 28))
    ImageDraw.Draw(sheet).text((pad, 14), f"STORYBOARD · {Path(plan.get('output', 'reel')).stem}",
                               font=font("Anton-Regular.ttf", 34), fill=acc)
    for k, tl in enumerate(tiles):
        sheet.paste(tl, (pad + (k % cols) * (TW + pad), 60 + pad + (k // cols) * (TH + 110 + pad)))
    stem = Path(plan.get("output", "reel.mp4")).stem
    out = base / Path(plan.get("output", "reel.mp4")).parent / f"{stem}_storyboard.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=88)
    print(f"✓ Storyboard: {out}  ({len(tiles)} planos, ~{starts[-1] + durs[-1]:.1f}s)")

    if plan.get("color"):
        vid = next((s for s in plan["segments"] if seg_kind(s) == "video"), None)
        if vid:
            a_png, b_png = tmp / "antes.png", tmp / "despues.png"
            grab(vid, base, plan, brand, a_png, graded=False)
            grab(vid, base, plan, brand, b_png, graded=True)
            A, B = Image.open(a_png).resize((TW, TH)), Image.open(b_png).resize((TW, TH))
            ab = Image.new("RGB", (TW * 2 + 12, TH + 50), (30, 30, 28))
            ab.paste(A, (0, 50))
            ab.paste(B, (TW + 12, 50))
            d2 = ImageDraw.Draw(ab)
            d2.text((10, 10), "ANTES", font=font("Anton-Regular.ttf", 30), fill=(255, 255, 255))
            d2.text((TW + 22, 10), f"DESPUÉS · {plan['color']}", font=font("Anton-Regular.ttf", 30), fill=acc)
            out2 = out.with_name(f"{stem}_antes_despues.jpg")
            ab.save(out2, quality=88)
            print(f"✓ Antes y después: {out2}")


if __name__ == "__main__":
    main()
