import pygame
import random
import sys
from collections import deque

# 初始化pygame
pygame.init()

# 游戏配置（匹配5×5面板要求）
CELL_SIZE = 80  # 单元格大小
GRID_ROWS = 5
GRID_COLS = 5
SCREEN_WIDTH = CELL_SIZE * GRID_COLS + 200  # 右侧预留排行榜区域
SCREEN_HEIGHT = CELL_SIZE * GRID_ROWS
FPS = 30

# 颜色定义
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# 屏幕初始化
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption
clock = pygame.time.Clock()
font = pygame.font.SysFont('SimHei', 40)
small_font = pygame.font.SysFont('SimHei', 25)


class TouchTenGame:
    def __init__(self, player_count=2, game_mode="time"):
        self.player_count = player_count  # 2-4人
        self.game_mode = game_mode  # time（计时冲分）/ score（积分排名）
        self.scores = [0] * player_count  # 玩家得分
        self.current_player = 0  # 当前回合玩家
        self.selected_cells = []  # 选中的单元格坐标 [(row, col), ...]
        self.grid = self.init_grid()  # 5×5游戏面板
        self.time_left = 60  # 计时模式剩余时间（秒）
        self.start_time = pygame.time.get_ticks()  # 游戏开始时间
        self.difficulty_level = 1  # 初始难度
        self.spawn_interval = 1000  # 数字刷新间隔（毫秒），难度越高间隔越短
        self.last_spawn_time = pygame.time.get_ticks()

    # 初始化5×5网格，随机生成1-9数字（空白格用0表示）
    def init_grid(self):
        grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if random.random() > 0.3:  # 70%概率生成数字
                    grid[row][col] = random.randint(1, 9)
        return grid

    # 检查选中的单元格是否相邻（横、竖、斜向）
    def is_adjacent(self, cells):
        if len(cells) < 2:
            return True  # 单个单元格默认相邻
        # 检查所有单元格是否互相连通（相邻）
        visited = set()
        queue = deque([cells[0]])
        visited.add(cells[0])
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1), (0, 1),
                      (1, -1), (1, 0), (1, 1)]  # 8个方向

        while queue:
            r, c = queue.popleft()
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if (nr, nc) in cells and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        return len(visited) == len(cells)

    # 检查选中数字总和是否为10
    def check_sum_ten(self, cells):
        total = sum(self.grid[r][c] for r, c in cells)
        return total == 10

    # 消除选中数字并填充新数字
    def eliminate_and_refill(self):
        # 计算得分：消除个数越多、用时越短，分值越高
        eliminate_count = len(self.selected_cells)
        time_used = (pygame.time.get_ticks() - self.last_spawn_time) / 1000  # 秒
        score = int(eliminate_count * 100 / max(time_used, 1))  # 用时越短分数越高
        self.scores[self.current_player] += score

        # 消除选中单元格（设为0）
        for r, c in self.selected_cells:
            self.grid[r][c] = 0

        # 填充新数字（梅森旋转算法优化随机性，random模块默认采用）
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if self.grid[row][col] == 0:
                    self.grid[row][col] = random.randint(1, 9)

        # 切换玩家（休闲模式）或保持当前玩家（对战模式）
        if self.game_mode == "score":  # 积分模式（轮流操作）
            self.current_player = (self.current_player + 1) % self.player_count

        # 动态调整难度：得分越快，刷新间隔越短
        self.adjust_difficulty()
        self.selected_cells.clear()
        self.last_spawn_time = pygame.time.get_ticks()

    # 动态难度调整（基于得分速度）
    def adjust_difficulty(self):
        avg_score = sum(self.scores) / len(self.scores) if self.scores else 0
        self.difficulty_level = min(5, max(1, int(avg_score / 500) + 1))  # 1-5级
        self.spawn_interval = 1000 - (self.difficulty_level - 1) * 200  # 难度越高，刷新越快

    # 绘制游戏面板
    def draw_grid(self):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                # 绘制单元格边框
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, GRAY, rect, 2)
                # 绘制数字
                num = self.grid[row][col]
                if num != 0:
                    text = font.render(str(num), True, BLACK)
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
                # 绘制选中状态
                if (row, col) in self.selected_cells:
                    pygame.draw.rect(screen, YELLOW, rect, 3)

        # 绘制得分与信息面板

    def draw_info_panel(self):
        # 绘制玩家得分
        panel_x = GRID_COLS * CELL_SIZE + 20
        y_offset = 50
        for i in range(self.player_count):
            color = BLUE if i == self.current_player else BLACK
            score_text = font.render(f"玩家{i + 1}：{self.scores[i]}分", True, color)
            screen.blit(score_text, (panel_x, y_offset + i * 60))

        # 绘制游戏模式与时间
        # 修正第147行：使用Python正确的三元表达式语法
        mode_name = "计时冲分" if self.game_mode == 'time' else '积分排名'
        mode_text = small_font.render(f"模式：{mode_name}", True, BLACK)
        screen.blit(mode_text, (panel_x, y_offset + self.player_count * 60 + 30))

        if self.game_mode == "time":
            time_text = small_font.render(f"剩余时间：{max(0, self.time_left)}秒", True, RED)
            screen.blit(time_text, (panel_x, y_offset + self.player_count * 60 + 60))

        # 绘制难度等级
        diff_text = small_font.render(f"难度：{self.difficulty_level}级", True, GREEN)
        screen.blit(diff_text, (panel_x, y_offset + self.player_count * 60 + 90))

    # 更新游戏状态
    def update(self):
        # 计时模式更新时间
        if self.game_mode == "time":
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
            self.time_left = 60 - int(elapsed)
            if self.time_left <= 0:
                return False  # 游戏结束

        # 检查是否需要刷新数字（动态难度控制）
        if pygame.time.get_ticks() - self.last_spawn_time > self.spawn_interval:
            self.refill_random_cells()
            self.last_spawn_time = pygame.time.get_ticks()

        return True  # 游戏继续

    # 随机填充空白格（补充新数字）
    def refill_random_cells(self):
        for _ in range(self.difficulty_level):  # 难度越高，填充越多
            empty_cells = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if self.grid[r][c] == 0]
            if empty_cells:
                r, c = random.choice(empty_cells)
                self.grid[r][c] = random.randint(1, 9)

    # 处理鼠标点击事件
    def handle_click(self, pos):
        x, y = pos
        if x >= GRID_COLS * CELL_SIZE:
            return  # 点击右侧信息面板，忽略
        col = x // CELL_SIZE
        row = y // CELL_SIZE
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            cell = (row, col)
            if cell in self.selected_cells:
                self.selected_cells.remove(cell)  # 取消选中
            else:
                self.selected_cells.append(cell)  # 新增选中

            # 检查是否满足碰十条件
            if len(self.selected_cells) >= 2 and self.is_adjacent(self.selected_cells):
                if self.check_sum_ten(self.selected_cells):
                    self.eliminate_and_refill()
            elif len(self.selected_cells) > 5:
                self.selected_cells.pop(0)  # 最多选中5个单元格


