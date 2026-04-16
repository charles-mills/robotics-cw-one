import grovepi

'''

Class names = UpperCaseWhateverItsCalled
Method names = like_this
Variable names = like_this

'''

class Led:
    def __init__(self, port: int) -> None:
        self.port: int = port
        grovepi.pinMode(self.port, "OUTPUT")
        self._light_state: bool = False
    
    def get_value(self) -> int :
        return grovepi.ultrasonicRead(self.port)

    @property
    def light_state(self) -> bool:
        return self._light_state

    @light_state.setter
    def light_state(self, value: bool) -> None:
        self._light_state = value