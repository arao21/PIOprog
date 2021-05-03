from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep

max_ct=1000
min_out=100

@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_prog():
    # fmt: off
    pull(noblock) .side(0)
    mov(x, osr) #Keep most recent pull data stashed in X, for recycling by noblock     
    mov(y, isr) #ISR must be preloaded with PWM count max
    
    #start pwm loop, pin is low and it will count down y until y=x
    #and then put the pin high and jump 
    label("pwmloop")
    jmp(x_not_y, "skip")
    nop()         .side(1)
    label("skip")
    jmp(y_dec, "pwmloop")
    # fmt: on

#class PIOPWM:
#    def __init__(self, sm_id, pin, max_count, count_freq):
#        self._sm = StateMachine(sm_id, pwm_prog, freq=freq, sideset_base=Pin(pin))
#        
#        #pre-load the isr with the value of max_count
#        self._sm.put(max_count)
#        self._sm.exec("pull()")
#        self._sm.exec("mov(isr, osr)")
#        self._sm.active(1)
#        self._max_count = max_count

#    def set(self, value):
#        #minimum value is -1 (which turns off motor), 0 still produce a narrow pulse
#        value = max(value, -1)
#        value = min(value, self._max_count)
#        self._sm.put(value)

#Setting motor to be in Pin 17 and initializing state machine
mtr_sm= StateMachine(0, pwm_prog, freq=10000000, sideset_base=Pin(17))
mtr_sm.put(max_ct)

#Use exec() to load max count into ISR
mtr_sm.exec("pull()")
mtr_sm.exec("mov(isr, osr)")
mtr_sm.active(1)

#Jerky motor motion
mtr_sm.put(0)
sleep(1)
mtr_sm.put(max_ct)
sleep(2)
mtr_sm.put(0)

#Smooth motor motion
for i in range(max_ct-min_out):
    mtr_sm.put(i+min_out)
    sleep(0.001)
sleep(2)
for i in range(max_ct):
    mtr_sm.put(max_ct-i)
    sleep(0.001)
mtr_sm.put(0)