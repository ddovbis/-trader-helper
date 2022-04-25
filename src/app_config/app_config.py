import logging
import os

import coloredlogs

from resources import config

log = logging.getLogger(__name__)


def configure_app():
    config_logger()
    create_dirs()
    log.info("App has been configured")


def config_logger():
    level_styles = dict(
        debug=dict(color='green'),
        info=dict(color='black'),
        warning=dict(color='yellow'),
        error=dict(color='red'),
        critical=dict(color='red', bold=True),
    )

    field_styles = dict(
        asctime=dict(color='black', faint=True),
        hostname=dict(color='magenta'),
        levelname=dict(color='magenta', bold=False),
        name=dict(color='blue'),
        programname=dict(color='cyan'),
        username=dict(color='yellow'),
    )

    # installs on root logger by default
    coloredlogs.install(
        level='INFO',
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        level_styles=level_styles,
        field_styles=field_styles
    )

    log.info("Logger has been configured")


def create_dirs():
    dirs = [config.LSTM_MODELS_PATH, config.ERRORS_DIR]

    for _dir in dirs:
        if not os.path.exists(_dir):
            log.info(f"Create dir: {_dir}")
            os.makedirs(_dir)

    log.info(f"All necessary dirs have been created")
