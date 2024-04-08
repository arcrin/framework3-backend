import logging

class TAGAppLoggerFilter(logging.Filter):
    def filter(self, record: logging.LogRecord): 
        return not (record.name.startswith("matplotlib") or 
                    record.name.startswith("PIL") or
                    record.name.startswith("asyncio") or 
                    record.name.startswith("trio-websocket"))