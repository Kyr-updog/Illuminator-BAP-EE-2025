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
    val = 0
    if animationSpeed > 255 : animationSpeed = 255
    connection.write(animationSpeed.to_bytes())
    while True:
        val = int.from_bytes(connection.read(1))
        if val == 1: #check if the ATtiny wrote to the correct variable (so we check if the data was received well)
            break 
        else:
            connection.write(animationSpeed.to_bytes()) #if not, just resend the data until you are at the correct variable
    #this design can rarely make the led a different color than it's supposed to be, but it's much better than the led strip bricking and requiring a restart. 
    
    connection.write(direction.to_bytes()) #true = 1, false = 0
    while True:
        val = int.from_bytes(connection.read(1))
        if val == 2: 
            break
        else:
            connection.write(direction.to_bytes())
    
    if red > 255: red = 255
    connection.write(red.to_bytes())
    while True:
        val = int.from_bytes(connection.read(1))
        if val == 3:
            break
        else:
            connection.write(red.to_bytes())
    
    if green > 255: green = 255
    connection.write(green.to_bytes())
    while True:
        val = int.from_bytes(connection.read(1))
        if val == 4:
            break
        else:
            connection.write(green.to_bytes())
    
    if blue > 255: blue = 255
    connection.write(blue.to_bytes())
    while True:
        val = int.from_bytes(connection.read(1))
        if val == 5:
            break
        else:
            connection.write(blue.to_bytes())
        
    id = 0
    while id == 0:
        id = int.from_bytes(connection.read(1))
        dummy = int.from_bytes(connection.read(1))
        if dummy == 1:
            return_dummy = True
        else:
            return_dummy = False
    
    return id, return_dummy

if __name__ == "__main__":
    connection = Serial("/dev/ttyACM0", timeout=1)
    for i in range(10):
        ID = sendPixelData(connection, 10, True, i*10, 255, 100)
        print("ID: "+str(ID))
        print("iteration: "+str(i))
        sleep(2)
    print(ID)
