#!/usr/bin/env python3
"""Limpia un video de presentador a cámara usando la transcripción palabra por palabra:
quita silencios largos, muletillas ("eh", "ehm", "mmm") y frases que se empezaron y se repitieron
(se queda con la ÚLTIMA toma completa).

Uso:
    python3 clean_takes.py video.mp4 [--words video_palabras.json] [--out video_limpio.mp4]
                          [--max-gap 0.30] [--pad 0.08] [--keep-fillers] [--dry-run]
                          [--drop 12-18,40-41]   (índices de palabras a sacar a mano)
                          [--keep 5-9]           (índices a conservar aunque el detector los saque)

Genera:
  - <video>_limpio.mp4            el video limpio (mismo formato que el original)
  - <video>_limpio_palabras.json  las palabras con los tiempos NUEVOS (para subtítulos)
  - <video>_cortes.md             la lista de cortes en lenguaje claro (junto al video limpio)
Con --dry-run solo muestra la lista de cortes, sin renderizar.
"""
import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

FILLERS = {"eh", "ehh", "ehm", "em", "emm", "mm", "mmm", "hmm", "ah", "aah", "eeh", "eee"}


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w%]", "", w)


def parse_ranges(txt):
    out = set()
    for part in filter(None, (txt or "").split(",")):
        a, _, b = part.partition("-")
        out.update(range(int(a), int(b or a) + 1))
    return out


def phrases(words, pause=0.55):
    """Agrupa palabras en frases: corta en pausas o en puntuación final."""
    groups, cur = [], []
    for i, w in enumerate(words):
        if cur and (w["start"] - words[cur[-1]]["end"] > pause):
            groups.append(cur)
            cur = []
        cur.append(i)
        if re.search(r"[.!?…]$", w["w"]):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


def detect_restarts(words, k=3, window=25):
    """Arranques repetidos: si las mismas k palabras vuelven a aparecer poco después,
    todo lo dicho desde la primera vez hasta la segunda era una toma fallida."""
    drop = {}
    keys = [norm(w["w"]) for w in words]
    i = 0
    while i + k <= len(words):
        key = keys[i:i + k]
        if all(key):
            for j in range(i + 1, min(len(words) - k + 1, i + window)):
                if keys[j:j + k] == key:
                    for x in range(i, j):
                        drop[x] = f"toma repetida (se usa la de {words[j]['start']:.1f}s)"
                    i = j - 1
                    break
        i += 1
    return drop


def silences(src, noise_db=-35, min_d=0.25):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-vn", "-af",
                        f"silencedetect=noise={noise_db}dB:d={min_d}", "-f", "null", "-"], capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return list(zip(starts, ends + [1e9] * (len(starts) - len(ends))))


def subtract(spans, holes, keep_gap):
    """Saca de los intervalos los silencios reales (dejando keep_gap/2 de aire a cada lado)."""
    out = []
    for a, b in spans:
        pieces = [[a, b]]
        for s, e in holes:
            s2, e2 = s + keep_gap / 2, e - keep_gap / 2
            if e2 - s2 <= 0.05:
                continue
            nxt = []
            for p, q in pieces:
                if e2 <= p or s2 >= q:
                    nxt.append([p, q])
                else:
                    if s2 > p:
                        nxt.append([p, s2])
                    if e2 < q:
                        nxt.append([e2, q])
            pieces = nxt
        out += pieces
    return [[round(p, 3), round(q, 3)] for p, q in out if q - p > 0.06]


def detect_repeats(words, groups, lookahead=3, k=3):
    """Una frase se considera toma fallida si otra frase posterior (cercana) arranca igual
    o la contiene como prefijo. Devuelve {índice_palabra: motivo}."""
    drop = {}
    keyed = [[norm(words[i]["w"]) for i in g] for g in groups]
    for a in range(len(groups)):
        ka = [x for x in keyed[a] if x]
        if len(ka) < 2:
            continue
        for b in range(a + 1, min(len(groups), a + 1 + lookahead)):
            kb = [x for x in keyed[b] if x]
            n = min(k, len(ka), len(kb))
            same_start = n >= 2 and ka[:n] == kb[:n]
            is_prefix = len(ka) <= len(kb) and kb[:len(ka)] == ka
            if same_start or is_prefix:
                for i in groups[a]:
                    drop[i] = f"toma repetida (se usa la de {words[groups[b][0]]['start']:.1f}s)"
                break
    # Repetición inmediata dentro de una frase: "la mesa la mesa se extiende"
    for g in groups:
        ks = [norm(words[i]["w"]) for i in g]
        for L in (3, 2, 1):
            j = 0
            while j + 2 * L <= len(ks):
                if ks[j:j + L] == ks[j + L:j + 2 * L] and all(ks[j:j + L]) and not (L == 1 and len(ks[j]) < 3):
                    for i in g[j:j + L]:
                        drop.setdefault(i, "palabra repetida")
                    j += L
                else:
                    j += 1
    return drop


def build_keep(words, keep_idx, total, max_gap, pad):
    """Intervalos a conservar: cada palabra con un pequeño margen; los huecos > max_gap se acortan."""
    spans = []
    for i in keep_idx:
        w = words[i]
        s, e = max(0.0, w["start"] - pad), min(total, w["end"] + pad)
        if spans and s - spans[-1][1] <= max_gap:
            spans[-1][1] = max(spans[-1][1], e)
        else:
            spans.append([s, e])
    return [[round(a, 3), round(b, 3)] for a, b in spans if b - a > 0.05]


