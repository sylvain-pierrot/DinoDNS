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
@click.option("--no-debug", is_flag=True, default=False, help="Disable debug mode")
def main(catalog_file: click.Path, host: str, port: int, no_debug: bool) -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO if no_debug else logging.DEBUG,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        catalog = Catalog.from_file(catalog_file)
        logger.info(f"Catalog loaded: \n{catalog}")
        server = DinoDNS(host, port, catalog)
        server.start()
    except Exception as e:
        logger.error(f"Invalid Dinofile format: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
