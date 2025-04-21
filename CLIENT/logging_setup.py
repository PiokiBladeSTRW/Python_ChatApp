import logging

def setup_log():
    client_logger = logging.getLogger("clientLog")
    client_logger.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler('logs/clientLog.log')
    formatter = logging.Formatter("%(asctime)s [%(module)s] -%(levelname)s : %(message)s")
    fileHandler.setFormatter(formatter)

    client_logger.addHandler(fileHandler)
    return client_logger


'''
For Testing One Log file is Sufficient to Contain All Logs and Details
In Future, any time the Application is ran, a new log with current timestamp should be created and a Hard Limit on no of existing Logs at a time
'''