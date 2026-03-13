import grovepi

class Led:
    def __init__(self, port):
        self.port = port
        pinMode(self.port, "OUTPUT")
    
    def get_value(self):
        return grovepi.ultrasonicRead(self.port)
