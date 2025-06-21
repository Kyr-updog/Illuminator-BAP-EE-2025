#order: speed (2 bytes), dir, r, g, b
from serial import Serial
from time import sleep, time

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
    do_send = False
    case = 0
    
    if animationSpeed > 255 : animationSpeed = 255
    if direction > 1 : direction = 1
    if red > 255 : red = 255
    if green > 255 : green = 255
    if blue > 255 : blue = 255 #don't send invalid values
    
    while not do_send:
        checks = [False, False, False, False, False] #if all phases are done at the end, the transfer is good, otherwise it should be redone.
        do_send = True
        if case <=1:
            connection.write(animationSpeed.to_bytes(1, "big"))
            case = int.from_bytes(connection.read(1), 'big')+1
            if case != 2:
                do_send = False
            else:
                checks[0] = True #when done, check 
                
        if case == 2:
            connection.write(direction.to_bytes(1, "big"))
            case = int.from_bytes(connection.read(1), 'big')+1
            if case != 3:
                do_send = False
            else:
                checks[1] = True
                
        if case ==3:
            connection.write(red.to_bytes(1, "big"))
            case = int.from_bytes(connection.read(1), 'big')+1
            if case != 4:
                do_send = False
            else:
                checks[2] = True
                
        if case <=4:
            connection.write(green.to_bytes(1, "big"))
            case = int.from_bytes(connection.read(1), 'big')+1
            if case != 5:
                do_send = False
            else:
                checks[3] = True
                
        if case <=5:
            connection.write(blue.to_bytes(1, "big"))
            case = int.from_bytes(connection.read(1), 'big')+1
            if case != 6:
                do_send = False
            else:
                checks[4] = True
                id = int.from_bytes(connection.read(1), 'big')
                return_dummy = int.from_bytes(connection.read(1), 'big')
        
        if False in checks:
            do_send = False
            case = 0
        
    if return_dummy == 2: #number to string
        return_dummy = 'sender'
    else:
        return_dummy = 'dummy'
    return id, return_dummy

if __name__ == "__main__":#testing function; usually doesn't run as you only run the function of this script
    connection = Serial("/dev/ttyACM0", timeout=1) #if it takes at least the timeout, then it errors
    for j in [0,0.5,1,2,3,4,5]: #all delay times for easier automated testing
        file = open("delay_"+str(j)+".csv", 'w')
        for i in range(100):
            begin_time = time()
            ID = sendPixelData(connection, 100, True, 30, 50, 50)
            file.write(str(time()-begin_time)+"\n")

            sleep(j)

        print(f"done: {j}")

