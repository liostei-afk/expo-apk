#!/usr/bin/env python3
"""Transcribe un video con el tiempo exacto de cada palabra (gratis y sin internet, con faster-whisper).

Uso:
    python3 transcribe.py video.mp4 [--out palabras.json] [--model small] [--lang es]

Salida (JSON):
    {"source": "video.mp4", "duration": 61.2,
     "words": [{"i": 0, "w": "Si", "start": 0.52, "end": 0.70, "p": 0.98}, ...],
     "sentences": [{"start_i": 0, "end_i": 7, "start": 0.52, "end": 2.9, "text": "Si vivís con poco espacio..."}]}
Además imprime la transcripción numerada (índice de la primera palabra de cada frase) para revisarla.

Modelos: "small" (rápido, bueno), "medium" (mejor con ruido, más lento). La primera vez descarga el modelo (~0,5–1,5 GB).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

PROMPT = (
    "Sundesign Muebles, showroom en Caballito. Sofá cama, mesas, sillas, mesa ratona, "
    "fábrica propia, amoblar, ambientar, showroom, WhatsApp, cuotas sin interés, efectivo."
)


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def load_audio(path, sr=16000):
    """Decodifica el audio con ffmpeg (evita depender de PyAV)."""
    import numpy as np
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sr),
                        "-f", "s16le", "-"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"No se pudo leer el audio de {path}: {r.stderr.decode()[-300:]}")
    return np.frombuffer(r.stdout, np.int16).astype(np.float32) / 32768.0


def transcribe(path, model_name="small", lang="es"):
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        sys.exit("Falta faster-whisper. Instalalo con:  pip install faster-whisper")
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(
        load_audio(path), language=lang, word_timestamps=True, vad_filter=False,
        initial_prompt=PROMPT, condition_on_previous_text=False,
    )
    words, sentences = [], []
    for seg in segments:
        first = len(words)
        for w in seg.words or []:
            text = w.word.strip()
            if not text:
                continue
            words.append({"i": len(words), "w": text, "start": round(w.start, 3), "end": round(w.end, 3),
                          "p": round(w.probability, 2)})
        if len(words) > first:
            sentences.append({"start_i": first, "end_i": len(words) - 1, "start": words[first]["start"],
                              "end": words[-1]["end"], "text": " ".join(x["w"] for x in words[first:])})
    return words, sentences


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out")
    ap.add_argument("--model", default="large-v3-turbo")
    ap.add_argument("--lang", default="es")
    a = ap.parse_args()
    src = Path(a.video)
    out = Path(a.out) if a.out else src.with_name(src.stem + "_palabras.json")
    print(f"… transcribiendo {src.name} (modelo {a.model})")
    words, sentences = transcribe(src, a.model, a.lang)
    data = {"source": str(src.resolve()), "duration": round(duration(src), 3), "words": words, "sentences": sentences}
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    for s in sentences:
        print(f"[{s['start']:6.2f}–{s['end']:6.2f}] #{s['start_i']:<4} {s['text']}")
    low = [w for w in words if w["p"] < 0.5]
    if low:
        print("\nPalabras dudosas (revisar en subtítulos): " + ", ".join(f"#{w['i']} '{w['w']}'" for w in low[:30]))
    print(f"\n✓ {len(words)} palabras → {out}")


if __name__ == "__main__":
    main()
