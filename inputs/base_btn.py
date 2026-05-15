import grovepi


class BaseButton:
    def __init__(self, port: int):
        self.port: int = port
        self._last_state: int = 0
        grovepi.pinMode(self.port, "INPUT")

    def get_value(self) -> int:
        """

        Gets the current value of the button where if it's pressed or not.

        Returns:
            int: Returns 1 if the button is pressed or 0 if the button is not pressed.
        """

        return grovepi.digitalRead(self.port)

    def was_pressed(self) -> bool:
        """

        Checks if the button was pressed by the user and stores the buttons last state to make sure that the no double clicks affect the result.

        Returns:
            bool: Returns true if the button was pressed and false if the button was not pressed.
        """
        
        current_state: int = self.get_value()
        pressed: bool = current_state == 1 and self._last_state == 0
        self._last_state = current_state
        return pressed

    def shutdown(self) -> int:
        """

        Shuts down the button component after resetting its hardware pin.


        Returns:
            int: A status code from the GrovePi indicating the success of the operation.
        """
        return grovepi.pinMode(self.port, "OUTPUT")
