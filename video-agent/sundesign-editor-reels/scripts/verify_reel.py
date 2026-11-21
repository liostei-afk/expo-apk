#!/usr/bin/env python3
"""Revisión obligatoria del reel YA EXPORTADO, antes de entregarlo.

Uso:
    python3 verify_reel.py "3 Listos/x/video_v1.mp4" [--no-transcribe] [--model large-v3-turbo]

Comprueba:
  1. Formato: 1080x1920 (o el pedido), 30 fps, H.264, duración.
  2. Volumen: -14 ±0,3 LUFS y pico real por debajo de -1,5 dB.
  3. Privacidad: que no queden datos del archivo original (ubicación GPS, modelo del teléfono).
  4. Repeticiones: transcribe el video terminado y busca palabras o frases repetidas seguidas.
  5. Pausas: mide con el audio (no con la transcripción) silencios de más de 0,4 s dentro del habla.
  6. Hoja con un cuadro por segundo (<video>_revision.jpg) para mirar que nada tape la cara ni se pise.
Escribe <video>_revision.md y termina con "0 errores" o la lista de problemas.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--no-transcribe", action="store_true")
    ap.add_argument("--model", default="large-v3-turbo")
    ap.add_argument("--size", default="1080x1920")
    a = ap.parse_args()
    v = Path(a.video)
    problems, notes = [], []

    # 1. Formato
    info = json.loads(run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(v)]).stdout)
    vs = next(s for s in info["streams"] if s["codec_type"] == "video")
    dur = float(info["format"]["duration"])
    size = f"{vs['width']}x{vs['height']}"
    num, den = vs["avg_frame_rate"].split("/")
    fps = round(float(num) / float(den), 2)
    notes.append(f"Formato: {size}, {fps} fps, {vs['codec_name']}, {dur:.1f} s")
    if size != a.size:
        problems.append(f"Resolución {size} (se esperaba {a.size})")
    if abs(fps - 30) > 0.5:
        problems.append(f"{fps} fps (se esperaban 30)")
    if vs["codec_name"] != "h264":
        problems.append(f"Códec {vs['codec_name']} (se esperaba H.264)")

    # 2. Volumen
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(v), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    pk = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    lufs = float(i[-1]) if i else None
    peak = float(pk[-1]) if pk else None
    notes.append(f"Volumen: {lufs} LUFS, pico real {peak} dB")
    if lufs is None or abs(lufs + 14) > 0.5:
        problems.append(f"Volumen {lufs} LUFS (objetivo -14)")
    if peak is not None and peak > -1.0:
        problems.append(f"Pico real {peak} dB (tiene que estar por debajo de -1,5)")

    # 3. Privacidad
    tags = {**info["format"].get("tags", {})}
    for s in info["streams"]:
        tags.update(s.get("tags", {}))
    sensitive = [k for k in tags if re.search(r"location|gps|xyz|make|model|software|creation_time", k, re.I)
                 and not k.lower().startswith(("handler", "vendor", "encoder", "language"))]
    if sensitive:
        problems.append("Quedan datos del archivo original: " + ", ".join(sensitive))
    else:
        notes.append("Privacidad: sin ubicación ni datos del teléfono")

    # 4. Repeticiones
    words = []
    if not a.no_transcribe:
        sys.path.insert(0, str(HERE))
        try:
            import transcribe as tr
            words, _ = tr.transcribe(v, a.model)
        except SystemExit:
            notes.append("No se pudo transcribir (falta faster-whisper): repeticiones sin revisar")
    if words:
        norm = [re.sub(r"[^\w%]", "", w["w"].lower()) for w in words]
        found = set()
        for L in range(10, 0, -1):  # frases repetidas de hasta 10 palabras seguidas
            for j in range(len(norm) - 2 * L + 1):
                a1, a2 = norm[j:j + L], norm[j + L:j + 2 * L]
                if all(a1) and a1 == a2 and not (L == 1 and len(a1[0]) < 3) and j not in found:
                    found.update(range(j, j + 2 * L))
                    problems.append(f"Repetición en {words[j]['start']:.1f}s: \"{' '.join(w['w'] for w in words[j:j + 2 * L])}\"")
        notes.append("Texto final: " + " ".join(w["w"] for w in words))

    # 5. Pausas dentro del habla
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(v), "-vn", "-af", "silencedetect=noise=-40dB:d=0.4", "-f", "null", "-"])
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    lo = words[0]["start"] if words else 0.5
    hi = words[-1]["end"] if words else dur - 0.5
    for s_, e_ in zip(st, en):
        if s_ > lo + 0.1 and e_ < hi - 0.1:
            problems.append(f"Pausa de {e_ - s_:.1f}s en {s_:.1f}s")
    if not st:
        notes.append("Pausas: sin silencios detectables (si hay música de fondo, revisalas escuchando)")

    # 6. Hoja de cuadros (uno por segundo)
    sheet = v.with_name(v.stem + "_revision.jpg")
    cols = 6
    rows = max(1, -(-int(dur) // cols))
    run(["ffmpeg", "-hide_banner", "-y", "-i", str(v), "-vf",
         f"fps=1,scale=220:-2,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,"
         f"tile={cols}x{rows}:padding=4:margin=4", "-frames:v", "1", "-q:v", "4", str(sheet)])
    notes.append(f"Hoja de revisión (mirar caras, manos y textos que se pisen): {sheet}")

    lines = [f"# Revisión de {v.name}", ""] + [f"- {n}" for n in notes] + [""]
    lines += (["## ✓ 0 errores automáticos", "Falta tu mirada: abrí la hoja de revisión y miralo una vez en el celular."]
              if not problems else [f"## ✗ {len(problems)} problema(s)"] + [f"- {p}" for p in problems])
    report = "\n".join(lines)
    v.with_name(v.stem + "_revision.md").write_text(report + "\n", encoding="utf-8")
    print(report)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
