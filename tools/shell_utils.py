import subprocess
import time


class Shell:
    def __init__(self, cmd, finish):
        self.cmd = cmd
        self.finish = finish
        self.ret_info = None

    def run_background(self):
        self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for i in range(6):  # 根据图数据库开启的经验来考虑的
            time.sleep(1)
            line = self.process.stdout.readline().decode()
            print(line)
            if self.finish in line:
                break

    def get_output(self):
        return self.process.stdout.readline().decode()


if __name__ == '__main__':
    keep = Shell('neo4j.bat console', 'Started')
    keep.run_background()
    print(keep.get_output())
