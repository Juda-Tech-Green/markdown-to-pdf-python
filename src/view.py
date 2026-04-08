import os
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False

# We dynamically create a base class that includes DnD wrapper if available
if HAS_DND:
    class BaseApp(ctk.CTk, TkinterDnD.DnDWrapper):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.TkdndVersion = TkinterDnD._require(self)
else:
    class BaseApp(ctk.CTk):
        pass

class AppUI(BaseApp):
    def __init__(self, pdf_callback: Callable[[str], None], docx_callback: Callable[[str], None]):
        super().__init__()
        
        self.title("Markdown to PDF & Word")
        self.geometry("700x500")
        self.minsize(600, 400)
        
        self.pdf_callback = pdf_callback
        self.docx_callback = docx_callback
        self.selected_file_path: Optional[str] = None
        self.last_output_path: Optional[str] = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=0) # Progress bar
        self.grid_rowconfigure(4, weight=1) # Log
        
        self._build_ui()
        
        if HAS_DND:
            self.path_entry.drop_target_register(DND_FILES)
            self.path_entry.dnd_bind('<<Drop>>', self.on_drop)
            self.log_message("Drag & Drop support enabled.")
        else:
            self.log_message("Drag & Drop support not available. Fallback: Browse button.")

    def _build_ui(self):
        self.header_label = ctk.CTkLabel(
            self, text="Markdown Converter", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.file_frame.grid_columnconfigure(0, weight=1)
        
        placeholder = "Drop a .md file here or browse..." if HAS_DND else "Browse for a .md file..."
        self.path_entry = ctk.CTkEntry(self.file_frame, placeholder_text=placeholder, state="disabled")
        self.path_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        
        self.browse_button = ctk.CTkButton(self.file_frame, text="Browse", width=80, command=self.on_browse)
        self.browse_button.grid(row=0, column=1, padx=(5, 10), pady=10)
        
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        
        self.pdf_button = ctk.CTkButton(
            self.button_frame, text="Convert to PDF", command=self.on_convert_pdf, state="disabled", height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.pdf_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.docx_button = ctk.CTkButton(
            self.button_frame, text="Convert to Word", command=self.on_convert_docx, state="disabled", height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.docx_button.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.open_button = ctk.CTkButton(
            self.button_frame, text="Open Result", command=self.on_open_last, state="disabled", height=40,
            font=ctk.CTkFont(size=13, weight="bold"), fg_color="#2ecc71", hover_color="#27ae60"
        )
        self.open_button.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        
        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        self.log_textbox = ctk.CTkTextbox(self, state="disabled", height=150)
        self.log_textbox.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="nsew")

    def on_drop(self, event):
        path = event.data
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
        if path.lower().endswith('.md'):
            self.set_file_path(path)
        else:
            self.log_message("Error: Please drop a valid Markdown (.md) file.")

    def on_browse(self):
        file_path = filedialog.askopenfilename(
            title="Select a Markdown file",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if file_path:
            self.set_file_path(file_path)
            
    def set_file_path(self, path: str):
        self.selected_file_path = path
        self.path_entry.configure(state="normal")
        self.path_entry.delete(0, 'end')
        self.path_entry.insert(0, path)
        self.path_entry.configure(state="disabled")
        self.pdf_button.configure(state="normal")
        self.docx_button.configure(state="normal")
        self.open_button.configure(state="disabled")
        self.log_message(f"Selected: {os.path.basename(path)}")
        
    def on_convert_pdf(self):
        self._start_conversion(self.pdf_callback, "PDF")

    def on_convert_docx(self):
        self._start_conversion(self.docx_callback, "Word (.docx)")

    def _start_conversion(self, callback, target_name):
        if self.selected_file_path:
            self.pdf_button.configure(state="disabled")
            self.docx_button.configure(state="disabled")
            self.browse_button.configure(state="disabled")
            self.progress_bar.start()
            self.log_message(f"Starting conversion to {target_name}...")
            callback(self.selected_file_path)
            
    def conversion_done(self, success: bool, message: str, output_path: Optional[str] = None):
        self.progress_bar.stop()
        self.pdf_button.configure(state="normal")
        self.docx_button.configure(state="normal")
        self.browse_button.configure(state="normal")
        self.log_message(message)
        if success and output_path:
            self.last_output_path = output_path
            self.open_button.configure(state="normal")
            
    def on_open_last(self):
        if self.last_output_path and os.path.exists(self.last_output_path):
            import sys
            import subprocess
            path = self.last_output_path
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        else:
            self.log_message("Error: Result file not found.")
        
    def log_message(self, message: str):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
