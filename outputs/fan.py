import grovepi

class Fan:
    def __init__(self, port):
        self.port = port
        self.power = 0
        grovepi.pinMode(self.port, self.power)
    
    def set_value(self, new_power):
        grovepi.analogWrite(self.port, new_power)
        self.power = new_power

    def get_value(self):
        return grovepi.analogRead(self.port)
    
    def shutdown(self):
        grovepi.pinMode(self.port, "OUTPUT")
