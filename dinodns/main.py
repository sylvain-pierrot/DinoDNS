from dinodns.server import DinoDNS
from dinodns.catalog import Catalog
import click
import sys
import logging

logger = logging.getLogger(__name__)


@click.command()
@click.argument("CATALOG_FILE", type=click.Path(exists=True), required=True)
@click.option(
    "--host",
    "-h",
    type=click.STRING,
    default="0.0.0.0",
    help="Host to listen on (default: 0.0.0.0)",
)
@click.option(
    "--port", "-p", type=click.INT, default=53, help="Port to listen on (default: 53)"
)
@click.option("--debug", is_flag=True, default=False, help="Enable debug mode")
def main(catalog_file: click.Path, host: str, port: int, debug: bool) -> None:
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = (
        "ts=%(asctime)s level=%(levelname)s %(message)s"
        if not debug
        else "ts=%(asctime)s level=%(levelname)s logger=%(name)s line=%(lineno)d %(message)s"
    )
    logging.basicConfig(
        stream=sys.stdout,
        level=log_level,
        format=log_format,
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    try:
        catalog = Catalog.from_file(catalog_file)
        logger.info(f'msg="Catalog loaded" kind=Catalog {catalog}')
        server = DinoDNS(host, port, catalog)
        server.start()
    except Exception as e:
        logger.error(f'msg="Invalid Dinofile format: {e}"')
        sys.exit(1)


if __name__ == "__main__":
    main()
