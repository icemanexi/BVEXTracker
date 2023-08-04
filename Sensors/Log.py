from time import time

class Log:
    def __init__(self, prefix, log_file):
        assert type(prefix) == str
        self.pf = prefix
        self.lf = log_file

    def __call__(self, arg):
        assert type(arg) == str

        print(round(time(), 2), self.pf, arg)
        try:
            self.lf.write(str(round(time(), 2)) + " " + self.pf + " " + arg + "\n")
        except Exception as e:
            print(e)


if __name__ == "__main__":

    fil = open("/home/fissellab/BVEXTracker/Logs/sysLog", "a")
    log = Log("ME:", fil)
    log2 = Log("test:", fil)
    
    log("asd\n")
    log2("dsa\n")
        
