from server import DinoDNS
import sys
import logging

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    server = DinoDNS()
    server.start()


if __name__ == "__main__":
    main()
