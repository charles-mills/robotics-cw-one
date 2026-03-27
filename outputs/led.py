import grovepi

class Led:
    def __init__(self, port: int) -> None:
        self.port: int = port
        grovepi.pinMode(self.port, "OUTPUT")
        self.lightState: bool = False
    
    def get_value(self) -> int :
        return grovepi.ultrasonicRead(self.port)


    def set_light_state(self, newLightState : bool) -> None:
        self.lightState = newLightState


    def get_light_state(self) -> bool:
        return self.lightState