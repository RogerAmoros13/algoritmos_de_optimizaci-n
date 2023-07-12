import pygame
pygame.init()

HEIGHT, WIDTH = 600, 800
TOWER_POSITIONS = (150, 400, 650)

WHITE = (255, 255, 255)
GREY = (224, 224, 224)
BROWN = (101, 67, 33)
CIAN  = (0, 128, 255)
BLUE  = (0, 0, 153)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

MAX_N = 20

font = pygame.font.SysFont("Arial", 30)
font2 = pygame.font.SysFont("Arial", 24)

class HanoiTower:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Torre de Hanoi")
        self.clock = pygame.time.Clock()
        self.N = 5
        self.floors = self.get_floors()
        self.tower_pressed = False
        self.moves = 0
        self.moves_done = []
        self.init_stacks()
        self.opt_moves = 2**self.N - 1
    
    def init_stacks(self):
        self.stacks = {
            0: Stack(self.N, "A"),
            1: Stack(self.N, "B"),
            2: Stack(self.N, "C"),
        }
        self.stacks[0].fill_stack()
        self.solver = self.hanoi_solver()
        self.next_move()
        
    
    def factorial(self, n):
        if n == 1:
            return 1
        return n * self.factorial(n - 1)
    
    def get_floors(self):
        height = int(280 / self.N)
        if height > 60:
            height = 60
        step = 160 / self.N
        floors = []
        for i in range(self.N):
            floors.append(
                Floor(height, 200-i*step, i, i, 0)
            )
        return floors
    
    def is_inside_rect(self, rect, pos):
        if pos[0] > rect[0] and pos[0] < rect[1] and pos[1] > rect[2] and pos[1] < rect[3]:
            return True
        return False
    
    def is_finish(self):
        for floor in self.floors:
            if floor.tower != 2:
                return False
        return True

    def next_move(self):
        if not self.is_finish():
            self.better_move = next(self.solver)
            return True
        return False

    def run(self):
        running = True
        select_floor = False
        auto_solve = False
        loop = 0
        good = True
        finish = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.is_inside_rect((20, 120, 10, 38), pos):
                        self.reset()
                        continue
                    if self.is_inside_rect((20, 140, 46, 74), pos):
                        if good:
                            auto_solve = not auto_solve
                        continue
                    if self.is_inside_rect((150, 350, 42, 57), pos):
                        if not self.moves:
                            self.N = (pos[0] - 150) // 20 + 1
                            self.reset()
                        continue
                    if auto_solve:
                        continue
                    for item, x in enumerate(TOWER_POSITIONS):
                        if pos[0] + 125 > x:
                            tower_pressed = item
                    if select_floor:
                        if select_floor.tower == tower_pressed:
                            select_floor.update_state(selected=False)
                            select_floor = False
                        else:
                            position = self.get_position(
                                tower_pressed, select_floor.level
                            )
                            if position > -.5:
                                move = select_floor.tower, tower_pressed
                                self.moves_done.append(
                                    (select_floor.tower, tower_pressed)
                                )
                                select_floor.update_state(
                                    selected=False,
                                    tower=tower_pressed,
                                    position=position,
                                )
                                self.moves += 1
                                select_floor = False
                                if move == self.better_move:
                                    self.next_move()
                                else:
                                    good = False
                            else:
                                select_floor.update_state(selected=False)
                                select_floor = self.upper_floor(tower_pressed)
                                if select_floor:
                                    select_floor.update_state(selected=True)
                    else:
                        select_floor = self.upper_floor(tower_pressed)
                        if select_floor:
                            select_floor.update_state(selected=True)
            if auto_solve and not loop % 10 and not finish:
                self.auto_solve()
                loop = 0
            if self.is_finish():
                auto_solve = False
                self.reset(True)
            self.update()
            self.clock.tick(60)
            loop += 1
        
    def auto_solve(self):
        src = self.upper_floor(self.better_move[0])
        pos = self.get_position(self.better_move[1], src.level)
        src.update_state(tower=self.better_move[1], position=pos)
        auto = self.next_move()
        self.moves += 1
        return not auto
        
    def reset(self, soft=False):
        self.opt_moves = 2**self.N - 1
        if not soft:
            self.moves = 0
            self.floors = self.get_floors()
            self.init_stacks()
    
    def update(self):
        self.screen.fill(GREY)
        self.draw_base()
        self.draw_floors()
        self.draw_reset()
        self.draw_auto_solve()
        self.draw_moves()
        self.draw_level()
        pygame.display.update()
    
    def draw_floors(self):
        for floor in self.floors:
            floor.draw(self.screen)

    def draw_base(self):
        pygame.draw.rect(
            self.screen, BROWN, (10, 580, 780, 10)
        )
        for pos, stack in zip(TOWER_POSITIONS, self.stacks):
            pygame.draw.rect(
                self.screen, BROWN, (pos-5, 270, 10, 320)
            )
            name = self.stacks[stack].name
            if stack in self.better_move:
                text = font.render(name, True, GREEN)
            else:
                text = font.render(name, True, BLACK)
            self.screen.blit(text, (pos-10, 100))
    
    def upper_floor(self, tower):
        _up, _floor = -1, False
        for floor in self.floors:
            if floor.tower == tower:
                if floor.position > _up:
                    _floor = floor
        return _floor
    
    def get_position(self, tower, level):
        position = 0
        floor_list = [f for f in self.floors if f.tower == tower]
        if not floor_list:
            return 0
        for floor in floor_list:
            if floor.level < level:
                position += 1
        return position or -1
    
    def draw_reset(self):
        pygame.draw.rect(
            self.screen, WHITE, (20, 10, 100, 28), 0, 5
        )
        pygame.draw.rect(
            self.screen, BLACK, (18, 8, 104, 30), 2, 5
        )
        reset_text = font2.render("Reset", True, BLACK)
        self.screen.blit(reset_text, (38, 9))

    def draw_auto_solve(self):
        pygame.draw.rect(
            self.screen, WHITE, (20, 46, 120, 28), 0, 5
        )
        pygame.draw.rect(
            self.screen, BLACK, (18, 44, 124, 30), 2, 5
        )
        reset_text = font2.render("Auto Solve", True, BLACK)
        self.screen.blit(reset_text, (22, 46))

    def draw_moves(self):
        moves_text = font.render(
            "Movimientos hechos: {}".format(self.moves), True, BLACK
        )
        self.screen.blit(moves_text, (360, 10))
        opt_moves_text = font.render(
            "Movimientos mínimos: {}".format(self.opt_moves), True, BLACK
        )
        self.screen.blit(opt_moves_text, (360, 50))
    
    def draw_level(self):
        level = font.render(
            "Altura: {}".format(self.N), True, BLACK
        )
        self.screen.blit(level, (200, 10))
        x = (self.N - 1) * 20 + 160
        pygame.draw.rect(self.screen, BROWN, (150, 45, 200, 10), 0, 3)
        pygame.draw.circle(self.screen, BLACK, (x, 50), 12)
        pygame.draw.circle(self.screen, GREY, (x, 50), 7)
    
    def hanoi_solver(self):
        s, d, a = 0, 2, 1
        total = 2**self.N - 1
        if not self.N % 2:
            temp = d
            d = a
            a = temp
        for i in range(1, total + 1):
            if i % 3 == 1:
                yield self.do_move(s, d)
            elif i % 3 == 2:
                yield self.do_move(s, a)
            else:
                yield self.do_move(a, d)

    def do_move(self, src, dest):
        src_obj = self.stacks[src]
        dest_obj = self.stacks[dest]
        pole1 = src_obj.pop()
        pole2 = dest_obj.pop()
        if pole1 == -MAX_N:
            src_obj.push(pole2)
            return dest, src
        elif pole2 == -MAX_N:
            dest_obj.push(pole1)
            return src, dest
        elif pole1 > pole2:
            src_obj.push(pole1)
            src_obj.push(pole2)
            return dest, src
        else:
            dest_obj.push(pole2)
            dest_obj.push(pole1)
            return src, dest

