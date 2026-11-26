"""
Script de arranque automático para Mi Control de Finanzas Personales.
Verifica dependencias, base de datos y lanza Streamlit en el navegador predeterminado.
"""
import os
from pathlib import Path
import subprocess
import sys
import time
import webbrowser

ROOT_DIR = Path(__file__).resolve().parent
APP_SCRIPT = ROOT_DIR / "src" / "ui" / "app.py"
EXCEL_FILE = ROOT_DIR / "finanzas.xlsx"


def main():
    print("=" * 65)
    print(" 🚀 INICIANDO MI CONTROL DE FINANZAS PERSONALES")
    print("=" * 65)

    # 1. Asegurar que finanzas.xlsx existe
    if not EXCEL_FILE.exists():
        print("📄 Creando base de datos inicial 'finanzas.xlsx' con 10 pestañas...")
        try:
            from src.storage.template_builder import create_master_spreadsheet
            create_master_spreadsheet(EXCEL_FILE, include_demo_data=True)
            print("✅ Base de datos 'finanzas.xlsx' creada con éxito.")
        except Exception as e:
            print(f"⚠️ Error al inicializar plantilla: {e}")

    # 2. Configurar variables de entorno
    os.chdir(str(ROOT_DIR))
    port = 8501

    print(f"\n🌐 Abriendo interfaz gráfica en: http://localhost:{port}")
    print("💡 Presiona Ctrl+C en esta ventana cuando desees cerrar la aplicación.\n")

    # 3. Lanzar Streamlit usando el mismo intérprete de Python
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_SCRIPT),
        f"--server.port={port}",
        "--server.headless=false",
        "--theme.base=dark",
    ]

    try:
        # Abrir navegador tras 1.5 segundos
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(f"http://localhost:{port}")

        import threading
        threading.Thread(target=open_browser, daemon=True).start()

        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 ¡Aplicación detenida correctamente! Hasta pronto.")
    except Exception as e:
        print(f"\n❌ Error al ejecutar Streamlit: {e}")
        input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()
