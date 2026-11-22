#!/usr/bin/env python3
"""Convierte preproduccion/plan_rodaje.json en una hoja imprimible (HTML) para la gente que filma:
un dibujo por toma (encuadre, sujeto, movimiento de cámara y lugar que hay que dejar libre para el texto),
qué se ve, qué hacer, qué decir, más el checklist de preparación y las reglas técnicas.

Uso:
    python3 shotlist.py plan_rodaje.json      → plan_rodaje.html al lado
Se abre en la app (o en cualquier navegador) y se imprime / guarda como PDF para mandar por WhatsApp.
"""
import base64
import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANTON = HERE.parent / "assets" / "fonts" / "Anton-Regular.ttf"
Y = "#F9D20A"
INK = "#1E1E1C"

REGLAS = [
    "Celular <b>vertical</b>, cámara trasera, 1080p o 4K a 30 fps (iPhone: Formatos → «Más compatible»).",
    "Limpiar la lente. Luz de frente o de costado: <b>nunca una ventana detrás</b> de lo que filmás.",
    "Si alguien habla: micrófono corbatero y silencio en el lugar (aire, música, teléfonos).",
    "Celular apoyado, trípode o gimbal. Movimientos <b>lentos</b>.",
    "Cada toma <b>al menos 2 veces</b>. Grabá 2 segundos antes y después de la acción.",
    "Si te equivocás hablando, repetí la frase entera: el editor se queda con la última.",
    "Dejá libre la zona marcada como <b>TEXTO</b> en el dibujo: ahí va a ir un título.",
    "Al terminar, subí cada video <b>en el casillero de su toma</b> en el Estudio de Reels.",
]


def esc(s):
    return html.escape(str(s or ""))


# ------------------------------------------------------------------ dibujos (SVG 9:16)
def person(cx, top, h, color=INK):
    """Silueta simple: cabeza + cuerpo. top = y de la cabeza, h = altura total visible."""
    r = h * 0.11
    body_w = h * 0.36
    return (f'<circle cx="{cx}" cy="{top + r}" r="{r:.1f}" fill="{color}"/>'
            f'<rect x="{cx - body_w / 2:.1f}" y="{top + 2.15 * r:.1f}" width="{body_w:.1f}" height="{h - 2.15 * r:.1f}" '
            f'rx="{body_w * 0.35:.1f}" fill="{color}"/>')


def table(cx, y, w, color="#8a6a3a"):
    """Mesa de frente: tapa + patas."""
    return (f'<rect x="{cx - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{w * 0.07:.1f}" rx="2" fill="{color}"/>'
            f'<rect x="{cx - w * 0.42:.1f}" y="{y + w * 0.07:.1f}" width="{w * 0.05:.1f}" height="{w * 0.38:.1f}" fill="{color}"/>'
            f'<rect x="{cx + w * 0.37:.1f}" y="{y + w * 0.07:.1f}" width="{w * 0.05:.1f}" height="{w * 0.38:.1f}" fill="{color}"/>')


def sofa(cx, y, w, color="#7d7f86"):
    h = w * 0.42
    return (f'<rect x="{cx - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h * 0.55:.1f}" rx="6" fill="{color}"/>'
            f'<rect x="{cx - w / 2:.1f}" y="{y + h * 0.4:.1f}" width="{w:.1f}" height="{h * 0.45:.1f}" rx="5" fill="#a3a5ab"/>'
            f'<rect x="{cx - w / 2 - 4:.1f}" y="{y + h * 0.25:.1f}" width="10" height="{h * 0.65:.1f}" rx="4" fill="{color}"/>'
            f'<rect x="{cx + w / 2 - 6:.1f}" y="{y + h * 0.25:.1f}" width="10" height="{h * 0.65:.1f}" rx="4" fill="{color}"/>')


def furniture(producto, cx, y, w):
    p = (producto or "").lower()
    return sofa(cx, y, w) if any(k in p for k in ("sofa", "sofá", "sillon", "sillón", "cama")) else table(cx, y, w)


