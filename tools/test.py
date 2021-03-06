import sys
from subprocess import Popen, PIPE

def run_it(cmd):
    """ Run given commands with provided parameters """
    cmd = cmd.split(" ")
    print("Running [" + cmd[0] + "]...")
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stdout:
        print("\t with output: " + stdout.decode("utf-8"))
        return stdout.decode("utf-8")


if __name__ == "__main__":
    run_it("sox -d -b 16 output.wav channels 1 rate 16k silence 1 0.1 3% 1 3.0 3%")
    stt = run_it("deepspeech --model ../deepspeech/deepspeech-0.7.4-models.pbmm --scorer ../deepspeech/deepspeech-0.7.4-models.scorer --audio output.wav")
    run_it("say " + stt)
