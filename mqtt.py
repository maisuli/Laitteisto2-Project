import network
from time import sleep
import network
from umqtt.simple import MQTTClient
from analysis import HRV_monitor
import json

# network credentials 
SSID = "KMD652_Group_9"
PASSWORD = "!GrandWorldTour2024"
BROKER_IP = "192.168.50.23" # 

class MQTT:
    def __init__(self):
        pass
        
    def connect_wlan(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)

        while wlan.isconnected() == False:
            print("Connecting to KMD652_Group_9... ")
            sleep(2)
            
        print("Connection successful. Pico IP:", wlan.ifconfig()[0])
        
    def get_timestamp(self):
        try:
            self.connect_wlan()
            
            ntptime.settime()
            local_time = time.localtime(time.time() + 3*3600)
            timestamp = "{:02d}.{:02d}.{:04d} {:02d}:{:02d}".format(local_time[2], local_time[1], local_time[0], local_time[3], local_time[4])
            print(timestamp)
            return timestamp
        except:
            return 2025
    
    def connect_mqtt(self):
        mqtt_client=MQTTClient("", BROKER_IP, 21883)
        mqtt_client.connect(clean_session=True)
        return mqtt_client

'''
# main programme
if __name__ == "__main__":
    mqtt_protocolla.connect_wlan()

    try:
        mqtt_client=mqtt_protocolla.connect_mqtt()
        
    except Exception as e:
        print(f"Failed to connect to MQTT: {e}")
        
    PPIdata = HRV_monitor().HRV_analysis()
    print(PPIdata)
    
    data = {
         "id": 000, # tähän vois pistää 
         "type": "RRI",
         "data": PPIdata,
         "analysis": { "type": "readiness" }
            }
    
    datajson = json.dumps(data)
    
    print(datajson)
    
    try:
        while True:
            # Sending a message every 5 seconds.
            topic = "hr-data"
            message = datajson
            mqtt_client.publish(topic, message)
            print(f"Sending to MQTT: {topic} -> {message}")
            sleep(5)
            
    except Exception as e:
        print(f"Failed to send MQTT message: {e}")
        
# mqtt_protocolla().get_timestamp()

'''
