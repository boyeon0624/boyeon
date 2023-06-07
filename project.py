import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import json

MQTT_HOST = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60
reset_topic= "mobile/boyeon/reset_topic"

MQTT_PUB_TOPIC ="mobile/boyeon/sensing"
client = mqtt.Client()

client.connect (MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
client.loop_start()

# GPIO 핀 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 버튼이 연결된 GPIO 핀 번호
button_pin = 17
# 초록색 LED가 연결된 GPIO 핀 번호
green_led_pin = 23
# 노란색 LED가 연결된 GPIO 핀 번호
yellow_led_pin = 24
# 빨간색 LED가 연결된 GPIO 핀 번호
red_led_pin = 25
# 부저가 연결된 GPIO 핀 번호
buzzer_pin = 12


# 버튼이 눌렸는지 확인하는 함수
def is_button_pressed():
    button_state = GPIO.input(button_pin)
    if button_state == GPIO.HIGH:
        time.sleep(0.09)  # 디바운싱을 위한 시간 지연
        button_state = GPIO.input(button_pin)
        if button_state == GPIO.HIGH:
            return True
    return False

# GPIO 핀 초기화
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(green_led_pin, GPIO.OUT)
GPIO.setup(yellow_led_pin, GPIO.OUT)
GPIO.setup(red_led_pin, GPIO.OUT)
GPIO.setup(buzzer_pin, GPIO.OUT)

# LED 및 부저 초기 상태 설정
GPIO.output(green_led_pin, GPIO.LOW)
GPIO.output(yellow_led_pin, GPIO.LOW)
GPIO.output(red_led_pin, GPIO.LOW)
GPIO.output(buzzer_pin, GPIO.LOW)
# 버튼을 누르는 횟수
button_count = 10


buzzer_pwm=GPIO.PWM(buzzer_pin, 1000)
buzzer_pwm.start(0)

try:
    while True:
       if is_button_pressed():
        button_count -= 1
        print("Button Count:", button_count)
        # 횟수가 7 이상일 때 초록색 LED 켜기
        if button_count >= 7:
            GPIO.output(green_led_pin, GPIO.HIGH)
        else:
            GPIO.output(green_led_pin, GPIO.LOW)
        # 횟수가 4 이상 6 이하일 때 노란색 LED 켜기
        if 4 <= button_count <= 6:
            GPIO.output(yellow_led_pin, GPIO.HIGH)
        else:
            GPIO.output(yellow_led_pin, GPIO.LOW)
        # 횟수가 1 이상 3 이하일 때 빨간색 LED와 부저 켜기
        if 1 <= button_count <= 3:
            GPIO.output(red_led_pin, GPIO.HIGH)
            buzzer_pwm.ChangeDutyCycle(50)  # 부저의 듀티 사이클 50%로 설정
        else:
            GPIO.output(red_led_pin, GPIO.LOW)
            buzzer_pwm.ChangeDutyCycle(0) 

        # 횟수가 0이면 다시 10으로 리셋
        if button_count == 0:
            button_count = 10
        
            
            print("버튼 횟수 리셋")
        
            sensing ={
                "button_count": button_count
            }
            value = json.dumps(sensing)
            client.publish(reset_topic, str("change"))
            time.sleep(0.1)
            
except KeyboardInterrupt:
    print("I'm done!")
finally:
    GPIO.cleanup()
   
