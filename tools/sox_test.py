import sox

# cli compatibale command string
silence = "sox -d -b 16 output.wav channels 1 rate 16k silence 1 0.1 3% 1 3.0 3%"


# soxArgsList returns a list of commands to feed sox.core.sox
def soxArgsList(cmd):
    cmd_arr = cmd.split(" ")
    cmd_arr.pop(0) # remove sox command
    return cmd_arr

# args = ['-d', '-t', 'wav', 'output.wav', 'trim', '0', '00:05']
args = soxArgsList(silence)
print(args)
sox.core.sox(args)
