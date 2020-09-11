import sys
import time
from subprocess import Popen, PIPE

deepspeech_dir="/User/michael/code/deepspeech"

def run_it(cmd):
    ''' Run given commands with provided parameters '''
    process = Popen(cmd.split(" "), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stdout:
        print(stdout)
        return stdout
    if stderr:
        print(stderr)

def get_user_voice(timestamp):
    t = timestamp
    print("Say your command... ")
    cmd = f'sox -q -d -b 16 output-{t}.wav channels 1 rate 16k silence 1 0.1 3% 1 3.0 3%'
    run_it(cmd)

def wav_to_text(timestamp):
    t = timestamp
    print("...converting to text")
    cmd = f'deepspeech --model {deepspeech_dir}/deepspeech-0.7.4-models.pbmm --scorer {deepspeech_dir}/deepspeech-0.7.4-models.scorer --audio /Users/michael/code/vcrud/tools/output-{t}.wav'
    run_it(cmd)

def get_timestamp():
    time_stamp = time.strftime("%Y%m%d-%H%M%S")
    return time_stamp 
 

if __name__ == "__main__":
    t = get_timestamp()
    # run_it("sox -d -b 16 output.wav channels 1 rate 16k silence 1 0.1 3% 1 3.0 3%")
    # run_it("deepspeech --model ../deepspeech/deepspeech-0.7.4-models.pbmm --scorer ../deepspeech/deepspeech-0.7.4-models.scorer --audio output.wav")
    get_user_voice(t)
    wav_to_text(t) 