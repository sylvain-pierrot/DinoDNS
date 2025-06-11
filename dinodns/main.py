from server import DinoDNS
import sys
import logging
logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    
    server = DinoDNS()
    server.start()

if __name__ == "__main__":
    main()
