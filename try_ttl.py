import RPi.GPIO as GPIO
import time

# Pin configuration (using BCM numbering)
PIN_A = 22 # Connect to first TDT input (e.g., DB25 Pin 1)
PIN_B = 6  # Connect to second TDT input (e.g., DB25 Pin 14)
PIN_C = 13
# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_A, GPIO.OUT)
GPIO.setup(PIN_B, GPIO.OUT)
GPIO.setup(PIN_C, GPIO.OUT)

print(f"Starting alternating TTL pulses on GPIO {PIN_A} and {PIN_B}.")
print("Press Ctrl+C to stop.")

try:
    GPIO.output(PIN_A, GPIO.LOW)
    GPIO.output(PIN_B, GPIO.LOW)
    GPIO.output(PIN_C, GPIO.LOW)
    while True:
        # Pulse on PIN_A
        GPIO.output(PIN_A, GPIO.HIGH)
        print(f"GPIO {PIN_A} ON")
        time.sleep(1) # Duration: 1 second
        GPIO.output(PIN_A, GPIO.LOW)
        print(f"GPIO {PIN_A} OFF")
        
        time.sleep(2) # Interval between pulses
        
        # Pulse on PIN_B
        GPIO.output(PIN_B, GPIO.HIGH)
        print(f"GPIO {PIN_B} ON")
        time.sleep(1) # Duration: 1 second
        GPIO.output(PIN_B, GPIO.LOW)
        print(f"GPIO {PIN_B} OFF")
        
        time.sleep(2) # Wait before restarting cycle
        
        
        # Pulse on PIN_C
        GPIO.output(PIN_C, GPIO.HIGH)
        print(f"GPIO {PIN_C} ON")
        time.sleep(1) # Duration: 1 second
        GPIO.output(PIN_C, GPIO.LOW)
        print(f"GPIO {PIN_C} OFF")
        
        time.sleep(2) # Wait before restarting cycle
except KeyboardInterrupt:
    # Cleanup GPIO states on exit
    GPIO.cleanup()
    print("\nProgram stopped and GPIO cleaned up.")