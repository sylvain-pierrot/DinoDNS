from dinodns.server import DinoDNS
from dinodns.dnsconfig import DnsConfig
import tomllib
import click
import sys
import logging

logger = logging.getLogger(__name__)


@click.command()
@click.argument("Dinofile", type=click.Path(exists=True), required=True)
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
@click.option("--no-debug", is_flag=True, default=False, help="Enable debug mode")
def main(dinofile: click.Path, host: str, port: int, no_debug: bool) -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO if no_debug else logging.DEBUG,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if dinofile:
        try:
            with click.open_file(click.format_filename(dinofile), "rb") as f:
                content = tomllib.load(f)
                _dnsconfig = DnsConfig.from_dict(content)
        except Exception as e:
            logger.error(f"Invalid Dinofile format: {e}")
            return

    server = DinoDNS(host, port)
    server.start()


if __name__ == "__main__":
    main()
