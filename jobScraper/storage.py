import json
from threading import Lock

class StreamingJsonlWriter:
    def __init__(self, filename):
        self.filename = filename
        self.write_lock = Lock()
        self.file_handle = None

    def __enter__(self):
        self.file_handle = open(self.filename, 'w', encoding='utf-8')
        return self

    def write_rows(self, rows):
        if not rows:
            return
        with self.write_lock:
            for row in rows:
                json.dump(row, self.file_handle, ensure_ascii=False)
                self.file_handle.write('\n')

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file_handle:
            self.file_handle.close()