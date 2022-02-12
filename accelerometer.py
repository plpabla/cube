from machine import I2C, Pin
import time

# I2C device address
ACCEL_ADDR = 0x68

# Memory addresses
WHOAMI_ADDR = 0x00
MEMORY_BANK_SEL_ADDR = 0x7F
LP_CONFIG_ADDR = 0x05
PWR_MGMT_1_ADDR = 0x06
PWR_MGMT_2_ADDR = 0x07
ACCEL_XOUT_H_ADDR = 0x2D
ACCEL_CONFIG_ADDR = 0x14

# Register values
WHOAMI_REPLY_ACCEL = bytes([0xEA])
MEMORY_BANK_0 = bytes([0x00])
MEMORY_BANK_1 = bytes([0x10])
MEMORY_BANK_2 = bytes([0x20])
MEMORY_BANK_3 = bytes([0x30])
LP_CONFIG_ENABLE_LP = bytes([0x70])
PWR_MGMG_1_RESET = bytes([0xE0])
PWR_MGMG_1_CLKSEL_AUTO_LP_EN = bytes([0x01])
PWR_MGMG_2_DISABLE_GYRO = bytes([0x07])
ACCEL_CONFIG_FS_2G = bytes([0x00])
ACCEL_CONFIG_FS_4G = bytes([(0x01 << 1)])
ACCEL_CONFIG_FS_8G = bytes([(0x02 << 1)])
ACCEL_CONFIG_FS_16G = bytes([(0x03 << 1)])

# Parameters
ACCEL_SCALE_G = 2 # TODO: support different values in constructor as well. Right now 2G is always set
ACCEL_SCALE = ACCEL_SCALE_G / 32768

class ICM20948:
    '''
    Accelerometer support
    '''
    
    i2c = None
    
    
    def __init__(self):      
        i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=100_000)
        addresses = i2c.scan()
        
        if ACCEL_ADDR not in addresses:
            raise Exception(f'No accelerometer I2C device found - looking for address {ACCEL_ADDR}')
        
        # Check if under ACCEL_ADDR we really have accelerometer by checking WHOAMI registger
        i2c.writeto_mem(ACCEL_ADDR, MEMORY_BANK_SEL_ADDR, MEMORY_BANK_0)
        msg = i2c.readfrom_mem(ACCEL_ADDR, WHOAMI_ADDR, 1)
        
        if(msg!=WHOAMI_REPLY_ACCEL):
            raise Exception(f'No accelerometer under {ACCEL_ADDR}. Whoami reply {msg} different than requested {WHOAMI_REPLY_ACCEL}')
        
        # Accelerometer setup
        # reset device
        i2c.writeto_mem(ACCEL_ADDR, MEMORY_BANK_SEL_ADDR, MEMORY_BANK_0)
        i2c.writeto_mem(ACCEL_ADDR, PWR_MGMT_1_ADDR, PWR_MGMG_1_RESET)
        time.sleep(0.1)
        
        # set clock selection
        i2c.writeto_mem(ACCEL_ADDR, MEMORY_BANK_SEL_ADDR, MEMORY_BANK_0)
        # print(f"Set {int.from_bytes(PWR_MGMG_1_CLKSEL_AUTO_LP_EN,'big')}")
        i2c.writeto_mem(ACCEL_ADDR, PWR_MGMT_1_ADDR, PWR_MGMG_1_CLKSEL_AUTO_LP_EN)
        
        # low power mode
        # TODO: configure low power mode correctly
        # i2c.writeto_mem(ACCEL_ADDR, MEMORY_BANK_SEL_ADDR, MEMORY_BANK_0)
        # i2c.writeto_mem(ACCEL_ADDR, LP_CONFIG_ADDR, LP_CONFIG_ENABLE_LP)        
        
        # disable gyro
        i2c.writeto_mem(ACCEL_ADDR, MEMORY_BANK_SEL_ADDR, MEMORY_BANK_0)
        i2c.writeto_mem(ACCEL_ADDR, PWR_MGMT_2_ADDR, PWR_MGMG_2_DISABLE_GYRO)
        
        # set accelerator range
        i2c.writeto_mem(ACCEL_ADDR, MEMORY_BANK_SEL_ADDR, MEMORY_BANK_2)
        i2c.writeto_mem(ACCEL_ADDR, ACCEL_CONFIG_ADDR, ACCEL_CONFIG_FS_2G)
        
        # TODO: Slow down accelerometer if it consumes too much power
              
        # Store i2c object
        self.i2c = i2c
        
        time.sleep(0.02)
        
    def read_accel(self):
        i2c = self.i2c
        
        i2c.writeto_mem(ACCEL_ADDR, MEMORY_BANK_SEL_ADDR, MEMORY_BANK_0)
        # read 6 following addresses
        msg = i2c.readfrom_mem(ACCEL_ADDR, ACCEL_XOUT_H_ADDR, 6)
        
        accel = [0,0,0]
        
        # odd index contains MLS, evel contains LSB
        accel[0] = (msg[0]<<8)|msg[1]
        accel[1] = (msg[2]<<8)|msg[3]
        accel[2] = (msg[4]<<8)|msg[5]
        
        # uint to int (overflow)
        if accel[0]>=32767:             
          accel[0]=accel[0]-65535
        elif accel[0]<=-32767:
          accel[0]=accel[0]+65535
        if accel[1]>=32767:
          accel[1]=accel[1]-65535
        elif accel[1]<=-32767:
          accel[1]=accel[1]+65535
        if accel[2]>=32767:
          accel[2]=accel[2]-65535
        elif accel[2]<=-32767:
          accel[2]=accel[2]+65535
           
        for idx,val in enumerate(accel):
            accel[idx] = round(accel[idx] * ACCEL_SCALE, 2)
        
        return accel
        
          
        
        
