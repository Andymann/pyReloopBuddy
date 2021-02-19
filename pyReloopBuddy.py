import sys, pygame, pygame.midi

# set up pygame
#pygame.midi.init()


CONTROLLERNAME = 'Reloop Buddy'
VIRTUALDEVICE_IN = 'IAC Driver Bus 1'
VIRTUALDEVICE_OUT = 'IAC Driver Bus 2'

hiByte=-1
loByte=-1

iSetCount = 0

# list all midi devices
while iSetCount < 4:
    pygame.midi.init()
    for i in range( 0, pygame.midi.get_count() ):
        try:
            s = pygame.midi.get_device_info(i) 
            (interf, name, input, output, opened) = s
            if output:
                print('out: ' + str(pygame.midi.get_device_info(i)) )
                if CONTROLLERNAME in str(pygame.midi.get_device_info(i)):
                    print('Controller Out set')
                    ControllerOut = pygame.midi.Output(i,0)
                    iSetCount += 1
                elif VIRTUALDEVICE_IN in str(pygame.midi.get_device_info(i)):
                    print('Virtual Out set')
                    VirtualIn = pygame.midi.Output(i,0)
                    iSetCount += 1
            if input:
                print('in: ' + str(pygame.midi.get_device_info(i)) )
                if CONTROLLERNAME in str(pygame.midi.get_device_info(i)):
                    print('Controller In set')
                    ControllerIn = pygame.midi.Input(i)
                    iSetCount += 1
                elif VIRTUALDEVICE_OUT in str(pygame.midi.get_device_info(i)):
                    print('Virtual In set')
                    VirtualOut = pygame.midi.Input(i)
                    iSetCount += 1
        except:
            iSetCount = 0
    if iSetCount == 4:
        print('*** All set up ***')
    else:
        pygame.midi.quit()
        pygame.time.wait(1000)
        iSetCount = 0

while True: 
    if ControllerIn.poll():
        # Hardware -> Traktor
        HardwareMidiIn = ControllerIn.read(1)
        hw_byte0 = (HardwareMidiIn[0][0][0])
        hw_byte1 = (HardwareMidiIn[0][0][1])
        hw_byte2 = (HardwareMidiIn[0][0][2])
        print('From Controller:' + str(HardwareMidiIn))

        if (hw_byte0 == 176) or (hw_byte0 == 177):
            if hw_byte1 == 6:   #jogwheel
                if hw_byte2 <= 63:
                    #print('jogwheel CW')
                    i=0
                    while i<hw_byte2:
                        VirtualIn.write([[[hw_byte0, hw_byte1, 1], 0]])
                        i+=1
                else:
                    #print('jogwheel CCW')
                    i=127
                    while i>=hw_byte2:
                        VirtualIn.write([[[hw_byte0, hw_byte1, 127], 0]])
                        i-=1
            elif hw_byte1 == 9:
                #Tempo HiByte
                hiByte = hw_byte2
            elif hw_byte1 == 63:
                #Tempo loByte
                loByte = hw_byte2

                if (hiByte>-1) and (loByte>-1):
                    #we received valid tempo data
                    iVal = hiByte*127 + loByte
                    if hw_byte0 == 176:
                        print('links ' + str(int(iVal*127/1016)))
                    elif hw_byte0 == 177:
                        print('rechts ' + str(int(iVal*127/1016)))    
                    VirtualIn.write([[[hw_byte0, hw_byte1, int(iVal*127/1016)], 0]])
                    hiByte = -1
                    loByte = -1
            else:   #Pass thru
                VirtualIn.write(HardwareMidiIn)
        else:   #Pass thru
            VirtualIn.write(HardwareMidiIn)

    if VirtualOut.poll():
        #Traktor -> Hardware
        VirtualMidiOut = VirtualOut.read(1)
        sw_byte0 = (VirtualMidiOut[0][0][0])
        sw_byte1 = (VirtualMidiOut[0][0][1])
        sw_byte2 = (VirtualMidiOut[0][0][2])
        print('From Traktor:' + str(VirtualMidiOut))
        ControllerOut.write([[[sw_byte0, sw_byte1, sw_byte2], 0]])
    pygame.time.wait(1)