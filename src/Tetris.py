import pygame
import random
import math
from pathlib import Path

# Lấy đường dẫn tới thư mục chứa file Python hiện tại
current_directory = Path(__file__).parent

# Tạo đường dẫn tới file Rank.txt
file_path = current_directory / "Rank.txt"
"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

pygame.font.init()

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per blo ck
block_size = 30
difficulty = "Easy"  # Mặc định là "Normal"
fall_speed = 0.75       # Tốc độ rơi mặc định
paused = False  # Trạng thái tạm dừng mặc định là False
player_name = ""
destroy_count = 0  # Số lần phá hủy đã sử dụng
max_destroy = 3    # Số lần phá hủy tối đa

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

score = 0
background_path = Path(__file__).parent / "AnhNen1.png"  # Đường dẫn tới ảnh nền
try:
    background = pygame.image.load(str(background_path))
    background = pygame.transform.scale(background, (s_width, s_height))  # Điều chỉnh kích thước ảnh nền
except pygame.error as e:
    print(f"Lỗi khi tải ảnh nền: {e}")
    background = None  # Nếu không có ảnh nền, trò chơi sẽ tiếp tục mà không có nền
# Khởi tạo hệ thống âm thanh
pygame.mixer.init()

# Đường dẫn tới file nhạc
music_path = Path(__file__).parent / "NhacNen.mp3"

# Phát nhạc nền
try:
    pygame.mixer.music.load(str(music_path))  # Tải nhạc
    pygame.mixer.music.play(-1)  # Phát nhạc lặp vô hạn
    pygame.mixer.music.set_volume(0.5)  # Thiết lập âm lượng (từ 0.0 tới 1.0)
except pygame.error as e:
    print(f"Lỗi khi phát nhạc: {e}")

# Tải âm thanh nút bấm
try:
    button_click_sound = pygame.mixer.Sound(str(Path(__file__).parent / "NhacBam.wav"))
    button_click_sound.set_volume(0.5)  # Thiết lập âm lượng (0.0 - 1.0)
except pygame.error as e:
    print(f"Lỗi khi tải âm thanh: {e}")
    button_click_sound = None  # Nếu không tải được, đặt giá trị là None

# SHAPE FORMATS

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape


class Piece(object):
    rows = 20  # y
    columns = 10  # x

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # number from 0-3

def set_difficulty(level):
    global difficulty, fall_speed
    difficulty = level
    if level == "Easy":
        fall_speed = 0.75  # Rơi chậm
    elif level == "Normal":
        fall_speed = 0.5  # Rơi trung bình
    elif level == "Hard":
        fall_speed = 0.1  # Rơi nhanh
        

     

def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid



def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False

    return True


def check_lost(locked):
    for pos in locked:
        x, y = pos
        if y < 1:  # Kiểm tra nếu có khối nào nằm ở hàng đầu tiên
            return True
    return False

def get_shape():
    global shapes, shape_colors
    # Khởi tạo khối ở giữa hàng trên cùng (y = 0)
    return Piece(5, 0, random.choice(shapes))

def draw_text_middle(text, size, color, surface, offset_y=0):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width / 2 - label.get_width() / 2,
                         top_left_y + play_height / 2 - label.get_height() / 2 + offset_y))


def draw_grid(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*30), (sx + play_width, sy + i * 30))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (sx + j * 30, sy), (sx + j * 30, sy + play_height))  # vertical lines

def draw_exit_button(surface):
    font = pygame.font.SysFont('comicsans', 30, bold=True)
    label_text = 'Exit'
    label = font.render(label_text, 1, (0, 0, 0))  # Chữ màu đen
    exit_x, exit_y = s_width - 120, 70  # Vị trí góc phải trên cùng (dưới nút Pause)
    button_width, button_height = 100, 40

    mouse_pos = pygame.mouse.get_pos()
    is_hovered = button_hover(exit_x, exit_y, button_width, button_height, mouse_pos)

    # Thay đổi màu sắc nút khi hover
    button_color = (255, 120, 120) if is_hovered else (255, 70, 70)
    border_color = (255, 255, 255) if is_hovered else (200, 200, 200)

    # Vẽ hình chữ nhật bo góc
    pygame.draw.rect(surface, button_color, (exit_x, exit_y, button_width, button_height), border_radius=10)
    pygame.draw.rect(surface, border_color, (exit_x, exit_y, button_width, button_height), 2, border_radius=10)

    # Hiển thị chữ trên nút
    label_x = exit_x + (button_width - label.get_width()) // 2
    label_y = exit_y + (button_height - label.get_height()) // 2
    surface.blit(label, (label_x, label_y))

    return exit_x, exit_y, button_width, button_height


