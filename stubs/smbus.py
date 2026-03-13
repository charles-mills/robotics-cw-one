class SMBus:
    def __init__(self, bus=None):
        pass

    def write_byte(self, addr, val):
        pass

    def write_byte_data(self, addr, cmd, val):
        pass

    def read_byte_data(self, addr, cmd):
        return 0

    def close(self):
        pass