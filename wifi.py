import utime, time
from machine import Pin
from machine import UART

class WiFi:
    '''
    Support WiFi module
    '''
    
    uart = None
    
    BASE_URL = 'GET /logger/test.php/?'
    IP = '192.168.100.191'
    
    def __init__(self):
        # TODO: Add fault handling
        self._create_uart()
        self.send_init_commands()

    def send_init_commands(self):
        SSID, password = self._get_credentials('wifi.txt')
        remote_IP = '192.168.100.191'
        remote_Port = '8087'
        local_Port = '1112'
        
        uart = self.uart
        
        uart.write('+++') 
        time.sleep(1)
        if(uart.any()>0):
            uart.read()

        self._sendCMD("AT","OK")
        self._sendCMD("AT+CWMODE=3","OK")
        
        self._sendCMD("AT+CWJAP=\""+SSID+"\",\""+password+"\"","OK",20000)
        self._sendCMD("AT+CIFSR","OK")
        
        self._sendCMD(f'AT+CIPSTART="TCP","{ self.IP }",80',"OK",10000)
        
        self._sendCMD('AT+CIPMODE=1',"OK")
        time.sleep(1)
        
    def send_log_data(self, obj_dict):
        '''
        Send log data for url:
            /logger/test.php/?arg1=x&arg2=y
        arguments and values are given as a dictionary
        '''
        def create_url(obj_dict):
            url = self.BASE_URL
            for k,v in obj_dict.items():
                url = url + f"{k}={v}&"
            return url
                
        msg = create_url(obj_dict)
        
        self._send_wifi_msg(msg)
        
#------------------
# Helper functions
#------------------
    def _create_uart(self):
        # Configuration
        UART_BAUDRATE = 115200
        UART_BITS = 8
        UART_PARITY = None
        UART_STOP = 1
        UART_TX_PIN_NO = 4
        UART_RX_PIN_NO = 5
        UART_MSG_END = '\r\n'
        
        self.uart = UART(1, baudrate=UART_BAUDRATE, bits=UART_BITS,\
                         parity=UART_PARITY, stop=UART_STOP,\
                         tx=Pin(UART_TX_PIN_NO), rx=Pin(UART_RX_PIN_NO))
        
    def _get_credentials(self, fname):
        f = open(fname, 'rt')
        ssid = f.readline().strip()
        pas = f.readline().strip()
        f.close()
        return (ssid, pas)

    def _sendCMD(self, cmd,ack,timeout=2000):
        uart = self.uart
        uart.write(cmd+'\r\n')
        t = utime.ticks_ms()
        while (utime.ticks_ms() - t) < timeout:
            s=uart.read()
            if(s != None):
                s=s.decode()
                # print(s)
                if(s.find(ack) >= 0):
                    return True
        return False
        
    def _send_wifi_msg(self, cmd_uart):
        #cmd_uart = "GET /logger/test.php/?id=69"
        cmd = f'AT+CIPSEND'
        self._sendCMD(cmd,">")
        time.sleep(0.2)
        self.uart.write(cmd_uart+'\r\n')
        self.uart.write('+++\r\n')
        time.sleep(0.2)
        self._sendCMD("AT+CIPCLOSE","OK")
        
