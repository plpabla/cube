from accelerometer import ICM20948
from wifi import WiFi
from ina219 import INA219
from cube_pos import CubePositions, cube_position_txt, calculate_valid_position
from machine import Timer
import time
from machine import I2C

def send_data(t=None):
    acc = ICM20948()
    bat = INA219(addr=0x43)
    
    pos = cube_position_txt(calculate_valid_position(acc))
    v, i, bat = bat.getMeas()
    
    wifi = WiFi()
    
    data_dict = {'meas': pos, 'bat': int(bat)}
    wifi.send_log_data(data_dict)
    

if __name__ == "__main__":
    
    i2c = I2C(1)
    addresses = i2c.scan()
    print("I2C Address(es): ")
    for a in addresses:
        print("\t"+hex(a))
        
    send_data(None)
    send_data_t = Timer(period=5*60_000, mode=Timer.PERIODIC, callback=send_data)
    
    while True:
        time.sleep(30)
