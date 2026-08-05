import time
from xgolib import XGO
from xgoedu import XGOEDU

dog = XGO(port='/dev/ttyAMA0', version="xgolite")

#input xgoedu
#Instantiating edu
edu = XGOEDU()

#Cycle through camera recognition, press the c key to exit
while True:
    result=edu.gestureRecognition()  #Default parameter, using camera recognition by default
    print(result)
    if dog.xgoButton("c"):   #Press the c key to exit the cycle
        break