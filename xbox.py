import pygame 
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

#pins declared 

IN1 = 23 #left motor 
IN2 = 24 #left motor 
IN3 = 25 #right motor
IN4 = 18 #right motor
ENA = 12 #left speed 
ENB = 13 #right speed 
SERVO = 21

GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)
GPIO.setup(SERVO, GPIO.OUT)


pwm_left = GPIO.PWM(ENA, 1000)
pwm_right = GPIO.PWM(ENB,1000)
pwm_left.start(30)
pwm_right.start(30)

servo_pwm = GPIO.PWM(SERVO, 50)
servo_pwm.start(0)

#xbox control 

pygame.init()
controller = pygame.joystick.Joystick(0)
controller.init()

DEADZONE = .1
was_centered = False

#helper 

def set_motors(speed):
	speed = max(-1.0, min(1.0, speed))
	
	if speed > 0:
		GPIO.output(IN1, GPIO.HIGH)
		GPIO.output(IN2, GPIO.LOW)
		GPIO.output(IN3, GPIO.HIGH)
		GPIO.output(IN4, GPIO.LOW)
	elif speed < 0:
		GPIO.output(IN1, GPIO.LOW)
		GPIO.output(IN2, GPIO.HIGH)
		GPIO.output(IN3, GPIO.LOW)
		GPIO.output(IN4, GPIO.HIGH)
	else:
		if speed > 0:
			GPIO.output(IN1, GPIO.LOW)
			GPIO.output(IN2, GPIO.LOW)
			GPIO.output(IN3, GPIO.LOW)
			GPIO.output(IN4, GPIO.LOW)
		
	duty_cycle = abs(speed) * 100
	pwm_left.ChangeDutyCycle(duty_cycle)
	pwm_right.ChangeDutyCycle(duty_cycle)

#servo help 
def set_servo_angle(angle):
	
	angle = max(0, min(180, angle))
	duty_cycle = 2 + (angle / 18)
	servo_pwm.ChangeDutyCycle(duty_cycle)

def servo_off():
	servo_pwm.ChangeDutyCycle(0)
	
pygame.event.pump()
time.sleep(.2)
pygame.event.pump()
center_offset = controller.get_axis(0)
	
#main drive 

try:
	while True:
		pygame.event.pump()
		
		throttle = controller.get_axis(5)
		reverse = controller.get_axis(2)
		steering = controller.get_axis(1)
		
		throttle_val = (throttle + 1) / 2
		reverse_val = (reverse + 1) / 2
		
		speed = throttle_val - reverse_val
		
		set_motors(speed)
		
		side_steer = controller.get_axis(0)
		steering = side_steer - center_offset
		
		if abs(steering) < DEADZONE:
			if not was_centered:
				set_servo_angle(90)
				time.sleep(0.3)
				servo_off()
				was_centered = True
		else:
			set_servo_angle( 90 - (steering * 25))
			was_centered = False
				
		time.sleep(.05)
		
		print(f"Throttle: {throttle:.2f}, Steering angle: {steering:.1f}")
		
except KeyboardInterrupt:
	print("stopping...")
	
finally:
	pwm_left.stop()
	pwm_right.stop()
	servo_pwm.stop()
	GPIO.cleanup()
		
		
		
		
		
		
		
		