# 游戏开始界面
def game_start_screen():
    player_buttons = [
        (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2, "2人"),
        (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2, "3人"),
        (SCREEN_WIDTH // 2 + 40, SCREEN_HEIGHT // 2, "4人")
    ]

    mode_buttons = [
        (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 90, "计时冲分"),
        (SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 90, "积分排名")
    ]

    selected_player = None
    selected_mode = None

    # 等待玩家选择
    while True:
        screen.fill(WHITE)
        title = font.render("碰十游戏", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(title, title_rect)

        # 选择玩家人数
        player_text = small_font.render("选择玩家人数（2-4）：", True, BLACK)
        screen.blit(player_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))

        # 选择游戏模式
        mode_text = small_font.render("选择游戏模式：", True, BLACK)
        screen.blit(mode_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 60))

        # 绘制玩家按钮，选中则高亮
        for idx, (x, y, text) in enumerate(player_buttons):
            rect = pygame.Rect(x, y, 50, 40)
            color = GREEN if selected_player == idx + 2 else GRAY
            pygame.draw.rect(screen, color, rect)
            text_surf = small_font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

        # 绘制模式按钮，选中则高亮
        for mode_idx, (x, y, text) in enumerate(mode_buttons):
            rect = pygame.Rect(x, y, 80, 40)
            color = GREEN if selected_mode == ("time" if mode_idx == 0 else "score") else GRAY
            pygame.draw.rect(screen, color, rect)
            text_surf = small_font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                # 检测玩家人数选择（允许单独点击）
                for idx, (bx, by, text) in enumerate(player_buttons):
                    if bx <= x <= bx + 50 and by <= y <= by + 40:
                        selected_player = idx + 2
                        break
                # 检测游戏模式选择（允许单独点击）
                for mode_idx, (mx, my, mtext) in enumerate(mode_buttons):
                    if mx <= x <= mx + 80 and my <= y <= my + 40:
                        selected_mode = "time" if mode_idx == 0 else "score"
                        break

                # 如果两项都已选，则返回选择
                if selected_player and selected_mode:
                    return selected_player, selected_mode


# 游戏结束界面
def game_over_screen(game):
    screen.fill(WHITE)
    title = font.render("游戏结束", True, RED)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(title, title_rect)

    # 显示排名
    rank_text = small_font.render("最终排名：", True, BLACK)
    screen.blit(rank_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 30))

    # 按得分排序
    players = [(i + 1, game.scores[i]) for i in range(game.player_count)]
    players.sort(key=lambda x: x[1], reverse=True)

    y_offset = 0
    for rank, (player_num, score) in enumerate(players, 1):
        color = YELLOW if rank == 1 else BLACK
        rank_text = font.render(f"{rank}名：玩家{player_num}（{score}分）", True, color)
        screen.blit(rank_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + y_offset))
        y_offset += 50

    # 重新开始按钮
    restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + y_offset + 30, 120, 40)
    pygame.draw.rect(screen, GREEN, restart_rect)
    restart_text = small_font.render("重新开始", True, WHITE)
    restart_text_rect = restart_text.get_rect(center=restart_rect.center)
    screen.blit(restart_text, restart_text_rect)

    pygame.display.flip()

    # 等待玩家操作
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                # 判断鼠标是否在重启按钮的矩形范围内
                if restart_rect.collidepoint(x, y):
                    main()  # 重新开始游戏


# 主函数
def main():
    # 开始界面选择参数
    player_count, game_mode = game_start_screen()
    # 初始化游戏
    game = TouchTenGame(player_count=player_count, game_mode=game_mode)

    running = True
    while running:
        screen.fill(WHITE)

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(pygame.mouse.get_pos())

        # 更新游戏状态
        if not game.update():
            running = False  # 游戏结束

        # 绘制界面
        game.draw_grid()
        game.draw_info_panel()
        pygame.display.flip()
        clock.tick(FPS)

    # 游戏结束界面
    game_over_screen(game)


if __name__ == "__main__":
    main()

