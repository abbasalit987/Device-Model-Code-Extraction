# uvicorn_config.py

# Uvicorn configuration settings for the FastAPI application

import logging

# Application settings
app = "component_warranty_model.main:app"  # Path to your FastAPI application
host = "0.0.0.0"  # Bind to all available interfaces
port = 9500  # Port number to run the server on
reload = True  # Enable auto-reloading for development
log_level = "info"  # Log level (debug, info, warning, error, critical)
workers = 1  # Number of worker processes; adjust based on your deployment

# Logging configuration
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - %(message)s",
            "use_colors": True,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": log_level,
        },
    },
}
