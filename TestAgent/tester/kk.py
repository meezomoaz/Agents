"""
Asynchronous Modbus communication agent for VOLTTRON.
"""

__docformat__ = 'reStructuredText'

import logging
import sys
import asyncio
from volttron.platform.vip.agent import Agent, Core
from volttron.platform.agent import utils
import minimalmodbus
import threading
import time


# Setup agent-specific logging
agent_log_file = '/home/taha/async_modbus_agent.log'
agent_logger = logging.getLogger('AsyncModbusAgentLogger')
agent_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(agent_log_file)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
agent_logger.addHandler(file_handler)

utils.setup_logging()
__version__ = '0.1'

class Tester(Agent):
    """
    An agent that performs asynchronous Modbus RTU communication.
    """

    def __init__(self, setting1=1, setting2="some/random/topic", **kwargs):
        # Initialize the agent
        kwargs.pop('config_path', None)
        super(Tester, self).__init__(**kwargs)
        agent_logger.info("Tester agent initialization")
        self.setting1 = setting1
        self.setting2 = setting2
        self.default_config = {"setting1": setting1, "setting2": setting2}
        self.vip.config.set_default("config", self.default_config)

    def modbus_communication(self):
        """
        Synchronous Modbus communication logic to be run in a separate thread.
        """
        agent_logger.info("inside mod fun")
        try:
            agent_logger.info("trying to connect")
            instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # Port name, slave address (unit)
            instrument.serial.baudrate = 9600
            instrument.serial.bytesize = 8
            instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
            instrument.serial.stopbits = 1
            instrument.serial.timeout = 0.1

            while True:
                try:
                    # Synchronous reading of registers
                    response = instrument.read_registers(43133, 10, functioncode=3)
                    agent_logger.info(f"Published input register values: {response}")
                except Exception as e:
                    # Log the error and continue with the next iteration of the loop
                    agent_logger.error(f"An error occurred while reading: {str(e)}")
                
                # Sleep or delay for synchronous operations should be handled appropriately
                time.sleep(5)

        except Exception as e:
            agent_logger.error(f"An error occurred while connecting: {str(e)}")

    def _start_asyncio_loop(self):
        """
        Starts a separate thread for Modbus communication to avoid blocking the asyncio event loop.
        """
        agent_logger.info("Starting Modbus communication in a separate thread")
        modbus_thread = threading.Thread(target=self.modbus_communication, daemon=True)
        modbus_thread.start()

    @Core.receiver('onstart')
    def on_start(self, sender, **kwargs):
        agent_logger.info("AsyncModbusAgent has started")
        self._start_asyncio_loop()

def main():
    """Main method called to start the agent."""
    try:
        utils.vip_main(Tester, version=__version__)
    except Exception as e:
        agent_logger.exception('Unhandled exception in main')

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
