from time import sleep
from gpiozero import OutputDevice

class WindDriver():
    
    def __init__(self):
        self.A = OutputDevice(18)
        self.B = OutputDevice(23)
        self.C = OutputDevice(24)
        self.D = OutputDevice(25)
        self.p_rated = 10
        
    def cycle(self):
        percentage = 0.9 #90% of max capacity
        wind_gen = percentage * self.p_rated
        motor = wind_gen
        delay_time = (0.0007 - motor/self.p_rated*0.0007 )  + 0.001  # 1 millisecond  #0.0017
        
        
        def step1():
            self.D.on()
            sleep(delay_time)
            self.D.off()
 
        def step2():
            self.D.on()
            self.C.on()
            sleep(delay_time)
            self.D.off()
            self.C.off()
 
        def step3():
            self.C.on()
            sleep(delay_time)
            self.C.off()
 
        def step4():
            self.B.on()
            self.C.on()
            sleep(delay_time)
            self.B.off()
            self.C.off()
 
        def step5():
            self.B.on()
            sleep(delay_time)
            self.B.off()
 
        def step6():
            self.A.on()
            self.B.on()
            sleep(delay_time)
            self.A.off()
            self.B.off()
 
        def step7():
            self.A.on()
            sleep(delay_time)
            self.A.off()
 
        def step8():
            self.D.on()
            self.A.on()
            sleep(delay_time)
            self.D.off()
            self.A.off()
 
        # Perform one fourth of a rotation
        while True:
            step1()
            step2()
            step3()
            step4()
            step5()
            step6()
            step7()
            step8() 
            
if __name__ == "__main__":
    driver = WindDriver()
    driver.cycle()