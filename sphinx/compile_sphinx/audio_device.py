import pyaudio

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))
#otherwise you can do:
print(p.get_default_input_device_info())
