import logging

class MyFilter(logging.Filter):
    def filter(self, record): # type: ignore
        return not record.name == "TCNodeLogger"

app_logger = logging.getLogger("")
app_logger.setLevel(logging.DEBUG)

tc_logger = logging.getLogger("TCNodeLogger")

formatter = logging.Formatter("%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler("tag_application.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
file_handler.addFilter(MyFilter())

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
console_handler.addFilter(MyFilter())   

app_logger.addHandler(file_handler)
app_logger.addHandler(console_handler)

app_logger.info("info from application")
tc_logger.info("info from tc_logger")