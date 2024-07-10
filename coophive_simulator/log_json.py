import json


# logger is self.logger, message is the logging message, and data is a dictionary that is converted to JSON format along with the message
# using json.dumps
def log_json(logger, message, data=None):
    log_entry = {"message": message}
    if data:
        log_entry.update(data)
    logger.info(json.dumps(log_entry))
