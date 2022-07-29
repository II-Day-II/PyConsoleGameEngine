from console_game_engine import CGE
import random

class App(CGE):
    def __init__(self):
        super().__init__()
        self.birdpos = 0
        self.birdvel = 0
        self.birdacc = 0
        self.gravity = 100
        self.levelpos = 0
        self.sectionwidth = 0
        self.sections = []
        self.hascollided = False
        self.reset = False
        self.attemptcount = 0
        self.flaps = 0
        self.high_flaps = 0

    def on_user_create(self):
        self.sections = [0, 0, 0, 0]
        self.reset = True
        self.sectionwidth = self.screen_width / float(len(self.sections) - 1)
        return True

    def on_user_update(self, delta_time):
        if self.reset:
            self.hascollided = False
            self.reset = False
            self.sections = [0,0,0,0]
            self.birdacc = 0
            self.birdvel = 0
            self.birdpos = self.screen_height / 2
            self.flaps = 0
            self.attemptcount += 1
        if self.hascollided:
            input()
        else:
            # get input
            if True and self.birdvel >= self.gravity / 10:
                self.birdacc = 0
                self.birdvel = -self.gravity / 4
                self.flaps += 1
                if self.flaps > self.high_flaps:
                    self.high_flaps = self.flaps
            else:
                self.birdacc += self.gravity * delta_time
            if self.birdacc > self.gravity:
                self.birdacc = self.gravity
            self.birdvel += self.birdacc * delta_time
            self.birdpos += self.birdvel * delta_time
            self.levelpos += 14 * delta_time
            if self.levelpos > self.sectionwidth:
                self.levelpos -= self.sectionwidth
                self.sections.pop(0)
                a = random.randint(0, self.screen_height - 20)
                self.sections.append(a if a > 10 else 0)
            self.fill(0, 0, self.screen_width, self.screen_height, " ") 

            sect = 0
            for s in self.sections:
                if s != 0:
                    self.fill(int(sect * self.sectionwidth + 10 - self.levelpos), int(self.screen_height - s),
                    int(sect * self.sectionwidth + 15 - self.levelpos), int(self.screen_height))
                    self.fill(int(sect * self.sectionwidth + 10 - self.levelpos), 0,
                    int(sect * self.sectionwidth + 15 - self.levelpos), int(self.screen_height - s - 15))
                sect += 1
            birdx = self.screen_width / 3
            self.draw_string(int(birdx), int(self.birdpos), "vv" if self.birdvel > 0 else "^^")
            self.draw_string(1, 1, f"attempt: {self.attemptcount} score: {self.flaps} highscore: {self.high_flaps}")

        return True

def main():
    tst = App()
    tst.construct_console(80, 48, 16, 16)
    tst.start()

if __name__ == "__main__":
    main()