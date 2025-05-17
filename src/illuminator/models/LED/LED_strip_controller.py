#volgorde: speed (2 bytes), dir, r, g, b
from serial import Serial
from time import sleep

def sendPixelData(connection: Serial, animationSpeed: int, direction: bool, red: int, green: int, blue: int):
    connection.write(animationSpeed.to_bytes(2))
    connection.write(direction.to_bytes()) #true = 1, false = 0
    if red > 255: red = 255
    connection.write(red.to_bytes())
    if green > 255: green = 255
    connection.write(green.to_bytes())
    if blue > 255: blue = 255
    connection.write(blue.to_bytes())

if __name__ == "__main__":
    connection = Serial("COM9")
    sleep(5)
    sendPixelData(connection, 300, False, 200, 50, 12)
    print(int.from_bytes(connection.read(2)))
    print(int.from_bytes(connection.read()))
    print(int.from_bytes(connection.read()))
    print(int.from_bytes(connection.read()))
    print(int.from_bytes(connection.read()))