def sketch(t, producto, W=150, H=266):
    plano = t.get("plano", "medio")
    suj = t.get("sujeto", "presentador")
    mov = t.get("movimiento", "fija")
    zona = t.get("zona_texto", "ninguna")
    g = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="#F4F1EA" stroke="{INK}" stroke-width="2"/>']
    floor = H * 0.78
    if plano in ("general",) or suj == "ambiente":
        g.append(f'<line x1="2" y1="{floor}" x2="{W - 2}" y2="{floor}" stroke="#c9c3b5" stroke-width="2"/>')
        g.append(f'<line x1="2" y1="{H * 0.2}" x2="{W * 0.22}" y2="{H * 0.3}" stroke="#d9d4c8"/><line x1="{W - 2}" y1="{H * 0.2}" x2="{W * 0.78}" y2="{H * 0.3}" stroke="#d9d4c8"/>')
    if plano == "cenital":
        g.append(f'<rect x="{W * 0.25}" y="{H * 0.3}" width="{W * 0.5}" height="{H * 0.4}" rx="6" fill="#8a6a3a"/>')
        for dx, dy in ((0.15, 0.38), (0.15, 0.55), (0.85, 0.38), (0.85, 0.55), (0.5, 0.24), (0.5, 0.76)):
            g.append(f'<circle cx="{W * dx}" cy="{H * dy}" r="{W * 0.07}" fill="#7d7f86"/>')
    elif suj == "presentador":
        if plano == "general":
            g.append(furniture(producto, W * 0.62, floor - W * 0.36, W * 0.55))
            g.append(person(W * 0.33, floor - H * 0.5, H * 0.5))
        elif plano == "medio":
            g.append(person(W * 0.5, H * 0.18, H * 0.95))
        else:  # primer plano / detalle
            g.append(person(W * 0.5, H * 0.12, H * 2.1))
    elif suj in ("producto", "ambiente"):
        if plano == "general":
            g.append(furniture(producto, W * 0.5, floor - W * 0.4, W * 0.75))
        elif plano == "medio":
            g.append(furniture(producto, W * 0.5, H * 0.45, W * 1.05))
        elif plano == "primer_plano":
            g.append(furniture(producto, W * 0.45, H * 0.4, W * 1.9))
        else:  # detalle: textura con lupa
            g.append(f'<circle cx="{W * 0.5}" cy="{H * 0.5}" r="{W * 0.36}" fill="#d8cbb1" stroke="{INK}" stroke-width="3"/>')
            for k in range(-3, 4):
                g.append(f'<line x1="{W * 0.5 - W * 0.3}" y1="{H * 0.5 + k * 9}" x2="{W * 0.5 + W * 0.3}" y2="{H * 0.5 + k * 9 + 6}" stroke="#b39d77" stroke-width="2"/>')
            g.append(f'<line x1="{W * 0.75}" y1="{H * 0.62}" x2="{W * 0.92}" y2="{H * 0.75}" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
    elif suj == "manos":
        if plano != "detalle":
            g.append(furniture(producto, W * 0.5, H * 0.55, W * 1.1))
        cx, cy = W * 0.5, H * 0.45
        g.append(f'<rect x="{cx - 22}" y="{cy}" width="44" height="34" rx="12" fill="#e2b48f"/>')
        for k in range(4):
            g.append(f'<rect x="{cx - 21 + k * 11}" y="{cy - 22}" width="9" height="28" rx="4.5" fill="#e2b48f"/>')
        g.append(f'<rect x="{cx - 14}" y="{cy + 30}" width="28" height="40" fill="#e2b48f"/>')

    # zona de texto (hay que dejarla libre)
    if zona in ("arriba", "abajo"):
        zy = H * 0.07 if zona == "arriba" else H * 0.62
        g.append(f'<rect x="10" y="{zy}" width="{W - 20}" height="{H * 0.14}" rx="6" fill="{Y}" fill-opacity=".35" '
                 f'stroke="{INK}" stroke-dasharray="5 4"/>')
        g.append(f'<text x="{W / 2}" y="{zy + H * 0.085}" text-anchor="middle" font-size="13" font-weight="700" fill="{INK}">TEXTO</text>')

    # movimiento de cámara
    a = f'stroke="#C0392B" stroke-width="4" fill="none" stroke-linecap="round" marker-end="url(#ar)"'
    if mov == "acercarse":
        for x1, y1, x2, y2 in ((14, 14, 38, 38), (W - 14, 14, W - 38, 38), (14, H - 14, 38, H - 38), (W - 14, H - 14, W - 38, H - 38)):
            g.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {a}/>')
    elif mov == "alejarse":
        for x1, y1, x2, y2 in ((38, 38, 14, 14), (W - 38, 38, W - 14, 14), (38, H - 38, 14, H - 14), (W - 38, H - 38, W - 14, H - 14)):
            g.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {a}/>')
    elif mov == "paneo":
        g.append(f'<line x1="20" y1="{H * 0.92}" x2="{W - 20}" y2="{H * 0.92}" {a}/>')
    elif mov == "seguimiento":
        g.append(f'<path d="M20 {H * 0.92} Q {W / 2} {H * 0.84} {W - 20} {H * 0.92}" {a}/>')
    elif mov == "giro":
        g.append(f'<path d="M{W * 0.25} {H * 0.9} A {W * 0.3} {H * 0.05} 0 1 0 {W * 0.75} {H * 0.9}" {a}/>')
    else:
        g.append(f'<text x="{W - 10}" y="{H - 12}" text-anchor="end" font-size="11" font-weight="700" fill="#C0392B">FIJA</text>')

    return (f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><marker id="ar" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">'
            f'<path d="M0,0 L6,3 L0,6 z" fill="#C0392B"/></marker></defs>{"".join(g)}</svg>')


PLANO_TXT = {"general": "Plano general", "medio": "Plano medio", "primer_plano": "Primer plano",
             "detalle": "Detalle", "cenital": "Cenital (desde arriba)"}
MOV_TXT = {"fija": "Cámara fija", "acercarse": "Acercarse despacio", "alejarse": "Alejarse despacio",
           "paneo": "Paneo (girar de costado)", "seguimiento": "Seguir la acción", "giro": "Girar alrededor"}


def product_photo(plan, base):
    rel = plan.get("foto_producto")
    if not rel:
        return ""
    for cand in (base / rel, base.parent.parent.parent / rel, Path(rel)):
        if cand.is_file() and cand.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            mime = "image/png" if cand.suffix.lower() == ".png" else "image/webp" if cand.suffix.lower() == ".webp" else "image/jpeg"
            return f'<img class="pf" src="data:{mime};base64,{base64.b64encode(cand.read_bytes()).decode()}" alt="Producto">'
    return ""


def build(plan, base=Path(".")):
    font = ""
    if ANTON.exists():
        font = ("@font-face{font-family:Anton;src:url(data:font/ttf;base64,"
                + base64.b64encode(ANTON.read_bytes()).decode() + ");}")
    tomas = plan.get("tomas", [])
    total = sum(float(t.get("duracion", 0)) for t in tomas)
    cards = []
    for t in tomas:
        rows = []
        for label, key in (("Se ve", "que_se_ve"), ("Acción", "accion"), ("Extra / seguridad", "extra"), ("Notas", "notas")):
            if t.get(key):
                rows.append(f"<dt>{label}</dt><dd>{esc(t[key])}</dd>")
        if t.get("dice"):
            rows.insert(1, f'<dt>Dice</dt><dd class="dice">«{esc(t["dice"])}»</dd>')
        if t.get("texto_pantalla"):
            rows.append(f'<dt>Texto (edición)</dt><dd><span class="tx">{esc(t["texto_pantalla"])}</span></dd>')
        cards.append(f'''<article class="toma">
  <div class="sk">{sketch(t, plan.get("producto", ""))}</div>
  <div class="info">
    <div class="hd"><span class="n">{esc(t.get("n"))}</span><div><b>{esc(t.get("momento", ""))}</b><small>{esc(t.get("duracion", ""))} s en el video</small></div></div>
    <div class="chips"><span>{esc(PLANO_TXT.get(t.get("plano"), t.get("plano", "")))}</span><span>Ángulo: {esc(t.get("angulo", ""))}</span><span>{esc(MOV_TXT.get(t.get("movimiento"), t.get("movimiento", "")))}</span></div>
    <dl>{"".join(rows)}</dl>
    <div class="ok">☐ Toma 1 &nbsp; ☐ Toma 2 &nbsp; ☐ Subida a la app</div>
  </div>
</article>''')
    prep = "".join(f"<li>☐ {esc(x)}</li>" for x in plan.get("preparar", []))
    if plan.get("orden_rodaje"):
        prep += ('<li style="margin-top:8px"><b>Orden para filmar:</b> '
                 + " → ".join(f"toma {esc(n)}" for n in plan["orden_rodaje"]) + "</li>")
    reglas = "".join(f"<li>{r}</li>" for r in REGLAS)
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Plan de rodaje · {esc(plan.get("titulo", ""))}</title>
<style>{font}
*{{box-sizing:border-box}} body{{margin:0;font-family:"Segoe UI",system-ui,sans-serif;color:{INK};background:#fff;font-size:13.5px}}
.page{{max-width:1000px;margin:0 auto;padding:24px}}
.top{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:4px solid {Y};padding-bottom:10px;margin-bottom:14px}}
.top small{{letter-spacing:2px;font-weight:700;font-size:11px}} h1{{font-family:Anton,Impact,sans-serif;font-weight:400;font-size:34px;margin:2px 0 0;line-height:1.1}}
.meta{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:14px}}
.meta div{{background:#F6F4EF;border-radius:8px;padding:8px 10px}} .meta b{{display:block;font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#6b6b66}}
.pf{{float:right;width:150px;height:150px;object-fit:cover;border-radius:10px;margin:0 0 10px 12px;border:1px solid #e3ded2}}
.cols{{clear:both;display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px}}
.box{{border:1px solid #e3ded2;border-radius:10px;padding:10px 14px}} .box h3{{font-family:Anton,Impact,sans-serif;font-weight:400;font-size:17px;margin:0 0 6px}}
.box ul{{margin:0;padding-left:16px}} .box li{{margin:3px 0}} .box.prep ul{{list-style:none;padding:0}}
.tomas{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.toma{{display:grid;grid-template-columns:150px 1fr;gap:12px;border:1px solid #e3ded2;border-radius:12px;padding:10px;break-inside:avoid;page-break-inside:avoid}}
.hd{{display:flex;gap:10px;align-items:center;margin-bottom:6px}} .n{{background:{INK};color:{Y};font-family:Anton,Impact,sans-serif;font-size:22px;width:40px;height:40px;border-radius:50%;display:grid;place-items:center;flex:none}}
.hd b{{display:block;font-size:15px}} .hd small{{color:#6b6b66}}
.chips{{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:6px}} .chips span{{background:#FFF6C4;border-radius:12px;padding:2px 8px;font-size:11.5px;font-weight:600}}
dl{{margin:0}} dt{{font-size:10.5px;text-transform:uppercase;letter-spacing:.8px;color:#8a8a84;margin-top:5px}} dd{{margin:0}}
.dice{{font-style:italic;font-weight:600}} .tx{{background:{Y};padding:0 4px;font-weight:700}}
.ok{{margin-top:8px;font-size:12px;color:#4a4a46;border-top:1px dashed #ddd;padding-top:6px}}
.pr{{position:fixed;right:18px;bottom:18px;background:{Y};border:0;border-radius:10px;padding:12px 18px;font-weight:700;font-size:15px;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.2)}}
@media (max-width:760px){{.meta,.cols,.tomas{{grid-template-columns:1fr}}}}
@media print{{.pr{{display:none}} .page{{padding:0}} body{{font-size:12px}} @page{{size:A4;margin:12mm}}}}
</style></head><body><div class="page">
<div class="top"><div><small>SUNDESIGN MUEBLES · PLAN DE RODAJE</small><h1>{esc(plan.get("titulo", ""))}</h1></div>
<div style="text-align:right"><b>{len(tomas)} tomas</b><br><small style="letter-spacing:0">≈ {plan.get("duracion") or round(total)} s de video</small></div></div>
{product_photo(plan, base)}<div class="meta"><div><b>Producto</b>{esc(plan.get("producto", ""))}</div><div><b>Dónde</b>{esc(plan.get("locacion", ""))}</div>
<div><b>Quién aparece</b>{esc(plan.get("quien_aparece", ""))}</div><div><b>Duración final</b>{esc(plan.get("duracion", round(total)))} s</div></div>
<div class="cols"><div class="box prep"><h3>Antes de filmar, preparar</h3><ul>{prep or "<li>—</li>"}</ul></div>
<div class="box"><h3>Cómo filmar (siempre)</h3><ul>{reglas}</ul></div></div>
<div class="tomas">{"".join(cards)}</div>
</div><button class="pr" onclick="print()">🖨 Imprimir / PDF</button></body></html>'''


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    plan = json.loads(src.read_text(encoding="utf-8"))
    out = src.with_suffix(".html")
    out.write_text(build(plan, src.parent), encoding="utf-8")
    print(f"✓ Plan de rodaje: {out}  ({len(plan.get('tomas', []))} tomas)")


if __name__ == "__main__":
    main()
