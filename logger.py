from datetime import datetime


class Log:
    @classmethod
    def info(self, message):
        time = datetime.now().strftime("%H:%M:%S")
        print(f"[{time}][INFO] " + str(message))
    @classmethod
    def console(self, message):
        time = datetime.now().strftime("%H:%M:%S")
        print(f"[{time}][CONSOLE] " + str(message))
    @classmethod
    def warning(self, message):
        time = datetime.now().strftime("%H:%M:%S")
        print(f"[{time}][WARNING] " + str(message))
    @classmethod
    def critical(self, message):
        time = datetime.now().strftime("%H:%M:%S")
        print(f"[{time}][CRITICAL] " + str(message))