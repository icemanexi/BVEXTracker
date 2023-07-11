from time import time

class Log:
    def __init__(self, prefix, log_file):
        assert type(prefix) == str
        self.pf = prefix
        self.lf = log_file

    def __call__(self, arg):
        assert type(arg) == str

        print(time(), self.pf, arg)
        try:
            self.lf.write("\n" + str(round(time(), 2)) + " " + self.pf + " " + arg)
        except Exception as e:
            print(e)


if __name__ == "__main__":

    with open("/home/fissellab/BVEXTracker/Sensors/test.log", "a") as fil:
        log = Log("ME:", fil)

        log("asd")
