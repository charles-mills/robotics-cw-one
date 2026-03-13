import grovepi

class Fan:
    def __init__(self, port):
        self.port = port
        self.power = 0
        grovepi.pinMode(self.port, self.power)
    
    def setValue(self, newPower):
        grovepi.analogWrite(self.port, newPower)
        self.power = newPower

    def getValue(self):
        return grovepi.analogRead(self.port)
    
    def shutdown(self):
        grovepi.pinMode(self.port, "OUTPUT")
