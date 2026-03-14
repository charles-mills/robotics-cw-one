import grovepi

class Button:
    def __init__(self, port):
        self.port = port
        grovepi.pinMode(self.port, "INPUT")
    
    def get_value(self):
        return grovepi.digitalRead(self.port)
    
    def shutdown(self):
        grovepi.pinMode(self.port, "OUTPUT")
