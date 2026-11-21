#!/usr/bin/env python3
"""Renderiza un reel/TikTok a partir de un plan JSON (ver references/plan_ejemplo.json).

Uso:
    python3 render_reel.py plan.json

Pasos internos:
  1. Cada segmento (clip de video, foto o placa de cierre) se normaliza a 1080x1920, 30 fps, audio 48 kHz.
  2. Se unen con fundidos cruzados (transition) o corte seco (transition = 0).
  3. Pasada final: logo, textos (ganchos, etiquetas, CTA), subtítulos, música con "ducking" y
     normalización de volumen a -14 LUFS (lo que esperan Instagram y TikTok).
Las rutas relativas del plan se resuelven desde la carpeta donde está el plan.
"""
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FORMATS = {"9:16": (1080, 1920), "4:5": (1080, 1350), "1:1": (1080, 1080), "16:9": (1920, 1080)}
FPS = 30
SKILL_DIR = Path(__file__).resolve().parent.parent

DEFAULT_BRAND = {
    "font": "Oswald",            # subtítulos y textos comunes
    "font_titulos": "Anton",     # títulos grandes (ARMADO, 20% OFF)
    "color_texto": "#FFFFFF",
    "color_caja": "#1E1E1C",
    "color_acento": "#F9D20A",   # amarillo Sundesign
    "color_fondo_cierre": "#FFFFFF",
    "color_texto_cierre": "#1E1E1C",
}
TRANSITIONS = {  # nombre en el plan -> transición de ffmpeg xfade
    "fundido": "fade", "fade": "fade",
    "barrido": "hblur", "whip": "hblur",
    "deslizar": "slideleft", "slide": "slideleft",
    "cortina": "wipeleft", "wipe": "wipeleft",
    "zoom": "zoomin",
}


# ---------------------------------------------------------------- utilidades
def sh(cmd, desc):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        tail = "\n".join(r.stderr.strip().splitlines()[-15:])
        sys.exit(f"✗ Error en {desc}:\n{tail}\n\nComando: {' '.join(map(str, cmd))}")
    return r


def probe(path):
    r = sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)], f"ffprobe {path}")
    return json.loads(r.stdout)


def has_audio(path):
    return any(s["codec_type"] == "audio" for s in probe(path)["streams"])


def duration(path):
    return float(probe(path)["format"]["duration"])


def ass_color(hex_color, alpha=0):
    """#RRGGBB -> &HAABBGGRR (alpha 0 = opaco, 255 = transparente)."""
    h = hex_color.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def ass_time(t):
    t = max(0.0, t)
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def ass_escape(text):
    text = text.replace("\\N", "\n")
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def ff_path(p):
    """Escapa una ruta para usarla dentro de un filtro de ffmpeg."""
    return str(p).replace("\\", "/").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")


def atempo_chain(speed):
    parts = []
    s = speed
    while s > 2.0:
        parts.append("atempo=2.0")
        s /= 2.0
    while s < 0.5:
        parts.append("atempo=0.5")
        s /= 0.5
    parts.append(f"atempo={s:.4f}")
    return ",".join(parts)


def fit_filter(W, H, fit, fx=0.5, fy=0.5, label_in="0:v", label_out="v"):
    """Lleva cualquier video/foto al formato vertical.
    crop: llena la pantalla recortando (fx/fy = dónde está el mueble, 0..1).
    blur: muestra el cuadro entero con fondo desenfocado (ideal para tomas horizontales)."""
    if fit == "blur":
        return (
            f"[{label_in}]split[bgsrc][fgsrc];"
            f"[bgsrc]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:3,eq=brightness=-0.08[bg];"
            f"[fgsrc]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[{label_out}]"
        )
    return (
        f"[{label_in}]scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})*{fy},setsar=1[{label_out}]"
    )


