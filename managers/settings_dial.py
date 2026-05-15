import grovepi


class SettingsDial:

    def __init__(self):

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
