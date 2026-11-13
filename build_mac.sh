#!/usr/bin/env bash
# Crea "Ciccio IVIM.app" e "CiccioIVIM.dmg" (macOS). Va eseguito SU UN MAC (Intel o Apple Silicon:
# l'app risultante e' per l'architettura del Mac su cui la costruisci).
# Uso, dalla cartella del progetto:
#     bash packaging/build_mac.sh
# Prerequisito: Python 3.10+ da https://www.python.org (include gia' Tk per la finestra grafica).
set -euo pipefail
cd "$(dirname "$0")/.."
WORK="${TMPDIR:-/tmp}/ciccio_ivim_build"

# --- scelta di Python: preferisce le versioni di python.org -------------------
PYBASE="${PYTHON:-}"
if [ -z "$PYBASE" ]; then
    for c in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$c" >/dev/null 2>&1; then PYBASE="$(command -v "$c")"; break; fi
    done
fi
if [ -z "$PYBASE" ]; then
    echo "ERRORE: Python non trovato. Installalo da https://www.python.org/downloads/macos/ e riprova."; exit 1
fi
echo ">> Uso Python: $PYBASE ($("$PYBASE" --version))"
"$PYBASE" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' || {
    echo "ERRORE: serve Python 3.10 o piu' recente. Installalo da https://www.python.org/downloads/macos/"; exit 1; }
"$PYBASE" -c 'import tkinter' 2>/dev/null || {
    echo "ERRORE: questo Python non ha Tk (finestra grafica). Usa Python di python.org"
    echo "        oppure con Homebrew: brew install python-tk"; exit 1; }

# --- ambiente di build ---------------------------------------------------------
rm -rf "$WORK/venv"
"$PYBASE" -m venv "$WORK/venv"
PY="$WORK/venv/bin/python"
echo ">> Installo le dipendenze (qualche minuto)..."
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet . pyinstaller pillow

echo ">> Creo l'app..."
"$PY" packaging/make_icon.py
"$PY" -m PyInstaller --noconfirm --clean --windowed --log-level WARN \
    --name "Ciccio IVIM" \
    --icon "$PWD/packaging/icon.png" \
    --osx-bundle-identifier com.ciccio.ivim \
    --collect-submodules pydicom --collect-data sv_ttk \
    --distpath "$PWD/dist" --workpath "$WORK/work" --specpath "$WORK" \
    "$PWD/packaging/launcher.py"
rm -rf build *.egg-info

APP="dist/Ciccio IVIM.app"
echo ">> Auto-verifica dell'app (phantom DICOM GE -> mappe IVIM)..."
if "$APP/Contents/MacOS/Ciccio IVIM" --selftest "$WORK/selftest"; then
    cat "$WORK/selftest/selftest.txt"
else
    cat "$WORK/selftest/selftest.txt" || true
    echo "ERRORE: l'auto-verifica e' fallita. Copia il messaggio qui sopra e invialo."; exit 1
fi

echo ">> Creo il dmg..."
STAGE="$WORK/dmg"
rm -rf "$STAGE" && mkdir -p "$STAGE"
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"          # per il trascinamento in Applicazioni
rm -f dist/CiccioIVIM.dmg
hdiutil create -volname "Ciccio IVIM" -srcfolder "$STAGE" -ov -format UDZO dist/CiccioIVIM.dmg >/dev/null
echo ""
echo "FATTO: $PWD/dist/CiccioIVIM.dmg"
# L'app non e' firmata: al primo avvio usare tasto destro > Apri (oppure
# xattr -dr com.apple.quarantine "/Applications/Ciccio IVIM.app").
