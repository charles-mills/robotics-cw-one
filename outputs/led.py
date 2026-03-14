import grovepi

class Led:
    def __init__(self, port: int) -> None:
        self.port: int = port
        grovepi.pinMode(self.port, "OUTPUT")
    
    def get_value(self) -> int :
        return grovepi.ultrasonicRead(self.port)
