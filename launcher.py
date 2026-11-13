"""Punto di ingresso dell'applicazione impacchettata (PyInstaller).

    Ciccio IVIM                 -> apre l'interfaccia grafica
    Ciccio IVIM --selftest DIR  -> crea un phantom, calcola le mappe e scrive DIR/selftest.txt
    Ciccio IVIM fit|info|...    -> riga di comando (come `ciccio-ivim`)
"""
import multiprocessing
import os
import sys
import traceback


def selftest(outdir):
    os.makedirs(outdir, exist_ok=True)
    report = os.path.join(outdir, "selftest.txt")
    try:
        import numpy as np
        from ciccio_ivim.cli import run_pipeline
        from ciccio_ivim.simulate import make_phantom, write_ge_like_dicom

        data, b, labels, truth = make_phantom(shape=(48, 48, 2), snr=80)
        write_ge_like_dicom(data, b, os.path.join(outdir, "dicom"))
        sel = labels == 1
        lines, ok = [], True
        for method, reg, ric in (("nlls", "none", "none"), ("nlls", "affine", "model"), ("dnn", "translation", "correct")):
            res = run_pipeline(dicom=os.path.join(outdir, "dicom"), out=os.path.join(outdir, f"out_{method}_{reg}"),
                               method=method, register=reg, rician=ric, progress=lambda m: None)
            D = float(np.nanmedian(res["maps"]["D"][sel]))
            good = abs(D / truth["D"][sel][0] - 1) < 0.1
            ok &= good
            lines.append(f"{'OK' if good else 'FAIL'} {method}/{reg}/{ric}: D_fegato={D:.4e} "
                         f"(atteso {truth['D'][sel][0]:.4e})")
        import ciccio_ivim.gui  # noqa: F401  verifica che l'interfaccia (tema incluso) si importi
        import sv_ttk  # noqa: F401
        msg = ("OK" if ok else "FAIL") + "\n" + "\n".join(lines) + "\n"
    except Exception:  # noqa: BLE001
        ok, msg = False, "FAIL\n" + traceback.format_exc()
    with open(report, "w", encoding="utf-8") as fh:
        fh.write(msg)
    return 0 if ok else 1


def main():
    args = sys.argv[1:]
    if args[:1] == ["--selftest"]:
        sys.exit(selftest(args[1] if len(args) > 1 else os.path.join(os.path.expanduser("~"), "ciccio_ivim_selftest")))
    if args:
        from ciccio_ivim.cli import main as cli_main
        sys.exit(cli_main(args))
    from ciccio_ivim.gui import main as gui_main
    gui_main()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
