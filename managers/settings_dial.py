import grovepi


class SettingsDial:

    def __init__(self):

        # Assumes that the port is D2. Should use D2 since rotary motor requires two ports and D2 is the recommended port
        grovepi.encoder_en()

        self.last_position: int = grovepi.encoderRead()

    def get_rotation(self) -> int:

        current_position: int = grovepi.encoderRead()
        rotation_value = 0

        if current_position > self.last_position:
            rotation_value = 1
        elif current_position < self.last_position:
            rotation_value = -1

        self.last_position = current_position

        return rotation_value
