import sys
import traceback
from pathlib import Path
import customtkinter as ctk

from model import ConversionService
from view import AppUI
from controller import AppController


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = Path(__file__).parent.parent

    return Path(base_path) / relative_path


def main():
    # Log to file immediately for debugging
    try:
        log_file = Path("debug_startup.log")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=== Application Start ===\n")
            f.write(f"sys.frozen: {getattr(sys, 'frozen', False)}\n")
            f.write(f"sys._MEIPASS: {getattr(sys, '_MEIPASS', 'Not set')}\n")
            f.write(f"Current dir: {Path.cwd()}\n")
    except Exception:
        pass

    try:
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        template_path = get_resource_path("src/templates/base.html")

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"Template path: {template_path}\n")
                f.write(f"Template exists: {template_path.exists()}\n")
        except:
            pass

        if not template_path.exists():
            print(f"Error: HTML template not found at {template_path}")
            sys.exit(1)

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Initializing ConversionService...\n")
        except:
            pass

        model = ConversionService(template_path=str(template_path))

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("ConversionService initialized successfully\n")
        except:
            pass

        # Initialize View with dummy callbacks
        view = AppUI(pdf_callback=lambda p: None, docx_callback=lambda p: None)

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("AppUI initialized\n")
        except:
            pass

        # Initialize Controller
        controller = AppController(model=model, view=view)

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("AppController initialized\n")
        except:
            pass

        # Bind the true controller callbacks
        view.pdf_callback = controller.start_pdf_conversion
        view.docx_callback = controller.start_docx_conversion

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Callbacks bound. Starting mainloop...\n")
        except:
            pass

        view.mainloop()

    except Exception as e:
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n=== EXCEPTION ===\n")
                f.write(f"{type(e).__name__}: {e}\n")
                f.write(traceback.format_exc())
        except:
            pass
        raise


if __name__ == "__main__":
    main()