def render(src, spans, out):
    parts, labels = [], ""
    for n, (a, b) in enumerate(spans):
        d = b - a
        f = min(0.012, d / 4)
        parts.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{n}]")
        parts.append(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d={f},afade=t=out:st={d - f:.4f}:d={f}[a{n}]")
        labels += f"[v{n}][a{n}]"
    parts.append(f"{labels}concat=n={len(spans)}:v=1:a=1[v][a]")
    script = Path(out).with_suffix(".filtro.txt")
    script.write_text(";\n".join(parts))
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", str(src), "-filter_complex_script", str(script),
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-map_metadata", "-1", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    script.unlink(missing_ok=True)
    if r.returncode != 0:
        sys.exit("✗ Error al renderizar el video limpio:\n" + "\n".join(r.stderr.splitlines()[-12:]))


def remap(words, keep_idx, spans):
    out, offset_spans = [], []
    acc = 0.0
    for a, b in spans:
        offset_spans.append((a, b, acc))
        acc += b - a
    for i in keep_idx:
        w = words[i]
        for a, b, off in offset_spans:
            if w["end"] > a and w["start"] < b:  # la palabra cae (aunque sea en parte) en este tramo
                st = off + (max(w["start"], a) - a)
                en = off + (min(w["end"], b) - a)
                out.append({**w, "i": len(out), "orig_i": i, "start": round(st, 3), "end": round(max(en, st + 0.05), 3)})
                break
    return out, acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--words")
    ap.add_argument("--out")
    ap.add_argument("--max-gap", type=float, default=0.30, help="silencio máximo que se deja entre palabras (s)")
    ap.add_argument("--pad", type=float, default=0.08, help="margen antes/después de cada palabra (s)")
    ap.add_argument("--keep-fillers", action="store_true")
    ap.add_argument("--silence-db", type=float, default=-35, help="umbral de silencio (más negativo = más estricto)")
    ap.add_argument("--no-repeats", action="store_true", help="no detectar tomas repetidas")
    ap.add_argument("--drop", default="")
    ap.add_argument("--keep", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    src = Path(a.video)
    wfile = Path(a.words) if a.words else src.with_name(src.stem + "_palabras.json")
    if not wfile.exists():
        sys.exit(f"No encuentro {wfile}. Primero corré: python3 transcribe.py {src}")
    data = json.loads(wfile.read_text(encoding="utf-8"))
    words, total = data["words"], float(data.get("duration") or words[-1]["end"] + 0.5)

    reasons = {}
    if not a.keep_fillers:
        for i, w in enumerate(words):
            if norm(w["w"]) in {norm(f) for f in FILLERS}:
                reasons[i] = "muletilla"
    if not a.no_repeats:
        for i, r in detect_restarts(words).items():
            reasons.setdefault(i, r)
        for i, r in detect_repeats(words, phrases(words)).items():
            reasons.setdefault(i, r)
    for i in parse_ranges(a.drop):
        reasons[i] = "sacado a mano"
    for i in parse_ranges(a.keep):
        reasons.pop(i, None)

    keep_idx = [i for i in range(len(words)) if i not in reasons]
    if not keep_idx:
        sys.exit("No quedó ninguna palabra después de limpiar.")
    spans = build_keep(words, keep_idx, total, a.max_gap, a.pad)
    # El modelo a veces "estira" una palabra sobre un silencio: lo detectamos en el audio y lo sacamos igual.
    spans = subtract(spans, silences(src, a.silence_db), a.max_gap)
    new_words, new_total = remap(words, keep_idx, spans)

    # Informe en lenguaje claro
    lines = [f"# Cortes de {src.name}", "", f"Duración: {total:.1f}s → {new_total:.1f}s "
             f"(se quitan {total - new_total:.1f}s)", "", "## Lo que se saca", ""]
    removed, cur = [], None
    for i, w in enumerate(words):
        if i in reasons:
            if cur and cur["reason"] == reasons[i] and cur["last"] == i - 1:
                cur["text"] += " " + w["w"]
                cur["last"], cur["end"] = i, w["end"]
            else:
                cur = {"reason": reasons[i], "text": w["w"], "first": i, "last": i, "start": w["start"], "end": w["end"]}
                removed.append(cur)
    for r in removed:
        lines.append(f"- {r['start']:.1f}–{r['end']:.1f}s · {r['reason']} · \"{r['text']}\" (palabras #{r['first']}–{r['last']})")
    if not removed:
        lines.append("- (ninguna palabra; solo se acortan silencios)")
    gaps = sum(1 for p, q in zip(spans, spans[1:]) if q[0] - p[1] > 0.05)
    lines += ["", f"Silencios recortados: {gaps}", "", "## Texto final", "",
              " ".join(w["w"] for w in new_words)]
    report = "\n".join(lines)
    print(report)

    if a.dry_run:
        return
    out = Path(a.out) if a.out else src.with_name(src.stem + "_limpio.mp4")
    print(f"\n… renderizando {out.name}")
    render(src, spans, out)
    (out.with_name(out.stem + "_palabras.json")).write_text(json.dumps(
        {"source": str(out.resolve()), "duration": round(new_total, 3), "words": new_words,
         # puntos de corte en el video limpio (los usa jump_zoom para alternar plano normal / cerrado)
         "cuts": [round(sum(b - a for a, b in spans[:k]), 3) for k in range(1, len(spans))
                  if spans[k][0] - spans[k - 1][1] > 0.05]}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    cortes = out.with_name(src.stem + "_cortes.md")  # junto al video limpio: nunca se escribe en la carpeta del original
    cortes.write_text(report + "\n", encoding="utf-8")
    print(f"✓ {out}\n✓ {out.with_name(out.stem + '_palabras.json')}\n✓ {cortes}")


if __name__ == "__main__":
    main()