# ---------------------------------------------------------------- segmentos
def render_video_segment(seg, W, H, out, base):
    src = (base / seg["src"]).resolve()
    start = float(seg.get("start", 0))
    end = seg.get("end")
    speed = float(seg.get("speed", 1.0))
    src_dur = duration(src)
    end = float(end) if end is not None else src_dur
    end = min(end, src_dur)
    if end <= start:
        sys.exit(f"✗ Segmento inválido en {src.name}: start={start} end={end}")
    out_dur = (end - start) / speed

    vf = fit_filter(W, H, seg.get("fit", "crop"), seg.get("focus_x", 0.5), seg.get("focus_y", 0.5), "0:v", "f")
    vf += f";[f]setpts=(PTS-STARTPTS)/{speed},fps={FPS},format=yuv420p"
    if seg.get("punch_in"):  # acercamiento fijo (recorta un poco más, da ritmo entre tomas)
        z = float(seg.get("punch_in"))
        vf += f",scale=iw*{1+z}:-2,crop={W}:{H}:(iw-{W})/2:(ih-{H})/2"
    vf += "[v]"

    use_audio = has_audio(src) and not seg.get("mute", False)
    cmd = ["ffmpeg", "-hide_banner", "-y", "-ss", f"{start}", "-to", f"{end}", "-i", str(src)]
    if use_audio:
        vol = float(seg.get("volume", 1.0))
        af = f"[0:a]asetpts=PTS-STARTPTS,{atempo_chain(speed)},volume={vol},aresample=48000,aformat=channel_layouts=stereo[a]"
    else:
        cmd += ["-f", "lavfi", "-t", f"{out_dur}", "-i", "anullsrc=r=48000:cl=stereo"]
        af = "[1:a]anull[a]"
    cmd += [
        "-filter_complex", f"{vf};{af}", "-map", "[v]", "-map", "[a]", "-t", f"{out_dur}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", str(out),
    ]
    sh(cmd, f"segmento de video {src.name}")
    return duration(out)


def render_image_segment(seg, W, H, out, base):
    src = (base / seg["src"]).resolve()
    dur = float(seg.get("duration", 2.5))
    frames = int(round(dur * FPS))
    fit = seg.get("fit", "crop")
    zoom = seg.get("zoom", True)
    z = float(seg.get("zoom_amount", 0.12))
    direction = seg.get("zoom_direction", "in")
    # Primero llevamos la foto a 2x el tamaño final (para que el zoom no pixele), luego Ken Burns.
    pre = fit_filter(W * 2, H * 2, fit, seg.get("focus_x", 0.5), seg.get("focus_y", 0.5), "0:v", "f")
    if zoom:
        if direction == "out":
            zexpr = f"{1+z}-{z}*on/{frames}"
        else:
            zexpr = f"1+{z}*on/{frames}"
        vf = (
            f"{pre};[f]zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={frames}:s={W}x{H}:fps={FPS},format=yuv420p[v]"
        )
    else:
        vf = f"{pre};[f]scale={W}:{H},fps={FPS},format=yuv420p[v]"
    cmd = [
        "ffmpeg", "-hide_banner", "-y", "-loop", "1", "-framerate", str(FPS), "-t", f"{dur}", "-i", str(src),
        "-f", "lavfi", "-t", f"{dur}", "-i", "anullsrc=r=48000:cl=stereo",
        "-filter_complex", vf, "-map", "[v]", "-map", "1:a", "-frames:v", str(frames),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", str(out),
    ]
    sh(cmd, f"segmento de foto {src.name}")
    return duration(out)


def render_card_segment(seg, W, H, out, base, brand):
    dur = float(seg.get("duration", 3.0))
    bg = seg.get("bg", brand["color_fondo_cierre"]).lstrip("#")
    logo = seg.get("logo")
    cmd = ["ffmpeg", "-hide_banner", "-y", "-f", "lavfi", "-t", f"{dur}", "-i", f"color=c=0x{bg}:s={W}x{H}:r={FPS}"]
    cmd += ["-f", "lavfi", "-t", f"{dur}", "-i", "anullsrc=r=48000:cl=stereo"]
    if logo:
        lw = int(seg.get("logo_width", W * 0.55))
        ly = seg.get("logo_y", 0.30)
        cmd += ["-loop", "1", "-t", f"{dur}", "-i", str((base / logo).resolve())]
        vf = (
            f"[2:v]scale={lw}:-1,format=rgba[lg];"
            f"[0:v][lg]overlay=(W-w)/2:H*{ly}-h/2,format=yuv420p[v]"
        )
    else:
        vf = "[0:v]format=yuv420p[v]"
    cmd += [
        "-filter_complex", vf, "-map", "[v]", "-map", "1:a", "-t", f"{dur}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", str(out),
    ]
    sh(cmd, "placa de cierre")
    return duration(out)


