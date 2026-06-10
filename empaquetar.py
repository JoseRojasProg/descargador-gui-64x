#!/usr/bin/env python3
"""
empaquetar.py — Proyecto Ola Digital
Empaqueta main.py con flet pack (PyInstaller) para Linux 64 o Windows 64.

Uso:
    python empaquetar.py           # empaqueta para la plataforma actual
    python empaquetar.py --limpiar # borra build/ y dist/ antes de empaquetar
"""

import os
import sys
import platform
import shutil
import subprocess
import argparse

# ─────────────────────────────────────────────────────────────
#  CONFIGURACIÓN DEL PROYECTO
# ─────────────────────────────────────────────────────────────
SCRIPT = "main.py"
APP_NAME = "DescargadorOlaDigital"
VERSION = "1.0.0"
COMPANY = "Proyecto Ola Digital"
COPYRIGHT = "© 2026 Proyecto Ola Digital"
DESCRIPTION = "Descargador de Videos — Proyecto Ola Digital"

# Iconos según plataforma
ICON_WINDOWS = os.path.join("assets", "logo_POD.ico")
ICON_LINUX = os.path.join("assets", "logo_POD.png")

# Assets a incluir en el ejecutable
ARCHIVOS_EXTRA = [
    (os.path.join("assets", "logo_POD.png"), "assets"),
    (os.path.join("assets", "logo_POD.ico"), "assets"),
    (os.path.join("assets", "logo_instagram.png"), "assets"),
    (os.path.join("assets", "logo_telegram.png"), "assets"),
    (os.path.join("assets", "logo_tiktok.png"), "assets"),
    (os.path.join("assets", "logo_facebook.png"), "assets"),
    (os.path.join("assets", "logo_x.png"), "assets"),
]

DIST_DIR = "dist"

# ─────────────────────────────────────────────────────────────
#  UTILIDADES
# ─────────────────────────────────────────────────────────────


def log(msg, color="\033[96m"):
    reset = "\033[0m"
    print(f"{color}▶ {msg}{reset}")


def ok(msg):
    print(f"\033[92m✓ {msg}\033[0m")


def warning(msg):
    print(f"\033[93m⚠ {msg}\033[0m")


def error(msg):
    print(f"\033[91m✗ {msg}\033[0m")
    sys.exit(1)


def detectar_plataforma():
    s = platform.system()
    if s == "Linux":
        return "linux"
    elif s == "Windows":
        return "windows"
    elif s == "Darwin":
        return "macos"
    else:
        error(f"Plataforma no soportada: {s}")


def verificar_dependencias():
    log("Verificando dependencias…")

    # Verificar flet
    try:
        import flet
        ok(f"Flet {flet.__version__}")
    except ImportError:
        error("Flet no instalado. Corre: pip install flet==0.84.0")

    # Verificar yt-dlp
    try:
        import yt_dlp
        ok(f"yt-dlp {yt_dlp.version.__version__}")
    except ImportError:
        error("yt-dlp no instalado. Corre: pip install yt-dlp")

    # Verificar flet pack
    if shutil.which("flet") is None:
        warning("'flet' no encontrado. Asegúrate de tener flet-cli instalado")


def verificar_archivos():
    log("Verificando archivos del proyecto…")

    if not os.path.exists(SCRIPT):
        error(f"No se encontró '{SCRIPT}'")
    ok(SCRIPT)

    for origen, _ in ARCHIVOS_EXTRA:
        if os.path.exists(origen):
            ok(origen)
        else:
            warning(f"No encontrado: {origen} (opcional)")


def limpiar():
    log("Limpiando build/ y dist/…")
    for carpeta in ["build", DIST_DIR, "__pycache__"]:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
            ok(f"Eliminado: {carpeta}/")


def construir_comando(plataforma):
    cmd = [
        "flet", "pack", SCRIPT,
        "--name", APP_NAME,
        "--distpath", DIST_DIR,
        "--product-name", APP_NAME,
        "--product-version", VERSION,
        "--file-version", VERSION,
        "--company-name", COMPANY,
        "--copyright", COPYRIGHT,
        "--file-description", DESCRIPTION,
    ]

    # Icono según plataforma
    if plataforma == "windows" and os.path.exists(ICON_WINDOWS):
        cmd += ["--icon", ICON_WINDOWS]
        ok(f"Icono Windows: {ICON_WINDOWS}")
    elif plataforma == "linux" and os.path.exists(ICON_LINUX):
        cmd += ["--icon", ICON_LINUX]
        ok(f"Icono Linux: {ICON_LINUX}")

    # Archivos adicionales
    for origen, destino in ARCHIVOS_EXTRA:
        if os.path.exists(origen):
            if plataforma == "windows":
                cmd += ["--add-data", f"{origen};{destino}"]
            else:
                cmd += ["--add-data", f"{origen}:{destino}"]

    # Hidden imports necesarios para yt-dlp
    for mod in ["yt_dlp", "yt_dlp.extractor", "yt_dlp.postprocessor",
                "yt_dlp.downloader", "yt_dlp.extractor.youtube"]:
        cmd += ["--hidden-import", mod]

    return cmd


def empaquetar(plataforma):
    log(f"Empaquetando para {plataforma.upper()}…")
    cmd = construir_comando(plataforma)

    print("\n\033[90m" + " ".join(cmd) + "\033[0m\n")

    resultado = subprocess.run(cmd, text=True)
    if resultado.returncode != 0:
        error("Error durante el empaquetado")


def mostrar_resultado(plataforma):
    sufijo = ".exe" if plataforma == "windows" else ""
    exe = os.path.join(DIST_DIR, f"{APP_NAME}{sufijo}")

    print()
    if os.path.exists(exe):
        size_mb = os.path.getsize(exe) / (1024 * 1024)
        ok(f"Ejecutable generado: {exe} ({size_mb:.1f} MB)")
    else:
        # Buscar en subcarpetas
        for root, _, files in os.walk(DIST_DIR):
            for f in files:
                if APP_NAME.lower() in f.lower():
                    ruta = os.path.join(root, f)
                    size_mb = os.path.getsize(ruta) / (1024 * 1024)
                    ok(f"Ejecutable generado: {ruta} ({size_mb:.1f} MB)")
                    return
        warning(f"No se encontró el ejecutable. Revisa la carpeta {DIST_DIR}/")

# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limpiar", action="store_true")
    args = parser.parse_args()

    print("\n\033[1m\033[96m╔══════════════════════════════════════╗")
    print("║   Empaquetador — Proyecto Ola Digital  ║")
    print("╚══════════════════════════════════════╝\033[0m\n")

    plataforma = detectar_plataforma()
    log(f"Sistema detectado: {platform.system()} {platform.machine()}")

    verificar_dependencias()
    verificar_archivos()

    if args.limpiar:
        limpiar()

    empaquetar(plataforma)
    mostrar_resultado(plataforma)

    print()
    ok("Listo! Puedes distribuir el ejecutable de la carpeta dist/")
    print()


if __name__ == "__main__":
    main()