class Stack:
    def __init__(self, n, name):
        self.n = n
        self.top = -1
        self.name = name
        self.array = [False]*n
    
    def is_full(self):
        return self.top == (self.n - 1)
    
    def is_empty(self):
        return self.top == -1
    
    def push(self, item):
        if self.is_full():
            return
        self.top += 1
        self.array[self.top] = item
    
    def pop(self):
        if self.is_empty():
            return -MAX_N
        top = self.top
        self.top -= 1
        return self.array[top]
    
    def fill_stack(self):
        for i in range(self.n, 0, -1):
            self.push(i)
    
class Floor:
    def __init__(self, height, width, level, position, tower=0):
        self.height = height
        self.width = width
        self.position = position
        self.level = level
        self.tower = tower
        self.selected = False
        self.rect_int = pygame.Rect(0, 0, width-8, height-8)
        self.rect_ext = pygame.Rect(0, 0, width, height)
        center = self.get_center()
        self.rect_int.center = center
        self.rect_ext.center = center
    
    def get_center(self):
        center = (
            TOWER_POSITIONS[self.tower], 
            HEIGHT-20-self.position*self.height - self.height / 2
        )
        if self.selected:
            center = center[0], 200
        return center
    
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect_ext, 0, 8)
        pygame.draw.rect(screen, CIAN, self.rect_int, 0, 8)
    
    def update_state(self, selected=False, tower=None, position=None):
        self.selected = selected
        self.tower = tower if tower or tower == 0 else self.tower
        self.position = position if position or position == 0 else self.position
        center = self.get_center()
        self.rect_ext.center = center
        self.rect_int.center = center


if __name__ == "__main__":
    hanoi = HanoiTower()
    hanoi.run()