# ---------------------------------------------------------------- unión
def join_segments(paths, durs, transition, out, kinds=None):
    """kinds[i] = nombre de transición para entrar al segmento i (None = fundido)."""
    n = len(paths)
    cmd = ["ffmpeg", "-hide_banner", "-y"]
    for p in paths:
        cmd += ["-i", str(p)]
    if n == 1:
        shutil.copy(paths[0], out)
        return durs[0], [0.0]
    starts = [0.0]
    kinds = kinds or [None] * n
    if transition and transition > 0:
        T = min(transition, min(durs) / 2.5)
        parts = []
        vlast, alast = "0:v", "0:a"
        length = durs[0]
        for i in range(1, n):
            offset = length - T
            starts.append(offset)
            vo, ao = f"v{i}", f"a{i}"
            parts.append(f"[{vlast}][{i}:v]xfade=transition={TRANSITIONS.get(kinds[i] or "fundido", "fade")}:duration={T:.3f}:offset={offset:.3f}[{vo}]")
            parts.append(f"[{alast}][{i}:a]acrossfade=d={T:.3f}:c1=tri:c2=tri[{ao}]")
            vlast, alast = vo, ao
            length = length + durs[i] - T
        fc = ";".join(parts)
        cmd += ["-filter_complex", fc, "-map", f"[{vlast}]", "-map", f"[{alast}]"]
        total = length
    else:
        for d in durs[:-1]:
            starts.append(starts[-1] + d)
        ins = "".join(f"[{i}:v][{i}:a]" for i in range(n))
        cmd += ["-filter_complex", f"{ins}concat=n={n}:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]"]
        total = sum(durs)
    cmd += ["-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", str(out)]
    sh(cmd, "unión de segmentos")
    return total, starts


# ---------------------------------------------------------------- subtítulos
def auto_subtitles(video, lang="es", words_per_line=3):
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        print("⚠ Subtítulos automáticos omitidos: falta faster-whisper (pip install faster-whisper).")
        return []
    print("… transcribiendo audio para subtítulos (faster-whisper)")
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(video), language=lang, word_timestamps=True, vad_filter=True)
    words = [w for s in segments for w in (s.words or [])]
    cues = []
    for i in range(0, len(words), words_per_line):
        chunk = words[i:i + words_per_line]
        cues.append({"start": chunk[0].start, "end": chunk[-1].end, "text": " ".join(w.word.strip() for w in chunk)})
    return cues


BRAND_FIXES = {
    r"\bdel taller\b": "de la fábrica",
    r"\bel taller\b": "la fábrica",
    r"\bsun?g? ?des[ie]?(?:gn|ng|n)\b": "Sundesign",
    r"\btaller\b": "fábrica",
}


def fix_text(text, extra=None):
    for pat, new in {**BRAND_FIXES, **(extra or {})}.items():
        text = re.sub(pat, new, text, flags=re.IGNORECASE)
    return text


def read_srt(path):
    cues = []
    blocks = re.split(r"\n\s*\n", Path(path).read_text(encoding="utf-8-sig").strip())
    for b in blocks:
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", b)
        if not m:
            continue
        g = list(map(int, m.groups()))
        st = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        en = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        text = " ".join(l for l in b.splitlines() if "-->" not in l and not l.strip().isdigit())
        cues.append({"start": st, "end": en, "text": text})
    return cues


