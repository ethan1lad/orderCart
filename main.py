from time import sleep
import traceback

from helpers import getCurrentHeight, unlockWallet
from orders import orderCartJob

currHeight = -1
while not sleep(5):
    try:
        unlockWallet()
        newCurrHeight = getCurrentHeight()
        if newCurrHeight >= currHeight + 1:
            orderCartJob()
    except:
        print("Program Crash!" + "\n")
        print(traceback.format_exc())
        print("\nProgram Crash!")