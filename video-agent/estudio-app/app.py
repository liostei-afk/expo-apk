#!/usr/bin/env python3
"""Estudio de Reels — Sundesign Muebles.

App local (solo en esta PC) para que un operador cargue videos crudos, guion y referencias de estilo,
y siga la edición que hace Claude en Cowork: storyboard para aprobar, video final, correcciones y caption.

Se abre con el ícono del escritorio (lo crea instalar.bat). No necesita instalar nada más que Python.
Todo se guarda en la carpeta de trabajo (por defecto: Documentos\\Reels Sundesign), que es la que se
conecta en Cowork.
"""
import json
import mimetypes
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import unicodedata
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

APP_DIR = Path(__file__).resolve().parent
WEB = APP_DIR / "web"
CONFIG = APP_DIR / "config.json"
PORT = 8765
HOST = "127.0.0.1"   # solo accesible desde esta PC

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm", ".3gp"}
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
AUDIO_EXT = {".mp3", ".m4a", ".wav", ".aac"}

# Estados de un trabajo. "quien" = de quién es el próximo paso.
ESTADOS = {
    "borrador": ("Borrador", "operador"),
    "pendiente": ("Esperando a Claude: storyboard", "claude"),
    "cambios_storyboard": ("Esperando a Claude: rehacer storyboard", "claude"),
    "storyboard_listo": ("Storyboard para aprobar", "operador"),
    "aprobado": ("Esperando a Claude: edición", "claude"),
    "editando": ("Claude está editando", "claude"),
    "listo": ("Video listo para revisar", "operador"),
    "correccion": ("Esperando a Claude: corrección", "claude"),
    "bloqueado": ("Claude necesita una respuesta", "operador"),
    "publicado": ("Publicado", "nadie"),
    "archivado": ("Archivado", "nadie"),
}


# ------------------------------------------------------------------ utilidades
def load_config():
    cfg = {}
    if CONFIG.exists():
        try:
            cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        except ValueError:
            cfg = {}
    if not cfg.get("carpeta"):
        docs = Path.home() / "Documents"
        if not docs.exists():
            docs = Path.home() / "Documentos"
        cfg["carpeta"] = str((docs if docs.exists() else Path.home()) / "Reels Sundesign")
    return cfg


def save_config(cfg):
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


CFG = load_config()
ROOT = Path(CFG["carpeta"])
LOCK = threading.Lock()


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def slug(text, n=40):
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:n] or "video"


def safe_name(name):
    name = Path(unquote(name)).name
    stem, ext = os.path.splitext(name)
    return f"{slug(stem, 60)}{ext.lower()}"


def inside(path, base):
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def read_json(p, default):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(p, data):
    p = Path(p)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def ensure_workspace():
    for d in ("trabajos", "estilos", "musica"):
        (ROOT / d).mkdir(parents=True, exist_ok=True)
    seed_style()
    write_readme()
    write_cola()


def seed_style():
    """Crea el estilo inicial "Sundesign clásico" a partir de la ficha de la skill, si no hay ninguno."""
    est = ROOT / "estilos"
    if any(p.is_dir() for p in est.iterdir()):
        return
    d = est / "sundesign-clasico"
    (d / "referencias").mkdir(parents=True, exist_ok=True)
    src = APP_DIR.parent / "sundesign-editor-reels" / "references" / "estilo_sundesign.md"
    ficha = src.read_text(encoding="utf-8") if src.exists() else "# Sundesign clásico\n"
    (d / "estilo.md").write_text(ficha, encoding="utf-8")
    write_json(d / "estilo.json", {"nombre": "Sundesign clásico", "estado": "listo", "creado": now(),
                                   "notas": "Estilo actual de la marca: presentador + demostración, títulos amarillos, "
                                            "subtítulos blancos, barridos, logo en círculo, promo gigante.",
                                   "historial": [{"fecha": now(), "evento": "Creado desde el reel de referencia"}]})
    write_json(est / "estilos.json", {"predeterminado": "sundesign-clasico"})