# ---------------------------------------------------------------- textos (ASS)
def build_ass(plan, W, H, brand, total, card_start, subtitle_cues, out):
    font = brand["font"]
    tfont = brand.get("font_titulos", font)
    dark = ass_color(brand.get("color_texto_cierre", "#1E1E1C"))
    txt = ass_color(brand["color_texto"])
    box = ass_color(brand["color_caja"], 0x30)
    acc = ass_color(brand["color_acento"])
    black = "&H00000000"
    # Zona segura: Instagram/TikTok tapan ~ 15% arriba y ~ 22% abajo con su interfaz.
    top_m = int(H * 0.14)
    bot_m = int(H * 0.24)
    s = int(W / 1080 * 100) / 100  # escala para otros formatos
    styles = [
        # Name, Font, Size, Primary, Secondary, Outline, Back, Bold, Italic, U, S, ScX, ScY, Sp, Ang, BorderStyle, Outline, Shadow, Align, ML, MR, MV
        f"Style: hook,{font},{int(96*s)},{txt},{txt},{box},{box},-1,0,0,0,100,100,0,0,3,18,0,8,70,70,{top_m},1",
        f"Style: label,{font},{int(76*s)},{txt},{txt},{box},{box},-1,0,0,0,100,100,0,0,3,14,0,2,70,70,{bot_m},1",
        f"Style: center,{font},{int(84*s)},{txt},{txt},{black},{black},-1,0,0,0,100,100,0,0,1,4,3,5,70,70,0,1",
        f"Style: sub,{font},{int(140*s)},{txt},{txt},{black},&H80000000,-1,0,0,0,100,100,0,0,1,4,3,2,90,90,{int(H*0.22)},1",
        # Títulos estilo Sundesign: amarillo, condensado, grande, arriba (ARMADO / COMPACTO Y ELEGANTE)
        f"Style: titulo,{tfont},{int(360*s)},{acc},{acc},{black},&H90000000,0,0,0,0,100,100,0,0,1,3,4,8,60,60,{int(H*0.06)},1",
        f"Style: bajada,{font},{int(84*s)},{acc},{acc},{black},&H90000000,-1,0,0,0,100,100,0,0,1,2,2,8,60,60,{int(H*0.06)+int(330*s)},1",
        # Promo gigante en negro (20% OFF)
        f"Style: promo,{tfont},{int(400*s)},{dark},{dark},{txt},&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,40,40,0,1",
        f"Style: cta,{font},{int(92*s)},{dark},{dark},{black},{black},-1,0,0,0,100,100,0,0,1,0,0,5,80,80,0,1",
        f"Style: cta_acento,{font},{int(100*s)},{acc},{acc},{dark},{black},-1,0,0,0,100,100,0,0,1,1,0,5,80,80,0,1",
    ]
    events = []

    def add(style, st, en, text, extra=""):
        fade = "{\\fad(180,180)}"
        events.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},{style},,0,0,0,,{fade}{extra}{ass_escape(text)}")

    pos_style = {"top": "hook", "bottom": "label", "center": "center"}
    for t in plan.get("texts", []):
        style = t.get("style") or pos_style.get(t.get("position", "top"), "hook")
        st = float(t.get("start", 0))
        en = float(t.get("end", st + 2.5))
        extra = ""
        if t.get("size"):
            extra += f"{{\\fs{int(t['size'])}}}"
        efecto = t.get("effect") or {"titulo": "revelar", "promo": "pop", "hook": "pop"}.get(style)
        if efecto == "pop":
            extra += "{\\fscx70\\fscy70\\t(0,180,\\fscx108\\fscy108)\\t(180,260,\\fscx100\\fscy100)}"
        elif efecto == "revelar":  # aparece de izquierda a derecha, como máquina de escribir
            extra += f"{{\\clip(0,0,0,{H})\\t(0,{int(t.get('reveal_ms', 450))},\\clip(0,0,{W},{H}))}}"
        text = t["text"].upper() if t.get("upper", style in ("titulo", "bajada")) else t["text"]
        add(style, st, min(en, total), fix_text(text), extra)

    for c in subtitle_cues:
        if card_start is not None and c["start"] >= card_start:
            continue
        text = fix_text(c["text"], plan.get("subtitle_fixes"))
        add("sub", c["start"], c["end"], text.upper() if plan.get("subtitles_upper", False) else text)

    card = plan.get("end_card")
    if card and card_start is not None:
        lines = card.get("lines", [])
        first_y = card.get("text_y", 0.55)
        step = card.get("line_gap", 0.065)
        for i, line in enumerate(lines):
            style = "cta_acento" if i == len(lines) - 1 and card.get("last_line_accent", True) else "cta"
            y = int(H * (first_y + i * step))
            add(style, card_start + 0.15 + i * 0.12, total, line, f"{{\\an5\\pos({W//2},{y})}}")

    header = (
        "[Script Info]\nScriptType: v4.00+\nWrapStyle: 0\nScaledBorderAndShadow: yes\n"
        f"PlayResX: {W}\nPlayResY: {H}\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding\n" + "\n".join(styles) + "\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    Path(out).write_text(header + "\n".join(events) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- pasada final
def final_pass(plan, base, W, H, joined, total, card_start, ass_file, out):
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", str(joined)]
    idx = 1
    vchain = "[0:v]"
    parts = []
    logo = plan.get("logo")
    if logo and logo.get("src"):
        cmd += ["-loop", "1", "-i", str((base / logo["src"]).resolve())]
        lw = int(logo.get("width", W * 0.2))
        op = float(logo.get("opacity", 0.9))
        m = int(W * 0.05)
        pos = {
            "top-left": f"{m}:{int(H*0.06)}",
            "top-right": f"W-w-{m}:{int(H*0.06)}",
            "bottom-left": f"{m}:H-h-{int(H*0.25)}",
            "bottom-right": f"W-w-{m}:H-h-{int(H*0.25)}",
        }[logo.get("position", "top-right")]
        enable = f":enable='lt(t,{card_start})'" if card_start is not None else ""
        parts.append(f"[{idx}:v]scale={lw}:-1,format=rgba,colorchannelmixer=aa={op}[lg]")
        parts.append(f"{vchain}[lg]overlay={pos}:shortest=1{enable}[vl]")
        vchain = "[vl]"
        idx += 1
    # Stickers: imágenes que aparecen un rato con "pop" (ej. el logo en círculo a mitad del video)
    for st in plan.get("stickers", []):
        a, b = float(st["start"]), float(st["end"])
        sw = int(st.get("width", W * 0.6))
        cx, cy = float(st.get("x", 0.5)), float(st.get("y", 0.4))
        cmd += ["-loop", "1", "-t", f"{total:.3f}", "-framerate", str(FPS), "-i", str((base / st["src"]).resolve())]
        # escala animada: 0 -> 110% -> 100% en 0,25 s (efecto pop), y fundido de salida
        zexpr = f"if(lt(t-{a},0.18),max(0.05,(t-{a})/0.18*1.1),if(lt(t-{a},0.26),1.1-(t-{a}-0.18)/0.08*0.1,1))"
        parts.append(
            f"[{idx}:v]format=rgba,scale=w='{sw}*({zexpr})':h=-1:eval=frame,"
            f"fade=t=out:st={b-0.2:.3f}:d=0.2:alpha=1[st{idx}]"
        )
        parts.append(
            f"{vchain}[st{idx}]overlay=x='{W}*{cx}-w/2':y='{H}*{cy}-h/2':eval=frame:"
            f"enable='between(t,{a},{b})'[vs{idx}]"
        )
        vchain = f"[vs{idx}]"
        idx += 1

    fontsdir = SKILL_DIR / "assets" / "fonts"
    extra_fonts = plan.get("fonts_dir")
    if extra_fonts:
        fontsdir = (base / extra_fonts).resolve()
    parts.append(f"{vchain}ass='{ff_path(ass_file)}':fontsdir='{ff_path(fontsdir)}',format=yuv420p[vout]")

    music = plan.get("music")
    if music and music.get("src"):
        cmd += ["-stream_loop", "-1", "-i", str((base / music["src"]).resolve())]
        mv = float(music.get("volume", 0.35))
        ms = float(music.get("start", 0))
        fade_out = min(2.0, total / 4)
        parts.append(
            f"[{idx}:a]atrim=start={ms},asetpts=PTS-STARTPTS,atrim=duration={total:.3f},aresample=48000,"
            f"aformat=channel_layouts=stereo,volume={mv},afade=t=in:d=0.4,"
            f"afade=t=out:st={total-fade_out:.3f}:d={fade_out:.3f}[mus]"
        )
        if music.get("duck", True):
            parts.append("[0:a]asplit[voz][sc]")
            parts.append("[mus][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[mduck]")
            parts.append("[voz][mduck]amix=inputs=2:duration=first:normalize=0[amix]")
        else:
            parts.append("[0:a][mus]amix=inputs=2:duration=first:normalize=0[amix]")
        alabel = "[amix]"
    else:
        alabel = "[0:a]"
    parts.append(f"{alabel}loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")

    cmd += [
        "-filter_complex", ";".join(parts), "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out),
    ]
    sh(cmd, "pasada final (logo, textos, música)")


def snapshot(video, total, out_jpg):
    n = 6
    vf = f"fps={n/total:.5f},scale=270:-2,tile={n}x1:padding=4:margin=4"
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(video), "-vf", vf, "-frames:v", "1", str(out_jpg)],
                   capture_output=True)


