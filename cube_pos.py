import time
from accelerometer import ICM20948

class CubePositions:
    INVALID = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    FRONT = 5
    BACK = 6
    
pos_txt=['Invalid','Up','Down','Left','Right','Front','Back']

def calculate_valid_position(accel):
    TIMEOUT = 10
    cnt = 0
    
    while(cnt<TIMEOUT):
        cnt+=1
        pos = calculate_position(accel)
        if (pos != CubePositions.INVALID):
            return pos
        time.sleep(0.5)
        
    return CubePositions.INVALID


def calculate_position(accel):
    '''
    Defines position based on accelerometer (x,y,z) measurements
    Returns CubePositions
    '''
    
    # LIMIT must be >0.75
    LIMIT = 0.9
    
    accel = accel.read_accel()
    
    if(accel[0]>LIMIT):
        return CubePositions.RIGHT
    if(accel[0]<-LIMIT):
        return CubePositions.LEFT
    
    if(accel[1]>LIMIT):
        return CubePositions.BACK
    if(accel[1]<-LIMIT):
        return CubePositions.FRONT
    
    if(accel[2]>LIMIT):
        return CubePositions.UP
    if(accel[2]<-LIMIT):
        return CubePositions.DOWN
    
    return CubePositions.INVALID

def cube_position_txt(pos):
    return pos_txt[pos]
