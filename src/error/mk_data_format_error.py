import os
import time

from resources import config


class MkDataFormatError(RuntimeError):
    def __init__(self, message="", content=None, save_to_file=False):
        if content and save_to_file:
            self.error_file_path = self._generate_id_and_save_to_file(content)
            self.message = f"MkDataFormatError has occurred. The content has been saved to: {self.error_file_path}\n" + message
            super().__init__(self.message)

    @staticmethod
    def _generate_id_and_save_to_file(content):
        file_id = time.time_ns()
        error_file_name = f"error_{file_id}.txt"
        error_file_path = os.path.join(config.ERRORS_DIR, error_file_name)
        with open(error_file_path, "w") as file:
            print(content, file=file)
        return error_file_path
