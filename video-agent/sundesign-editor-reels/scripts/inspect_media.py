#!/usr/bin/env python3
"""Inspecciona clips y fotos para que Claude pueda "ver" el material antes de editar.

Uso:
    python3 inspect_media.py <carpeta_o_archivos...> [--out inspeccion] [--frames 12]

Por cada video genera:
  - datos técnicos (duración, resolución, orientación, fps, si tiene audio, volumen medio)
  - cortes de escena detectados (segundos)
  - una hoja de contactos JPG con miniaturas y su minuto:segundo, para mirarla y elegir los mejores momentos
Por cada foto: resolución y orientación.
Escribe todo en <out>/resumen.json y muestra un resumen legible.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm", ".3gp"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp"}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe falló con {path}: {r.stderr.strip()}")
    return json.loads(r.stdout)


def video_info(path):
    data = probe(path)
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    if v is None:
        raise RuntimeError(f"{path} no tiene pista de video")
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    rot = int(v.get("tags", {}).get("rotate", rot))
    if abs(rot) in (90, 270):
        w, h = h, w
    num, den = (v.get("avg_frame_rate") or "30/1").split("/")
    fps = round(float(num) / float(den), 2) if float(den) else 30.0
    dur = float(data["format"].get("duration") or v.get("duration") or 0)
    return {
        "archivo": str(path),
        "tipo": "video",
        "duracion_s": round(dur, 2),
        "ancho": w,
        "alto": h,
        "orientacion": "vertical" if h > w else ("cuadrado" if h == w else "horizontal"),
        "fps": fps,
        "tiene_audio": a is not None,
    }


def mean_volume(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "volumedetect", "-f", "null", "-"])
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", r.stderr)
    return float(m.group(1)) if m else None


def scene_cuts(path, threshold=0.3):
    r = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-an",
        "-vf", f"scale=320:-2,select='gt(scene,{threshold})',showinfo", "-f", "null", "-",
    ])
    return [round(float(t), 2) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def contact_sheet(path, dur, out_jpg, frames=12):
    cols = 4
    rows = max(1, -(-frames // cols))
    rate = frames / max(dur, 0.1)
    vf = (
        f"fps={rate:.5f},scale=360:-2,"
        "drawtext=text='%{pts\\:hms}':x=8:y=8:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=6,"
        f"tile={cols}x{rows}:padding=6:margin=6"
    )
    r = run(["ffmpeg", "-hide_banner", "-y", "-i", str(path), "-vf", vf, "-frames:v", "1", "-q:v", "4", str(out_jpg)])
    if r.returncode != 0:
        print(f"  (no se pudo hacer la hoja de contactos: {r.stderr.strip().splitlines()[-1:]})", file=sys.stderr)
        return None
    return str(out_jpg)


def image_info(path):
    data = probe(path)
    v = data["streams"][0]
    w, h = int(v["width"]), int(v["height"])
    return {
        "archivo": str(path),
        "tipo": "foto",
        "ancho": w,
        "alto": h,
        "orientacion": "vertical" if h > w else ("cuadrado" if h == w else "horizontal"),
    }


def collect(inputs):
    files = []
    for p in map(Path, inputs):
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.suffix.lower() in VIDEO_EXT | IMAGE_EXT)
        elif p.exists():
            files.append(p)
        else:
            print(f"No existe: {p}", file=sys.stderr)
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", default="inspeccion")
    ap.add_argument("--frames", type=int, default=12)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for f in collect(args.inputs):
        try:
            if f.suffix.lower() in IMAGE_EXT:
                info = image_info(f)
            else:
                info = video_info(f)
                info["volumen_medio_db"] = mean_volume(f) if info["tiene_audio"] else None
                info["cortes_de_escena_s"] = scene_cuts(f)
                info["hoja_contactos"] = contact_sheet(f, info["duracion_s"], out / f"{f.stem}_contactos.jpg", args.frames)
            results.append(info)
        except Exception as e:  # seguimos con el resto
            results.append({"archivo": str(f), "error": str(e)})

    (out / "resumen.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
    for r in results:
        if "error" in r:
            print(f"✗ {r['archivo']}: {r['error']}")
        elif r["tipo"] == "foto":
            print(f"🖼  {r['archivo']}  {r['ancho']}x{r['alto']} ({r['orientacion']})")
        else:
            print(
                f"🎬 {r['archivo']}  {r['duracion_s']}s  {r['ancho']}x{r['alto']} ({r['orientacion']})  "
                f"audio={'sí' if r['tiene_audio'] else 'no'}  cortes={r['cortes_de_escena_s'][:10]}"
            )
            if r.get("hoja_contactos"):
                print(f"   hoja de contactos: {r['hoja_contactos']}")
    print(f"\nResumen completo: {out / 'resumen.json'}")


if __name__ == "__main__":
    main()