def clear_rows(grid, locked):
    # need to see if row is clear the shift every other row above down one
    global score

    inc = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            # add positions to remove from locked
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

        score += inc * 10


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*30, sy + i*30, 30, 30), 0)

    surface.blit(label, (sx + 10, sy- 30))

def draw_score(surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50  # Vị trí bảng điểm bên trái lưới
    sy = top_left_y + play_height / 2 + 100
    surface.blit(label, (sx, sy))

def toggle_pause():
    global paused
    paused = not paused


def draw_pause_message(surface):
    if paused:
        draw_text_middle("Paused", 40, (255, 255, 255), surface)
        pygame.display.update() 


def draw_pause_button(surface):
    font = pygame.font.SysFont('comicsans', 30, bold=True)
    label_text = 'Resume' if paused else 'Pause'
    label = font.render(label_text, 1, (0, 0, 0))  # Chữ màu đen
    pause_x, pause_y = s_width - 120, 20  # Vị trí góc phải trên cùng
    button_width, button_height = 100, 40

    mouse_pos = pygame.mouse.get_pos()
    is_hovered = button_hover(pause_x, pause_y, button_width, button_height, mouse_pos)

    # Thay đổi màu sắc nút khi hover
    button_color = (186, 255, 201) if is_hovered else (150, 235, 170)
    border_color = (255, 255, 255) if is_hovered else (200, 200, 200)

    # Vẽ hình chữ nhật bo góc
    pygame.draw.rect(surface, button_color, (pause_x, pause_y, button_width, button_height), border_radius=10)
    pygame.draw.rect(surface, border_color, (pause_x, pause_y, button_width, button_height), 2, border_radius=10)

    # Hiển thị chữ trên nút
    label_x = pause_x + (button_width - label.get_width()) // 2
    label_y = pause_y + (button_height - label.get_height()) // 2
    surface.blit(label, (label_x, label_y))

    return pause_x, pause_y, button_width, button_height


def draw_window(surface, background):
    # Hiển thị ảnh nền nếu có
    if background:
        surface.blit(background, (0, 0))
    else:
        surface.fill((0, 0, 0))  # Nếu không có ảnh nền, sử dụng nền đen

    # Hiển thị tiêu đề Tetris
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', 1, (255, 255, 255))
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # Hiển thị các khối trong lưới
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j * 30, top_left_y + i * 30, 30, 30), 0)

    # Vẽ lưới và viền
    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

    # Hiển thị bảng điểm và số lần phá hủy
    draw_score(surface)
    draw_destroy_count(surface)


def button_hover(x, y, width, height, mouse_pos):
    mouse_x, mouse_y = mouse_pos
    return x <= mouse_x <= x + width and y <= mouse_y <= y + height


def draw_button(surface, label, x, y, width, height, mouse_pos):
    color = (255, 255, 255)  # Màu mặc định
    if button_hover(x, y, width, height, mouse_pos):
        color = (200, 200, 200)  # Màu khi hover
    pygame.draw.rect(surface, color, (x, y, width, height))
    surface.blit(label, (x + 10, y + 10))

