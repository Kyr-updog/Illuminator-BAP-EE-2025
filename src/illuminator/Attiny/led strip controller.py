#volgorde: speed (2 bytes), dir, r, g, b
from serial import Serial
from time import sleep

def sendPixelData(connection: Serial, animationSpeed: int, direction: bool, red: int, green: int, blue: int):
    """This function sends the data needed for the ATtiny to the ATtiny. When this data is send, it receives the ID of the ATtiny.

    Args:
        connection (Serial): The serial connection to the ATtiny (should be between 0 and 255)
        animationSpeed (int): Animation speed (the time between each light switch)
        direction (bool): The direction of the animation
        red (int): Value of the red light (should be between 0 and 255)
        green (int): Value of the green light (should be between 0 and 255)
        blue (int): Value of the blue light (should be between 0 and 255)
    
    Returns:
        ATtiny ID 
    """
    if animationSpeed > 255 : animationSpeed = 255
    connection.write(animationSpeed.to_bytes())
    connection.write(direction.to_bytes()) #true = 1, false = 0
    if red > 255: red = 255
    connection.write(red.to_bytes())
    if green > 255: green = 255
    connection.write(green.to_bytes())
    if blue > 255: blue = 255
    connection.write(blue.to_bytes())
    
    return int.from_bytes(connection.read(1))

if __name__ == "__main__":
    connection = Serial("COM9")
    sleep(5)
    ID = sendPixelData(connection, 300, False, 200, 50, 12)
    print(ID)