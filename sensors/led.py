import grovepi

class Led:
    def __init__(self, port):
        self.port = port
        pinMode(self.port, "OUTPUT")
    
    def getValue(self):
        return grovepi.ultrasonicRead(self.port)
