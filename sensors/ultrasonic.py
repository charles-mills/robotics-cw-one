import grovepi

class Ultrasonic:
    def __init__(self, port):
        grovepi.set_bus("RPI_1")
        self.port = port
    
    def getValue(self):
        return grovepi.ultrasonicRead(self.port)
