import threading
from model import ConversionService
from view import AppUI

class AppController:
    def __init__(self, model: ConversionService, view: AppUI):
        self.model = model
        self.view = view
        
    def start_pdf_conversion(self, file_path: str):
        self._run_task(self.model.convert_to_pdf, file_path, "PDF")

    def start_docx_conversion(self, file_path: str):
        self._run_task(self.model.convert_to_docx, file_path, "Word (.docx)")

    def _run_task(self, conversion_func, file_path: str, target_name: str):
        thread = threading.Thread(target=self._conversion_task, args=(conversion_func, file_path, target_name))
        thread.daemon = True
        thread.start()
        
    def _conversion_task(self, conversion_func, file_path: str, target_name: str):
        try:
            output_path = conversion_func(file_path)
            self.view.after(0, self.view.conversion_done, True, f"Success: {target_name} saved to {output_path}", output_path)
        except Exception as e:
            self.view.after(0, self.view.conversion_done, False, f"Error converting to {target_name}: {str(e)}", None)

