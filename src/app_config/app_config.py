import logging

import coloredlogs


def config():
    config_logger()
    logging.info("App has been configured")


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

    logging.info("Logger has been configured")
