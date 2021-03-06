import os
import logging
import logging.config
import yaml

class AuditLogger(logging.getLoggerClass()):
    """ Custom logging class, to ensure that audit log calls always succeed.

        Refer to super()._log() directly to ensure correct stack frame.
    """

    def __init__(self, name):
        # super() call is preferred but we need to cater for Python 2 usage as well.
        super(AuditLogger, self).__init__(name)

        try:
            logging.getLevelName(logging.AUDIT)
        except AttributeError as e:
            setattr(logging, 'AUDIT', logging.CRITICAL * 10)
            logging.addLevelName(logging.AUDIT, 'AUDIT')

        if not self.isEnabledFor(logging.AUDIT):
            raise RuntimeError("logging.AUDIT level is disabled")

    def audit(self, msg, *args, **kwargs):
        """ Add AUDIT level and ensure that it is enabled. """

        # This code derived from logging.log() call.
        if self.isEnabledFor(logging.AUDIT):
            super(AuditLogger, self)._log(logging.AUDIT, msg, args, **kwargs)
        else:
            raise RuntimeError("logging.AUDIT level is disabled")


def get_log_path(name=None):

    # 'logs' directory name is assumed - see "logging.yaml".
    log_path = 'logs'
    return log_path if name is None else log_path + '/' + name


def setup_logging(default_level=logging.INFO):
    """Setup logging configuration. """

    log_path = os.getenv('LOGGING_PATH', 'python_logging/logging.yaml')
    
    # if log_path is None:
    #     raise FileExistsError('Path to logging YAML not found.')
    #

    logging.setLoggerClass(AuditLogger)
    logging.basicConfig(level=default_level)

    # Make sure that directory for logs exists.
    try:
        os.mkdir(get_log_path())
    except OSError as e:
        pass

    if os.path.exists(log_path):
        with open(log_path, 'rt') as f:
            config = yaml.load(f.read())
            logging.config.dictConfig(config)