def enter_player_name():
    global player_name
    run = True
    input_box_width = 300  # Chiều rộng khung nhập
    input_box_height = 50  # Chiều cao khung nhập
    input_box = pygame.Rect(s_width // 2 - input_box_width // 2, s_height // 2 - input_box_height // 2, input_box_width, input_box_height)

    font = pygame.font.SysFont('comicsans', 40)
    player_name = ""

    # Tải ảnh nền (nếu có)
    background_path = Path(__file__).parent / "AnhNen1.png"
    try:
        background = pygame.image.load(str(background_path))
        background = pygame.transform.scale(background, (s_width, s_height))  # Thay đổi kích thước ảnh phù hợp
    except pygame.error as e:
        print(f"Lỗi khi tải hình ảnh: {e}")
        background = None

    while run:
        # Hiển thị ảnh nền nếu tồn tại
        if background:
            win.blit(background, (0, 0))
        else:
            win.fill((255, 255, 255))  # Làm sạch màn hình (nền trắng nếu không có ảnh nền)

        # Hiển thị tiêu đề với màu trắng
        label = font.render("Enter your name:", True, (255, 255, 255))  # Chữ màu trắng
        win.blit(label, (s_width // 2 - label.get_width() // 2, input_box.y - 60))

        # Vẽ nền và viền khung nhập
        pygame.draw.rect(win, (255, 255, 255), input_box)  # Nền khung màu trắng
        pygame.draw.rect(win, (0, 0, 0), input_box, 2)  # Viền khung màu đen

        # Hiển thị văn bản bên trong khung nhập
        text_surface = font.render(player_name, True, (0, 0, 0))  # Chữ màu đen
        text_x = input_box.x + 10  # Thụt vào từ lề trái
        text_y = input_box.y + (input_box.height - text_surface.get_height()) // 2  # Căn giữa dọc
        win.blit(text_surface, (text_x, text_y))

        pygame.display.flip()

        # Lắng nghe sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Nhấn Enter để xác nhận tên
                    if player_name.strip():  # Chỉ chấp nhận nếu có tên
                        return player_name
                elif event.key == pygame.K_BACKSPACE:  # Xóa ký tự cuối cùng
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 13:  # Giới hạn tên tối đa 13 ký tự
                        player_name += event.unicode  # Thêm ký tự vào tên


def destroy_blocks(locked_positions):
    # Xóa ngẫu nhiên 3-5 khối từ các vị trí đã khóa
    num_blocks_to_destroy = random.randint(3, 5)  # Số lượng khối phá hủy ngẫu nhiên
    positions_to_destroy = random.sample(list(locked_positions.keys()), min(num_blocks_to_destroy, len(locked_positions)))

    # Xóa các khối khỏi vị trí đã khóa
    for pos in positions_to_destroy:
        del locked_positions[pos]

    # Cập nhật lại lưới
    global grid
    grid = create_grid(locked_positions)

def destroy_blocks_with_effect_at_mouse(surface, locked_positions, mouse_pos):
    global grid, destroy_count  # Cập nhật biến toàn cục

    # Kiểm tra số lần phá hủy còn lại
    if destroy_count >= max_destroy:
        print("Bạn đã sử dụng hết số lần phá hủy!")
        return

    # Xác định vị trí chuột trong lưới
    mouse_x, mouse_y = mouse_pos
    grid_x = (mouse_x - top_left_x) // block_size
    grid_y = (mouse_y - top_left_y) // block_size

    # Kiểm tra vị trí chuột có nằm trong phạm vi lưới không
    if grid_x < 0 or grid_x >= 10 or grid_y < 0 or grid_y >= 20:
        print("Vị trí chuột ngoài phạm vi lưới!")
        return

    # Tạo vùng phá hủy 3x3 xung quanh vị trí chuột
    positions_to_destroy = []
    for dx in range(-1, 2):  # -1, 0, 1
        for dy in range(-1, 2):  # -1, 0, 1
            x, y = grid_x + dx, grid_y + dy
            if (x, y) in locked_positions:  # Chỉ thêm vị trí hợp lệ
                positions_to_destroy.append((x, y))

    # Hiệu ứng phá hủy
    for pos in positions_to_destroy:
        x, y = pos
        color = locked_positions[pos]

        # Hiệu ứng nhấp nháy
        for _ in range(3):  # Lặp hiệu ứng nhấp nháy 3 lần
            pygame.draw.rect(surface, color,
                             (top_left_x + x * block_size, top_left_y + y * block_size, block_size, block_size))
            pygame.display.update()
            pygame.time.delay(100)
            pygame.draw.rect(surface, (0, 0, 0),
                             (top_left_x + x * block_size, top_left_y + y * block_size, block_size, block_size))
            pygame.display.update()
            pygame.time.delay(100)

        # Xóa vị trí khỏi danh sách bị khóa
        del locked_positions[pos]

    # Cập nhật lại lưới
    grid = create_grid(locked_positions)

    # Tăng số lần phá hủy đã sử dụng
    destroy_count += 1
    print(f"Số lần phá hủy đã sử dụng: {destroy_count}/{max_destroy}")

def draw_destroy_count(surface):
    font = pygame.font.SysFont('comicsans', 30)

    # Hiển thị số lần phá hủy còn lại
    destroy_left_label = font.render(f"Destroy: {max_destroy - destroy_count}", True, (255, 255, 255))
    sx = top_left_x - 235  # Đặt ở bên trái lưới (giảm x để chuyển sang trái)
    sy = top_left_y + 200  # Đặt dưới phần "TETRIS" một khoảng hợp lý
    surface.blit(destroy_left_label, (sx, sy))

    # Hiển thị số lần phá hủy tối đa
    max_destroy_label = font.render(f"Max Destroy: {max_destroy}", True, (255, 255, 255))
    surface.blit(max_destroy_label, (sx, sy + 40))  # Dịch xuống 40 pixel để không bị đè


                    
def fireworks_effect_pro(surface, num_fireworks=10, duration=2000):
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration:
        surface.fill((0, 0, 0))  # Làm mới màn hình
        for _ in range(num_fireworks):
            x = random.randint(0, s_width)
            y = random.randint(0, s_height // 2)
            color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)])
            radius = random.randint(5, 15)
            pygame.draw.circle(surface, color, (x, y), radius)
        pygame.display.update()
        pygame.time.delay(100)  # Tạo độ mượt cho hiệu ứng

def fireworks_effect(surface, num_fireworks=10, duration=3000):
    particles = []  # Danh sách các hạt pháo hoa
    start_time = pygame.time.get_ticks()

    while pygame.time.get_ticks() - start_time < duration:
        # Tạo pháo hoa mới
        if len(particles) < num_fireworks:
            x = random.randint(100, s_width - 100)
            y = random.randint(100, s_height // 2)
            color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)])
            for _ in range(50):  # Số lượng hạt mỗi pháo hoa
                angle = random.uniform(0, 2 * math.pi)  # Góc ngẫu nhiên
                speed = random.uniform(2, 5)  # Tốc độ ngẫu nhiên
                particles.append({
                    "x": x,
                    "y": y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "radius": random.randint(2, 4),  # Kích thước hạt
                    "color": color,
                    "lifetime": random.randint(30, 60)  # Tuổi thọ hạt
                })

        # Vẽ các hạt pháo hoa
        surface.fill((0, 0, 0))  # Làm sạch màn hình
        for particle in particles[:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["lifetime"] -= 1
            pygame.draw.circle(surface, particle["color"], (int(particle["x"]), int(particle["y"])), particle["radius"])

            # Loại bỏ hạt nếu hết tuổi thọ
            if particle["lifetime"] <= 0:
                particles.remove(particle)

        pygame.display.update()
        pygame.time.delay(30)  # Tạo độ mượt mà

                    
def settings_menu():
    try:
        # Tải hình ảnh
        background_path = Path(__file__).parent / "AnhNen1.png"  # Đường dẫn tới ảnh nền
        try:
            background = pygame.image.load(str(background_path))
            background = pygame.transform.scale(background, (s_width, s_height))  # Thay đổi kích thước ảnh cho vừa màn hình
        except pygame.error as e:
            print(f"Lỗi khi tải hình ảnh: {e}")
            return

        run = True
        while run:
            # Hiển thị hình nền
            win.blit(background, (0, 0))

            # Tạo font và nhãn tiêu đề
            font_title = pygame.font.SysFont('comicsans', 60)
            title_label = font_title.render('Select Difficulty', 1, (255, 255, 255))

            # Tạo nhãn hiển thị độ khó hiện tại
            font_current = pygame.font.SysFont('comicsans', 40)
            current_label = font_current.render(f'Current: {difficulty}', 1, (255, 255, 255))

            # Khoảng cách dọc giữa các thành phần
            spacing = 100

            # Vị trí tiêu đề
            title_y = 50
            title_x = s_width // 2 - title_label.get_width() // 2

            # Vị trí các nhãn
            current_x = s_width // 2 - current_label.get_width() // 2
            current_y = title_y + title_label.get_height() + 20  # Cách tiêu đề một chút

            # Kích thước nút
            button_width, button_height = 200, 60
            button_x = s_width // 2 - button_width // 2

            easy_y = current_y + spacing
            normal_y = easy_y + spacing
            hard_y = normal_y + spacing

            # Tọa độ và kích thước các nút
            buttons = [
                ("Easy", easy_y, "Easy", (0, 128, 0)),  # Màu chữ cho Easy
                ("Normal", normal_y, "Normal", (255, 165, 0)),  # Màu chữ cho Normal
                ("Hard", hard_y, "Hard", (255, 0, 0)),  # Màu chữ cho Hard
            ]

            for label, y_pos, value, text_color in buttons:
                # Kiểm tra trạng thái hover
                mouse_pos = pygame.mouse.get_pos()
                is_hovered = button_hover(button_x, y_pos, button_width, button_height, mouse_pos)

                # Xác định màu nút
                if difficulty == value:
                    button_color = (173, 216, 230)  # Màu xanh matcha cho nút đang chọn (186, 255, 201)
                elif is_hovered:
                    button_color = (173, 216, 230)  # Màu xanh nhạt khi hover
                else:
                    button_color = (255, 255, 255)  # Màu trắng mặc định

                # Màu viền
                border_color = (0, 0, 0)

                # Vẽ nút
                pygame.draw.rect(win, button_color, (button_x, y_pos, button_width, button_height), border_radius=10)
                pygame.draw.rect(win, border_color, (button_x, y_pos, button_width, button_height), 3, border_radius=10)

                # Hiển thị nhãn trên nút (giữ màu chữ cố định)
                font_menu = pygame.font.SysFont('comicsans', 50)
                label_text = font_menu.render(label, 1, text_color)  # Màu chữ không thay đổi
                win.blit(label_text, (button_x + (button_width - label_text.get_width()) // 2,
                                      y_pos + (button_height - label_text.get_height()) // 2))

            # Hiển thị tiêu đề và độ khó hiện tại
            win.blit(title_label, (title_x, title_y))
            win.blit(current_label, (current_x, current_y))

            pygame.display.update()

            # Lắng nghe sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # Kiểm tra click vào các nút
                    for label, y_pos, value, _ in buttons:
                        if button_hover(button_x, y_pos, button_width, button_height, mouse_pos):
                            if button_click_sound:
                                button_click_sound.play()  # Phát âm thanh khi nhấn nút
                            set_difficulty(value)
                            run = False
    except Exception as e:
        print("Lỗi trong settings_menu:", e)

                    
def display_rankings():
    try:
        # Kiểm tra file hình ảnh
        background_path = Path(__file__).parent / "AnhNen1.png"
        if not background_path.exists():
            print("File hình ảnh không tồn tại:", background_path)
            return
        background = pygame.image.load(str(background_path))
        background = pygame.transform.scale(background, (s_width, s_height))

        # Đọc file Rank.txt
        file_path = Path(__file__).parent / "Rank.txt"
        if not file_path.exists():
            file_path.touch()  # Tạo file nếu chưa có
            print("Rank.txt đã được tạo. Hiện không có dữ liệu.")
            win.fill((0, 0, 0))
            draw_text_middle("Rank.txt đã được tạo. Hiện không có dữ liệu.", 40, (255, 255, 255), win)
            pygame.display.update()
            pygame.time.delay(2000)
            return

        with file_path.open(mode="r") as file:
            lines = file.readlines()
            rankings = []
            for line in lines:
                if line.strip():
                    try:
                        name, score = line.strip().split(",")
                        rankings.append((name, int(score)))
                    except ValueError:
                        print(f"Dữ liệu không hợp lệ trong Rank.txt: {line.strip()}")
                        continue

            rankings = sorted(rankings, key=lambda x: x[1], reverse=True)

        # Nếu không có dữ liệu
        if not rankings:
            win.fill((0, 0, 0))
            draw_text_middle("Không có dữ liệu xếp hạng.", 40, (255, 255, 255), win)
            pygame.display.update()
            pygame.time.delay(2000)
            return

        # Bắt đầu vòng lặp sự kiện
        waiting = True
        while waiting:
            # Hiển thị ảnh nền
            win.blit(background, (0, 0))

            # Hiển thị tiêu đề
            font_title = pygame.font.SysFont('comicsans', 60)
            title_label = font_title.render('Rankings', 1, (255, 255, 255))
            win.blit(title_label, (s_width // 2 - title_label.get_width() // 2, 50))

            # Hiển thị top 5 người chơi
            font = pygame.font.SysFont('comicsans', 40)
            y_offset = 150  # Khoảng cách từ trên cùng xuống
            for i, (name, score) in enumerate(rankings[:5]):  # Hiển thị top 5
                rank_label = font.render(f"#{i + 1}: {name} - {score}", 1, (255, 255, 255))
                win.blit(rank_label, (s_width // 2 - rank_label.get_width() // 2, y_offset))
                y_offset += 50  # Khoảng cách giữa các hàng

            # Hiển thị nút "Back"
            button_width, button_height = 200, 60
            button_x = s_width // 2 - button_width // 2
            button_y = s_height - 150

            # Lấy vị trí chuột
            mouse_pos = pygame.mouse.get_pos()

            # Kiểm tra trạng thái hover
            is_hovered = button_hover(button_x, button_y, button_width, button_height, mouse_pos)

            # Thay đổi màu nút dựa trên trạng thái hover
            button_color = (255, 255, 255) if not is_hovered else (173, 216, 230)  # Màu nền
            border_color = (0, 0, 0) if is_hovered else (0, 0, 0)  # Màu viền

            pygame.draw.rect(win, button_color, (button_x, button_y, button_width, button_height))
            pygame.draw.rect(win, border_color, (button_x, button_y, button_width, button_height), 3)

            back_label = font.render("Back", 1, (0, 0, 0))
            win.blit(back_label, (button_x + (button_width - back_label.get_width()) // 2,
                                  button_y + (button_height - back_label.get_height()) // 2))

            # Cập nhật màn hình
            pygame.display.update()

            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_hover(button_x, button_y, button_width, button_height, mouse_pos):
                        if button_click_sound:
                            button_click_sound.play()  # Phát âm thanh khi nhấn nút
                        waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False

    except Exception as e:
        print("Lỗi trong display_rankings:", e)


def save_score_and_get_rank(player_name, score):
    file_path = Path(__file__).parent / "Rank.txt"

    # Lưu điểm của người chơi vào file
    try:
        with file_path.open(mode="a") as file:
            file.write(f"{player_name},{score}\n")  # Ghi tên và điểm vào file
    except Exception as e:
        print(f"Lỗi khi lưu điểm: {e}")
        return None, None

    # Đọc file và xác định hạng
    try:
        with file_path.open(mode="r") as file:
            lines = file.readlines()
            rankings = [line.strip().split(",") for line in lines if line.strip()]  # Phân tách tên và điểm
            rankings = sorted(rankings, key=lambda x: int(x[1]), reverse=True)  # Sắp xếp theo điểm giảm dần

        # Tìm hạng của người chơi
        for rank, (name, score_str) in enumerate(rankings, start=1):
            if name == player_name and int(score_str) == score:
                return rank, rankings  # Chỉ trả về hạng và bảng xếp hạng
    except Exception as e:
        print(f"Lỗi khi xác định hạng: {e}")
        return None, None

    return None, None



def main():
    global grid, paused, fall_speed, destroy_count, score
    destroy_count = 0
    score = 0
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.unpause()


    locked_positions = {}  # Lưu các vị trí đã khóa của khối
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # Xử lý các sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Nút chuột trái
                    mouse_pos = pygame.mouse.get_pos()  # Lấy vị trí chuột
                    destroy_blocks_with_effect_at_mouse(win, locked_positions, mouse_pos)  # Gọi hàm phá hủy


            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Xử lý nút Exit
                exit_x, exit_y, exit_width, exit_height = draw_exit_button(win)
                if button_hover(exit_x, exit_y, exit_width, exit_height, mouse_pos):
                    run = False  # Thoát trò chơi

                # Xử lý nút Pause
                pause_x, pause_y, pause_width, pause_height = draw_pause_button(win)
                if button_hover(pause_x, pause_y, pause_width, pause_height, mouse_pos):
                    toggle_pause()  # Chuyển trạng thái tạm dừng

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Phím 'P' để tạm dừng
                    toggle_pause()

                if not paused:  # Chỉ xử lý phím khi không bị tạm dừng
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1

                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1

                    elif event.key == pygame.K_UP:
                        current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                        if not valid_space(current_piece, grid):
                            current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

                    elif event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1

                    elif event.key == pygame.K_SPACE:
                        while valid_space(current_piece, grid):
                            current_piece.y += 1
                        current_piece.y -= 1  # Điều chỉnh vị trí

        if paused:
            draw_pause_message(win)
            pygame.mixer.music.pause()  # Dừng nhạc khi Pause
            continue
        else:
            pygame.mixer.music.unpause()  # Tiếp tục nhạc khi Resume
    
        # Logic rơi khối
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        shape_pos = convert_shape_format(current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        # Khi khối chạm đáy hoặc khối khác
        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # Kiểm tra nếu người chơi thua
            if check_lost(locked_positions):
                run = False  # Kết thúc trò chơi

            # Xóa các hàng đầy
            clear_rows(grid, locked_positions)

        draw_window(win, background)
        draw_next_shape(next_piece, win)
        draw_pause_button(win)
        draw_exit_button(win)
        pygame.display.update()

    # Hiển thị thông báo thua
    draw_text_middle("You Lost", 40, (255, 255, 255), win)
    pygame.display.update()
    pygame.time.delay(2000)

    # Lưu điểm và công bố hạng
    rank, rankings = save_score_and_get_rank(player_name, score)

    # Hiển thị hiệu ứng và thông báo nếu lọt top 5
    if rank is not None:
        # Hiển thị ảnh nền trước
        if background:  # Kiểm tra nếu ảnh nền đã được tải
            win.blit(background, (0, 0))
        else:
            win.fill((0, 0, 0))  # Nếu không có ảnh nền, sử dụng nền đen

        if rank == 1:
            fireworks_effect_pro(win, num_fireworks=20, duration=3000)  # Pháo hoa nhiều hơn cho top 1
            draw_text_middle("Champion!", 60, (255, 255, 0), win)
        elif rank <= 5:
            fireworks_effect(win, num_fireworks=10, duration=2000)  # Pháo hoa cho top 5
            draw_text_middle("Top 5!", 40, (255, 255, 0), win)

    # Cập nhật màn hình hiển thị
    pygame.display.update()
    pygame.time.delay(2000)

    # Hiển thị điểm và hạng của người chơi
    if background:  # Kiểm tra nếu ảnh nền đã được tải
        win.blit(background, (0, 0))  # Hiển thị ảnh nền
    else:
        win.fill((0, 0, 0))  # Nếu không có ảnh nền, dùng nền đen
        
    font = pygame.font.SysFont('comicsans', 40)
    if rank is not None:
        message = f"Your Score: {score}\nYour Rank: #{rank}"
    else:
        message = f"Your Score: {score}\nUnable to determine your rank."

    # Hiển thị thông báo kết quả
    for i, line in enumerate(message.split("\n")):
        label = font.render(line, 1, (255, 255, 255))
        win.blit(label, (s_width // 2 - label.get_width() // 2, s_height // 2 - 50 + i * 50))

    pygame.display.update()
    pygame.time.delay(3000)

    # Hiển thị bảng xếp hạng nếu có
    if rankings:
        if background:
            win.blit(background, (0, 0))  # Hiển thị ảnh nền
        else:
            win.fill((0, 0, 0))  # Nếu không có ảnh nền, dùng nền đen

        title = font.render("Top Rankings:", 1, (255, 255, 255))
        win.blit(title, (s_width // 2 - title.get_width() // 2, 50))

        for i, (name, score_str) in enumerate(rankings[:10], start=1):  # Hiển thị top 10
            label = font.render(f"{i}. {name} - {score_str}", 1, (255, 255, 255))
            win.blit(label, (s_width // 2 - label.get_width() // 2, 100 + i * 40))

        pygame.display.update()
        pygame.time.delay(5000)

    # Quay lại menu chính
    main_menu()


def main_menu():
    # Nếu nhạc đang tạm dừng (pause), tiếp tục phát
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.unpause()
    # Tải ảnh nền
    background_path = Path(__file__).parent / "AnhNen8.png"  # Đảm bảo file AnhNen.png nằm cùng thư mục với script
    background = pygame.image.load(str(background_path))
    background = pygame.transform.scale(background, (s_width, s_height))  # Thay đổi kích thước ảnh cho vừa màn hình

    run = True
    while run:
        win.blit(background, (0, 0))  # Vẽ ảnh nền lên màn hình

        # Tạo các nút menu với hiệu ứng viền
        font_menu = pygame.font.SysFont('comicsans', 50, bold=True)
        button_spacing = 80  # Khoảng cách giữa các nút
        start_y = 300  # Điểm bắt đầu cho các nút
        button_width = 350  # Chiều rộng của nút (tăng lên so với 300)
        button_height = 60  # Chiều cao của nút (tăng lên so với 50)

        # Danh sách nút (text, vị trí Y)
        buttons = [
            ("Play", start_y),
            ("Level", start_y + button_spacing),
            ("Rankings", start_y + button_spacing * 2),
            ("Quit", start_y + button_spacing * 3),
        ]

        mouse_pos = pygame.mouse.get_pos()  # Vị trí chuột

        for button_text, y_pos in buttons:
            # Kiểm tra nếu chuột đang hover nút
            is_hovered = button_hover(s_width // 2 - button_width // 2, y_pos, button_width, button_height, mouse_pos)

            button_color = (255, 255, 255) if not is_hovered else (173, 216, 230)  # Màu nền
            border_color = (0, 0, 0) if is_hovered else (0, 0, 0)  # Màu viền
            
            # Vẽ hình chữ nhật cho nút (có viền)
            pygame.draw.rect(win, button_color, (s_width // 2 - button_width // 2, y_pos, button_width, button_height))  # Nền nút
            pygame.draw.rect(win, border_color, (s_width // 2 - button_width // 2, y_pos, button_width, button_height), 3)  # Viền nút

            # Vẽ text chính giữa ô
            label = font_menu.render(button_text, 1, (0, 0, 0) if not is_hovered else (0, 0, 0))  # Màu text
            label_x = s_width // 2 - label.get_width() // 2  # Căn giữa theo chiều ngang
            label_y = y_pos + (button_height - label.get_height()) // 2  # Căn giữa theo chiều dọc
            win.blit(label, (label_x, label_y))

        pygame.display.update()

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()############################################
                run = False
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_hover(s_width // 2 - button_width // 2, start_y, button_width, button_height, mouse_pos):
                    if button_click_sound:
                        button_click_sound.play()  # Phát âm thanh khi nhấn nút
                    enter_player_name()  # Yêu cầu nhập tên
                    main()  # Bắt đầu trò chơi
                elif button_hover(s_width // 2 - button_width // 2, start_y + button_spacing, button_width, button_height, mouse_pos):
                    if button_click_sound:
                        button_click_sound.play()  # Phát âm thanh khi nhấn nút
                    settings_menu()  # Chuyển tới menu cài đặt
                elif button_hover(s_width // 2 - button_width // 2, start_y + button_spacing * 2, button_width, button_height, mouse_pos):
                    if button_click_sound:
                        button_click_sound.play()  # Phát âm thanh khi nhấn nút
                    display_rankings()  # Hiển thị bảng xếp hạng
                elif button_hover(s_width // 2 - button_width // 2, start_y + button_spacing * 3, button_width, button_height, mouse_pos):
                    if button_click_sound:
                        button_click_sound.play()  # Phát âm thanh khi nhấn nút
                    run = False  # Thoát game


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')
main_menu()  # start game