def write_readme():
    p = ROOT / "LEEME-CLAUDE.md"
    p.write_text(
        "# Carpeta del Estudio de Reels de Sundesign\n\n"
        "Esta carpeta la maneja la app **Estudio de Reels**. Claude: usá la skill **sundesign-editor-reels** y seguí "
        "`references/protocolo-app.md` de esa skill. La lista de lo que hay que hacer está siempre en **COLA.md**.\n\n"
        "- `trabajos/<id>/` — un video por carpeta: `pedido.json`, `guion.md`, `brutos/`, `salida/`, `estado.json`.\n"
        "- `estilos/<id>/` — fichas de estilo: `referencias/` (videos), `estilo.md`, `estilo.json`.\n"
        "- `musica/` — música libre de derechos para usar de fondo.\n", encoding="utf-8")


def job_dir(jid):
    d = ROOT / "trabajos" / jid
    if not re.fullmatch(r"[a-z0-9-]+", jid) or not d.is_dir():
        raise KeyError(jid)
    return d


def style_dir(sid):
    d = ROOT / "estilos" / sid
    if not re.fullmatch(r"[a-z0-9-]+", sid) or not d.is_dir():
        raise KeyError(sid)
    return d


def list_files(d, exts=None):
    if not d.exists():
        return []
    out = []
    for f in sorted(d.iterdir()):
        if f.is_file() and not f.name.startswith(".") and (exts is None or f.suffix.lower() in exts):
            out.append({"nombre": f.name, "ruta": f.relative_to(ROOT).as_posix(), "tam": f.stat().st_size,
                        "fecha": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")})
    return out


def job_summary(d):
    pedido = read_json(d / "pedido.json", {})
    est = read_json(d / "estado.json", {"estado": "borrador"})
    code = est.get("estado", "borrador")
    label, quien = ESTADOS.get(code, (code, "claude"))
    videos = [f for f in list_files(d / "salida", VIDEO_EXT) if re.search(r"_v\d+\.mp4$", f["nombre"])]
    thumb = d / "miniatura.jpg"
    return {"id": d.name, "titulo": pedido.get("titulo") or d.name, "producto": pedido.get("producto", ""),
            "estado": code, "estado_txt": label, "quien": quien, "actualizado": est.get("actualizado", ""),
            "versiones": len(videos), "miniatura": thumb.relative_to(ROOT).as_posix() if thumb.exists() else None,
            "mensaje": est.get("mensaje", "")}


def job_full(jid):
    d = job_dir(jid)
    s = job_summary(d)
    s["pedido"] = read_json(d / "pedido.json", {})
    s["guion"] = (d / "guion.md").read_text(encoding="utf-8") if (d / "guion.md").exists() else ""
    s["estado_json"] = read_json(d / "estado.json", {})
    s["brutos"] = list_files(d / "brutos")
    sal = d / "salida"
    files = list_files(sal)
    s["salida"] = files
    s["videos"] = sorted([f for f in files if re.search(r"_v\d+\.mp4$", f["nombre"])],
                         key=lambda f: int(re.search(r"_v(\d+)\.mp4$", f["nombre"]).group(1)))
    s["storyboards"] = [f for f in files if "storyboard" in f["nombre"] and f["nombre"].endswith((".jpg", ".png"))]
    s["imagenes"] = [f for f in files if f["nombre"].endswith((".jpg", ".png")) and f not in s["storyboards"]]
    texts = {}
    for name in ("caption.md", "guion_propuesto.md", "resumen.md"):
        if (sal / name).exists():
            texts[name] = (sal / name).read_text(encoding="utf-8")
    for f in files:
        if f["nombre"].endswith("_revision.md"):
            texts[f["nombre"]] = (sal / f["nombre"]).read_text(encoding="utf-8")
    s["textos"] = texts
    return s


def style_summary(d):
    meta = read_json(d / "estilo.json", {})
    default = read_json(ROOT / "estilos" / "estilos.json", {}).get("predeterminado")
    refs = list_files(d / "referencias")
    return {"id": d.name, "nombre": meta.get("nombre", d.name), "estado": meta.get("estado", "por_analizar"),
            "notas": meta.get("notas", ""), "predeterminado": d.name == default, "referencias": refs,
            "ficha": (d / "estilo.md").read_text(encoding="utf-8") if (d / "estilo.md").exists() else "",
            "muestras": [f for f in list_files(d) if f["nombre"].endswith((".jpg", ".png"))],
            "historial": meta.get("historial", [])[-8:]}


def set_job_state(d, code, evento, texto="", extra=None):
    est = read_json(d / "estado.json", {"historial": []})
    est["estado"] = code
    est["actualizado"] = now()
    est.setdefault("historial", []).append({"fecha": now(), "quien": "operador", "evento": evento, "texto": texto})
    if code != "bloqueado":
        est.pop("mensaje", None)
    if extra:
        est.update(extra)
    write_json(d / "estado.json", est)


# ------------------------------------------------------------------ cola para Claude
def write_cola():
    lines = ["# COLA — lo que Claude tiene que hacer", "",
             f"_Actualizado: {now()}. Esta lista la genera la app; no la edites a mano._", "",
             "Usá la skill **sundesign-editor-reels** y seguí `references/protocolo-app.md`. "
             "Procesá los ítems en orden. Al terminar cada uno, actualizá su `estado.json` como dice el protocolo.", ""]
    n = 0
    for d in sorted((ROOT / "trabajos").glob("*")):
        if not d.is_dir():
            continue
        est = read_json(d / "estado.json", {})
        code = est.get("estado", "borrador")
        if ESTADOS.get(code, ("", "claude"))[1] != "claude" or code == "editando":
            continue
        n += 1
        ped = read_json(d / "pedido.json", {})
        accion = {
            "pendiente": "Hacer guion propuesto + storyboard (y antes/después si hay color). "
                         + ("El operador pidió **editar directo**: después del storyboard, seguí con la edición sin esperar."
                            if ped.get("directo") else "Dejar en `storyboard_listo`."),
            "cambios_storyboard": "Rehacer el storyboard con los cambios pedidos (ver último mensaje del historial).",
            "aprobado": "Editar, revisar con verify_reel hasta 0 errores, escribir caption.md y resumen.md. Dejar en `listo`.",
            "correccion": "Hacer una versión nueva aplicando la corrección (ver último mensaje del historial) "
                          "y anotarla en la ficha de estilo (Correcciones aprendidas). Dejar en `listo`.",
        }.get(code, "Revisar")
        ultimo = (est.get("historial") or [{}])[-1]
        lines += [f"## {n}. Trabajo `trabajos/{d.name}` — {ped.get('titulo', d.name)}",
                  f"- Estado: `{code}` → {accion}",
                  f"- Estilo: `estilos/{ped.get('estilo') or 'predeterminado'}`"]
        if ultimo.get("texto"):
            lines.append(f"- Último mensaje del operador ({ultimo.get('fecha')}): «{ultimo['texto']}»")
        lines.append("")
    for d in sorted((ROOT / "estilos").glob("*")):
        if d.is_dir() and read_json(d / "estilo.json", {}).get("estado") == "por_analizar":
            n += 1
            lines += [f"## {n}. Estilo `estilos/{d.name}` — analizar referencias",
                      "- Estudiar los videos de `referencias/` y escribir `estilo.md` + `muestra.jpg`. Dejar en `listo`.", ""]
    if n == 0:
        lines.append("**No hay nada pendiente.**")
    (ROOT / "COLA.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return n


def cola_count():
    n = 0
    for d in (ROOT / "trabajos").glob("*"):
        code = read_json(d / "estado.json", {}).get("estado", "borrador")
        if d.is_dir() and ESTADOS.get(code, ("", "claude"))[1] == "claude":
            n += 1
    for d in (ROOT / "estilos").glob("*"):
        if d.is_dir() and read_json(d / "estilo.json", {}).get("estado") == "por_analizar":
            n += 1
    return n


COWORK_PROMPT = ("Usá la skill sundesign-editor-reels. Leé COLA.md de esta carpeta y procesá todo lo pendiente "
                 "siguiendo el protocolo de la app. Avisame con una línea cuando termines cada ítem.")


# ------------------------------------------------------------------ servidor
class Handler(BaseHTTPRequestHandler):
    server_version = "EstudioReels/1.0"

    def log_message(self, fmt, *args):
        pass

    # --- respuestas
    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def fail(self, msg, code=400):
        self.send_json({"error": msg}, code)

    def body_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8") or "{}") if n else {}

    def send_file(self, path):
        if not path.is_file():
            return self.fail("No existe", 404)
        size = path.stat().st_size
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix == ".md":
            ctype = "text/markdown; charset=utf-8"
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        if rng and (m := re.match(r"bytes=(\d*)-(\d*)", rng)):
            if m.group(1):
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else size - 1
            else:
                start = size - int(m.group(2))
            end = min(end, size - 1)
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-cache")
        if parse_qs(urlparse(self.path).query).get("descargar"):
            self.send_header("Content-Disposition", f'attachment; filename="{path.name}"')
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            try:
                while left > 0:
                    chunk = f.read(min(1 << 20, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
            except (ConnectionResetError, BrokenPipeError):
                pass

    # --- GET
    def do_GET(self):
        u = urlparse(self.path)
        p = unquote(u.path)
        try:
            if p in ("/", "/index.html"):
                return self.send_file(WEB / "index.html")
            if p.startswith("/web/"):
                f = (WEB / p[5:]).resolve()
                return self.send_file(f) if inside(f, WEB) else self.fail("No", 403)
            if p.startswith("/archivo/"):
                f = (ROOT / p[9:]).resolve()
                return self.send_file(f) if inside(f, ROOT) else self.fail("No", 403)
            if p == "/api/inicio":
                trabajos = [job_summary(d) for d in sorted((ROOT / "trabajos").glob("*"), reverse=True) if d.is_dir()]
                estilos = [style_summary(d) for d in sorted((ROOT / "estilos").glob("*")) if d.is_dir()]
                musica = list_files(ROOT / "musica", AUDIO_EXT)
                return self.send_json({"carpeta": str(ROOT), "trabajos": trabajos, "estilos": estilos,
                                       "musica": musica, "pendientes": cola_count(), "cowork": COWORK_PROMPT,
                                       "estados": {k: v[0] for k, v in ESTADOS.items()}})
            if m := re.fullmatch(r"/api/trabajo/([a-z0-9-]+)", p):
                return self.send_json(job_full(m.group(1)))
            if p == "/api/cola":
                write_cola()
                return self.send_json({"texto": (ROOT / "COLA.md").read_text(encoding="utf-8")})
            return self.fail("No encontrado", 404)
        except KeyError:
            return self.fail("No existe ese trabajo o estilo", 404)

    # --- PUT: subida de archivos (el cuerpo es el archivo, sin multipart, para videos grandes)
    def do_PUT(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path != "/api/subir":
            return self.fail("No encontrado", 404)
        destino = q.get("destino", [""])[0]
        nombre = safe_name(q.get("nombre", ["archivo"])[0])
        try:
            if m := re.fullmatch(r"trabajo/([a-z0-9-]+)/(brutos|miniatura)", destino):
                d = job_dir(m.group(1))
                target = d / "miniatura.jpg" if m.group(2) == "miniatura" else d / "brutos" / nombre
            elif m := re.fullmatch(r"estilo/([a-z0-9-]+)/referencias", destino):
                target = style_dir(m.group(1)) / "referencias" / nombre
            elif destino == "musica":
                target = ROOT / "musica" / nombre
            else:
                return self.fail("Destino inválido")
        except KeyError:
            return self.fail("No existe", 404)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.name != "miniatura.jpg":
            base, ext = target.stem, target.suffix
            k = 2
            while (target.parent / f"{base}-{k}{ext}").exists():
                k += 1
            target = target.parent / f"{base}-{k}{ext}"
        left = int(self.headers.get("Content-Length") or 0)
        tmp = target.with_name(target.name + ".subiendo")
        try:
            with open(tmp, "wb") as f:
                while left > 0:
                    chunk = self.rfile.read(min(1 << 20, left))
                    if not chunk:
                        break
                    f.write(chunk)
                    left -= len(chunk)
            if left:
                tmp.unlink(missing_ok=True)
                return self.fail("La subida se cortó")
            tmp.replace(target)
        except OSError as e:
            tmp.unlink(missing_ok=True)
            return self.fail(f"No se pudo guardar: {e}", 500)
        write_cola()
        return self.send_json({"ok": True, "ruta": target.relative_to(ROOT).as_posix(), "nombre": target.name})

    # --- POST
    def do_POST(self):
        p = urlparse(self.path).path
        try:
            data = self.body_json()
        except ValueError:
            return self.fail("Datos inválidos")
        with LOCK:
            try:
                return self.route_post(p, data)
            except KeyError:
                return self.fail("No existe", 404)

    def route_post(self, p, data):
        global ROOT
        if p == "/api/trabajo":  # crear
            titulo = (data.get("titulo") or "Video nuevo").strip()
            jid = f"{datetime.now():%Y%m%d-%H%M}-{slug(titulo, 30)}"
            d = ROOT / "trabajos" / jid
            k = 2
            while d.exists():
                d = ROOT / "trabajos" / f"{jid}-{k}"
                k += 1
            (d / "brutos").mkdir(parents=True)
            (d / "salida").mkdir()
            default = read_json(ROOT / "estilos" / "estilos.json", {}).get("predeterminado", "")
            write_json(d / "pedido.json", {"titulo": titulo, "estilo": default, "plataformas": ["instagram", "tiktok"],
                                           "duracion": 30, "creado": now()})
            write_json(d / "estado.json", {"estado": "borrador", "actualizado": now(),
                                           "historial": [{"fecha": now(), "quien": "operador", "evento": "Creado"}]})
            return self.send_json({"id": d.name})

        if m := re.fullmatch(r"/api/trabajo/([a-z0-9-]+)/pedido", p):
            d = job_dir(m.group(1))
            ped = read_json(d / "pedido.json", {})
            guion = data.pop("guion", None)
            ped.update({k: v for k, v in data.items() if k not in ("creado",)})
            write_json(d / "pedido.json", ped)
            if guion is not None:
                (d / "guion.md").write_text(guion, encoding="utf-8")
            return self.send_json({"ok": True})

        if m := re.fullmatch(r"/api/trabajo/([a-z0-9-]+)/accion", p):
            d = job_dir(m.group(1))
            acc, texto = data.get("accion"), (data.get("texto") or "").strip()
            code = read_json(d / "estado.json", {}).get("estado", "borrador")
            if acc == "enviar":
                if not list_files(d / "brutos"):
                    return self.fail("Cargá al menos un video o foto antes de enviar.")
                set_job_state(d, "pendiente", "Enviado a Claude", texto)
            elif acc == "aprobar":
                set_job_state(d, "aprobado", "Storyboard aprobado", texto)
            elif acc == "cambios":
                if not texto:
                    return self.fail("Escribí qué querés cambiar.")
                set_job_state(d, "cambios_storyboard", "Cambios al storyboard", texto)
            elif acc == "correccion":
                if not texto:
                    return self.fail("Escribí qué querés corregir.")
                v = data.get("version") or ""
                set_job_state(d, "correccion", f"Corrección sobre {v}".strip(), texto)
            elif acc == "responder":
                set_job_state(d, data.get("volver_a") or "pendiente", "Respuesta del operador", texto)
            elif acc == "publicado":
                set_job_state(d, "publicado", "Marcado como publicado", texto)
            elif acc == "archivar":
                set_job_state(d, "archivado", "Archivado", texto)
            elif acc == "reabrir":
                set_job_state(d, "borrador" if code in ("archivado",) else "listo", "Reabierto", texto)
            elif acc == "cancelar":
                set_job_state(d, "borrador", "Vuelto a borrador por el operador", texto)
            else:
                return self.fail("Acción desconocida")
            write_cola()
            return self.send_json({"ok": True})

        if p == "/api/borrar-archivo":
            f = (ROOT / data.get("ruta", "")).resolve()
            ok = inside(f, ROOT) and f.is_file() and (f.parent.name in ("brutos", "referencias", "musica"))
            if not ok:
                return self.fail("Solo se pueden borrar archivos cargados por el operador.", 403)
            f.unlink()
            write_cola()
            return self.send_json({"ok": True})

        if p == "/api/estilo":  # crear estilo
            nombre = (data.get("nombre") or "Estilo nuevo").strip()
            sid = slug(nombre, 30)
            d = ROOT / "estilos" / sid
            k = 2
            while d.exists():
                d = ROOT / "estilos" / f"{sid}-{k}"
                k += 1
            (d / "referencias").mkdir(parents=True)
            write_json(d / "estilo.json", {"nombre": nombre, "estado": "borrador", "creado": now(),
                                           "notas": data.get("notas", ""),
                                           "historial": [{"fecha": now(), "evento": "Creado"}]})
            return self.send_json({"id": d.name})

        if m := re.fullmatch(r"/api/estilo/([a-z0-9-]+)/accion", p):
            d = style_dir(m.group(1))
            meta = read_json(d / "estilo.json", {})
            acc = data.get("accion")
            if acc == "analizar":
                if not list_files(d / "referencias"):
                    return self.fail("Cargá al menos un video de referencia.")
                meta["estado"] = "por_analizar"
                meta.setdefault("historial", []).append({"fecha": now(), "evento": "Enviado a analizar",
                                                         "texto": data.get("texto", "")})
            elif acc == "notas":
                meta["notas"] = data.get("texto", "")
                meta["nombre"] = data.get("nombre") or meta.get("nombre")
            elif acc == "predeterminado":
                write_json(ROOT / "estilos" / "estilos.json", {"predeterminado": d.name})
            elif acc == "borrar":
                if read_json(ROOT / "estilos" / "estilos.json", {}).get("predeterminado") == d.name:
                    return self.fail("No se puede borrar el estilo predeterminado.")
                shutil.rmtree(d)
                write_cola()
                return self.send_json({"ok": True})
            else:
                return self.fail("Acción desconocida")
            write_json(d / "estilo.json", meta)
            write_cola()
            return self.send_json({"ok": True})

        if p == "/api/abrir-carpeta":
            target = ROOT
            if data.get("trabajo"):
                target = job_dir(data["trabajo"]) / ("salida" if data.get("salida") else "")
            if sys.platform.startswith("win"):
                os.startfile(str(target))  # noqa
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(target)])
            else:
                subprocess.Popen(["xdg-open", str(target)])
            return self.send_json({"ok": True})

        if p == "/api/abrir-claude":
            return self.send_json({"abierto": open_claude()})

        if p == "/api/carpeta":
            nueva = Path(data.get("carpeta", "")).expanduser()
            if not str(nueva).strip():
                return self.fail("Carpeta inválida")
            nueva.mkdir(parents=True, exist_ok=True)
            CFG["carpeta"] = str(nueva)
            save_config(CFG)
            ROOT = nueva
            ensure_workspace()
            return self.send_json({"ok": True, "carpeta": str(ROOT)})

        return self.fail("No encontrado", 404)


def open_claude():
    """Intenta abrir (o traer al frente) la app de escritorio de Claude. Devuelve True si la encontró."""
    if not sys.platform.startswith("win"):
        return False
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    candidatos = [CFG.get("claude_exe", ""),
                  local / "AnthropicClaude" / "claude.exe",
                  local / "Programs" / "Claude" / "Claude.exe",
                  local / "Programs" / "claude" / "Claude.exe",
                  Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Claude" / "Claude.exe"]
    for c in candidatos:
        if c and Path(c).is_file():
            try:
                subprocess.Popen([str(c)], close_fds=True)
                return True
            except OSError:
                pass
    return False


def already_running():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((HOST, PORT)) == 0


def open_window():
    url = f"http://{HOST}:{PORT}/"
    if sys.platform.startswith("win"):
        # Edge en "modo app": ventana propia, sin barra de direcciones, como un programa
        for exe in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
            if Path(exe).exists():
                subprocess.Popen([exe, f"--app={url}", "--window-size=1280,860"])
                return
    webbrowser.open(url)


def main():
    if already_running():
        open_window()
        return
    ensure_workspace()
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    if "--sin-ventana" not in sys.argv:
        threading.Timer(0.6, open_window).start()
    print(f"Estudio de Reels en http://{HOST}:{PORT}/  ·  carpeta: {ROOT}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