# ---------------------------------------------------------------- main
def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    plan_path = Path(sys.argv[1]).resolve()
    base = plan_path.parent
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    brand = dict(DEFAULT_BRAND)
    brand_file = SKILL_DIR / "references" / "marca.json"
    if brand_file.exists():
        brand.update(json.loads(brand_file.read_text(encoding="utf-8")))
    brand.update(plan.get("brand", {}))

    W, H = FORMATS[plan.get("format", "9:16")]
    out = (base / plan.get("output", "salida/reel.mp4")).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    segs = list(plan["segments"])
    card = plan.get("end_card")
    if card:
        segs.append({"type": "card", **card})

    tmp = Path(tempfile.mkdtemp(prefix="reel_"))
    try:
        paths, durs = [], []
        for i, seg in enumerate(segs):
            kind = seg.get("type") or ("image" if Path(seg.get("src", "")).suffix.lower()
                                       in {".jpg", ".jpeg", ".png", ".webp", ".bmp"} else "video")
            p = tmp / f"seg{i:02d}.mp4"
            print(f"… segmento {i+1}/{len(segs)} ({kind}) {seg.get('src', '')}")
            if kind == "image":
                d = render_image_segment(seg, W, H, p, base)
            elif kind == "card":
                d = render_card_segment(seg, W, H, p, base, brand)
            else:
                d = render_video_segment(seg, W, H, p, base)
            paths.append(p)
            durs.append(d)

        joined = tmp / "joined.mp4"
        print("… uniendo segmentos")
        kinds = [s_.get("transition_in", plan.get("transition_type")) for s_ in segs]
        total, starts = join_segments(paths, durs, float(plan.get("transition", 0.25)), joined, kinds)
        card_start = starts[-1] if card else None

        cues = []
        subs = plan.get("subtitles")
        if subs == "auto":
            cues = auto_subtitles(joined, plan.get("language", "es"), int(plan.get("words_per_line", 3)))
        elif subs:
            cues = read_srt(base / subs)

        ass_file = tmp / "textos.ass"
        build_ass(plan, W, H, brand, total, card_start, cues, ass_file)
        print("… pasada final")
        final_pass(plan, base, W, H, joined, total, card_start, ass_file, out)

        prev = out.with_name(out.stem + "_preview.jpg")
        snapshot(out, total, prev)
        print(f"\n✓ Listo: {out}  ({total:.1f}s, {W}x{H})")
        print(f"  Vista previa (6 cuadros): {prev}")
        if total > 90:
            print("  ⚠ Dura más de 90 s: Instagram lo publica como reel igual, pero lo ideal son 15–45 s.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
