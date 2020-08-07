import sys
from subprocess import Popen, PIPE

def run_it(cmd):
    """ Run given commands with provided parameters """
    process = Popen(cmd.split(" "), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stdout:
        print(stdout)
        return stdout


if __name__ == "__main__":
    run_it("sox -d -b 16 output.wav channels 1 rate 16k silence 1 0.1 3% 1 3.0 3%")
    run_it("deepspeech --model ../deepspeech/deepspeech-0.7.4-models.pbmm --scorer ../deepspeech/deepspeech-0.7.4-models.scorer --audio output.wav")
