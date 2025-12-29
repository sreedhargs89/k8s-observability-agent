import os
from .config import load_config
from .logger import setup_logging
from .core.agent import Agent

def main():
    # Load configuration
    config = load_config()
    
    # Setup logging
    setup_logging(config.log_level)
    
    # Init and start agent
    agent = Agent(config)
    agent.start()

if __name__ == "__main__":
    main()
