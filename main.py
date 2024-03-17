import pygame as pg
import numpy as np

class Fourc():
    def __init__(self):
        self.WIDTH = 500
        self.HEIGHT = 500
        self.create_game()
        self.puzzle = np.zeros((6,7), dtype=np.ubyte)
        self.emps = np.zeros(7, dtype=np.ubyte)
        self.cell_size = self.WIDTH / 7
        self.color_GR = (40,10,60)
        self.many_used = 0
        self.end = False
        self.tie = False
        self.color_yellow = (214,221,0)
        self.color_white = (255,255,221)
        self.color_blue = (112,122,183)
        self.color_red = (175,26,11)

    def create_game(self):
        pg.init()
        self. screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        self.font = pg.font.Font('FreeSansBold.ttf', 32)
        pg.display.set_caption("Four Connect")

    def draw(self):
        self.screen.fill(self.color_yellow)

        for x in range(len(self.puzzle)):
            for y in range(len(self.puzzle[x])):
                color = self.color_white
                if self.puzzle[5-x][y] == 1:
                    color = self.color_red
                elif self.puzzle[5-x][y] == 2:
                    color = self.color_blue
                pg.draw.circle(self.screen, color, ((y+.5) * self.cell_size, (x+.5) * self.cell_size), self.cell_size /2)

        self.text_render()
        pg.display.update()

    def text_render(self):
        if self.is_blue:
            status = "Blue"
        else:
            status = "Red"
        if self.end:
            status += " wins!"
        elif self.tie:
            status = "TIE!"
        else:
            status += "'s turn"

        text = self.font.render(status, True, self.color_GR)
        textRect = text.get_rect()
        textRect.center = 100 , 450
        self.screen.blit(text, textRect)

    def calc_score_sec(self, section:np.ndarray):
        zero, neg, pos = 0, 0, 0
        for i in range(4):
            if section[i] == 0:
                zero += 1
            elif (section[i] == -1) == self.is_blue:
                neg += 1
            else:
                pos += 1
        if pos == 4:
            return 3
        if zero == 1:
            if pos == 3:
                return 2
            if neg == 3:
                return -2
        elif zero == 2:
            if pos == 2:
                return 1
            if neg == 2:
                return -1
        return 0

    def cal_score(self):
        score = 0 

        for i in range(self.puzzle.shape[0]):
            for j in range(self.puzzle.shape[1] - 3):
                score += self.calc_score_sec(self.puzzle[i,j: j + 4])

        for i in range(self.puzzle.shape[1]):
            for j in range(self.puzzle.shape[0] - 3):
                score += self.calc_score_sec(self.puzzle[j: j + 4,i])

        for i in range(self.puzzle.shape[0] - 3):
            for j in range(self.puzzle.shape[1] - 3):
                section = np.array([self.puzzle[i+d,j+d] for d in range(4)])
                score += self.calc_score_sec(section)

        for i in range(3, self.puzzle.shape[0]):
            for j in range(self.puzzle.shape[1] - 3):
                section = np.array([self.puzzle[i-d,j+d] for d in range(4)])
                score += self.calc_score_sec(section)

        return score

    def check_win(self, cell_x, cell_y):
        pco = self.puzzle[cell_x][cell_y] 
        for i in range(max(0, cell_x-3), min(cell_x+4, self.puzzle.shape[0])):
            if i+3 < self.puzzle.shape[0] and np.all(self.puzzle[i:i+4, cell_y] == pco):
                return True

        for j in range(max(0, cell_y-3), min(cell_y+4, self.puzzle.shape[1])):
            if j+3 < self.puzzle.shape[1] and np.all(self.puzzle[cell_x, j:j+4] == pco):
                return True

        for i, j in zip(range(cell_x, min(cell_x+4, self.puzzle.shape[0])), range(cell_y, max(0, cell_y-4) -1, -1)):
            if i-3 >= 0 and j+3 < self.puzzle.shape[1] :
                for t, d in zip(range(i, i-4, -1), range(j, j+4)):
                    if self.puzzle[t, d] != pco:
                        break
                else:
                    return True

        for i, j in zip(range(cell_x, min(cell_x+4, self.puzzle.shape[0])), range(cell_y, min(cell_y+4, self.puzzle.shape[1]))):
            if i-3 >= 0 and j-3 >= 0 :
                for t, d in zip(range(i-3, i+1), range(j-3, j+1)):
                    if self.puzzle[t, d] != pco:
                        break
                else:
                    return True

        return False

    def check_tie(self):
        return self.many_used == self.puzzle.shape[0] * self.puzzle.shape[1]

    def action_xy(self, cell_x, cell_y):
        self.puzzle[cell_x , cell_y] = self.is_blue + 1
        self.many_used += 1
        self.emps[cell_y] += 1
        self.is_blue = not self.is_blue 
        if self.check_win(cell_x, cell_y):
            self.end = True
            return 3
        if self.check_tie():
            self.tie = True
            return 2
        return 1

    def action_y(self, cell_y):
        cell_x = self.emps[cell_y]
        if cell_x > 5 or cell_x<0:
            return 0
        return self.action_xy(cell_x, cell_y)

    def get_y_mouse(self, mouse_pos):
        return np.floor(mouse_pos[0]/self.cell_size).astype(np.ubyte)
    
    def undo_action_y(self, cell_y):
        self.emps[cell_y] -= 1
        self.puzzle[self.emps[cell_y], cell_y] = 0
        self.many_used -= 1
        self.end = False
        self.tie = False
        self.is_blue = not self.is_blue

class PlayersManager():
    def __init__(self, fourc:Fourc, is_AI):
        self.fourc = fourc
        self.is_AI = is_AI

    def play(self):
        self.fourc.is_blue = False
        while True:
            if self.process_game() == False:
                return
            self.fourc.draw()

    def process_game(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            if self.fourc.tie or self.fourc.end:
                continue
            if not self.is_AI[self.fourc.is_blue]:
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    mouse_cell_y = self.fourc.get_y_mouse(mouse_pos)
                    self.fourc.action_y(mouse_cell_y)
            else:
                score,cell_y = self.minimax(True, 5, -5, 5)
                self.fourc.action_y(cell_y)
            if self.fourc.end:
                self.fourc.is_blue = not self.fourc.is_blue
        return True

    def minimax(self, is_max, max_depth, alpha, beta):
        if max_depth == 0:
            return self.fourc.cal_score(), None

        best_score, cbest_score = (is_max*-8) +4, 0
        for column in range(self.fourc.puzzle.shape[1]):
            ans_act = self.fourc.action_y(column)
            if ans_act: 
                if ans_act == 3:
                    score = (is_max*8) - 4
                elif ans_act == 2:
                    score = 0
                else:
                    score,_ = self.minimax(not is_max, max_depth - 1, alpha, beta)
                self.fourc.undo_action_y(column)
                if (is_max and best_score <= score) or (not is_max and best_score >= score):
                    best_score, cbest_score = score, column 
                if is_max:
                    alpha = max(alpha, best_score)
                else:
                    beta = min(beta, best_score)

                if beta <= alpha:
                    break
        return best_score, cbest_score

fourc = Fourc()
playersManager = PlayersManager(fourc, [0, 1])
playersManager.play()