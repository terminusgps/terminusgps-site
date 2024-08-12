
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "WARNING",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": "WARNING",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": "terminusgps.log",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        },
        "terminusgps_tracker.models": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "terminusgps_tracker.wialonapi": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "terminusgps_tracker.markdown_processor": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "__main__": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
    }
}
