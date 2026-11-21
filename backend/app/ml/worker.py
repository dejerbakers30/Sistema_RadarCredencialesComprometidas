"""Proceso aislado, iniciado por manager; hereda el bloqueo de ejecución."""
import os
import sys


def main():
    # Evitar que bibliotecas nativas sobreocupen la CPU antes de importarlas.
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[key] = "1"
    from app.ml.training import train_run
    train_run(sys.argv[1])


if __name__ == "__main__":
    main()
