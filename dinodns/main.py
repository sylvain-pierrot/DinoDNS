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
def main(dinofile: click.Path, host: str, port: int) -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if dinofile:
        try:
            with click.open_file(click.format_filename(dinofile), "rb") as f:
                content = tomllib.load(f)
                dnsconfig = DnsConfig.from_dict(content)
                logger.info(dnsconfig)
        except Exception as e:
            logger.error(f"Invalid Dinofile format: {e}")
            return

    server = DinoDNS(host, port)
    server.start()


if __name__ == "__main__":
    main()
