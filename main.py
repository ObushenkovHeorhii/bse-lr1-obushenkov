import tkinter as tk
import random
import os

# --- КОНСТАНТИ ГРИ / GAME CONSTANTS ---
GAME_WIDTH = 600
GAME_HEIGHT = 600
INITIAL_SPEED = 120  # Швидкість у мілісекундах (менше = швидше)
MIN_SPEED = 50
SPACE_SIZE = 25      # Розмір однієї клітинки (повинен ділити GAME_WIDTH/GAME_HEIGHT)
GRID_ROWS = GAME_HEIGHT // SPACE_SIZE
GRID_COLS = GAME_WIDTH // SPACE_SIZE

# Кольорова палітра (Neon Dark)
BACKGROUND_COLOR = "#0D0E15"
GRID_COLOR = "#161925"
FOOD_COLOR = "#FF2E93"
FOOD_GLOW = "#FF2E93"
SNAKE_HEAD_COLOR = "#00FF88"
# Градієнт для тіла змійки
SNAKE_BODY_GRADIENT = [
    "#00FF88", "#05F390", "#0AE798", "#0FDAA0", 
    "#14CFA8", "#19C3B0", "#1EB7B8", "#23ABC0", 
    "#289FC8", "#2D93D0", "#3287D8", "#377BE0"
]
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#00FF88"
UI_PANEL_COLOR = "#161925"

HIGH_SCORE_FILE = "highscore.txt"

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Neon Snake Game")
        self.root.resizable(False, False)
        
        # Центрування вікна на екрані
        self.center_window(GAME_WIDTH, GAME_HEIGHT + 60)
        
        # Ініціалізація змінних стану
        self.score = 0
        self.high_score = self.load_high_score()
        self.direction = "right"
        self.next_direction = "right"
        self.speed = INITIAL_SPEED
        
        self.game_over = False
        self.paused = False
        self.game_started = False
        
        self.snake_coords = []
        self.snake_parts = []
        self.food_coord = None
        self.food_item = None
        self.food_glow_item = None
        
        self.setup_ui()
        self.bind_keys()
        
        # Показати головне меню при старті
        self.show_start_screen()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2) - 40
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        # Панель рахунку (Score Panel)
        self.score_frame = tk.Frame(self.root, bg=UI_PANEL_COLOR, height=60)
        self.score_frame.pack(fill=tk.X, side=tk.TOP)
        self.score_frame.pack_propagate(False)
        
        # Рахунок
        self.score_label = tk.Label(
            self.score_frame, 
            text="РАХУНОК: 0", 
            font=("Courier New", 16, "bold"), 
            bg=UI_PANEL_COLOR, 
            fg=ACCENT_COLOR
        )
        self.score_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Рекорд
        self.high_score_label = tk.Label(
            self.score_frame, 
            text=f"РЕКОРД: {self.high_score}", 
            font=("Courier New", 16, "bold"), 
            bg=UI_PANEL_COLOR, 
            fg="#FFC837"
        )
        self.high_score_label.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Ігрове поле (Canvas)
        self.canvas = tk.Canvas(
            self.root, 
            bg=BACKGROUND_COLOR, 
            height=GAME_HEIGHT, 
            width=GAME_WIDTH, 
            highlightthickness=0
        )
        self.canvas.pack()

    def bind_keys(self):
        # Керування рухом
        self.root.bind("<Up>", lambda event: self.change_direction("up"))
        self.root.bind("<Down>", lambda event: self.change_direction("down"))
        self.root.bind("<Left>", lambda event: self.change_direction("left"))
        self.root.bind("<Right>", lambda event: self.change_direction("right"))
        
        # Альтернативне керування (WASD)
        self.root.bind("<w>", lambda event: self.change_direction("up"))
        self.root.bind("<s>", lambda event: self.change_direction("down"))
        self.root.bind("<a>", lambda event: self.change_direction("left"))
        self.root.bind("<d>", lambda event: self.change_direction("right"))
        self.root.bind("<W>", lambda event: self.change_direction("up"))
        self.root.bind("<S>", lambda event: self.change_direction("down"))
        self.root.bind("<A>", lambda event: self.change_direction("left"))
        self.root.bind("<D>", lambda event: self.change_direction("right"))
        
        # Інші гарячі клавіші
        self.root.bind("<space>", self.toggle_pause)
        self.root.bind("<Return>", self.start_game_trigger)
        self.root.bind("<r>", self.restart_game_trigger)
        self.root.bind("<R>", self.restart_game_trigger)
        self.root.bind("<Escape>", lambda event: self.root.destroy())

    def draw_grid(self):
        self.canvas.delete("grid")
        # Горизонтальні лінії
        for y in range(0, GAME_HEIGHT, SPACE_SIZE):
            self.canvas.create_line(0, y, GAME_WIDTH, y, fill=GRID_COLOR, tags="grid")
        # Вертикальні лінії
        for x in range(0, GAME_WIDTH, SPACE_SIZE):
            self.canvas.create_line(x, 0, x, GAME_HEIGHT, fill=GRID_COLOR, tags="grid")

    def show_start_screen(self):
        self.canvas.delete("all")
        self.draw_grid()
        
        # Заголовок гри з ефектом світіння
        self.canvas.create_text(
            GAME_WIDTH // 2 + 2, GAME_HEIGHT // 3 + 2,
            text="NEON SNAKE",
            font=("Courier New", 42, "bold"),
            fill="#121212",
            tags="start_ui"
        )
        self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 3,
            text="NEON SNAKE",
            font=("Courier New", 42, "bold"),
            fill=ACCENT_COLOR,
            tags="start_ui"
        )
        
        # Підзаголовок
        self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2 - 10,
            text="Натисніть ENTER для старту",
            font=("Helvetica", 16, "bold"),
            fill=TEXT_COLOR,
            tags="start_ui"
        )
        
        # Керування
        instructions = (
            "КЕРУВАННЯ:\n"
            "• Стрілочки або WASD - рух змійки\n"
            "• Space (Пробіл) - пауза\n"
            "• R - перезапуск після програшу\n"
            "• Esc - вийти з гри"
        )
        self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT * 2 // 3 + 20,
            text=instructions,
            font=("Helvetica", 12),
            fill="#8B90A0",
            justify=tk.CENTER,
            tags="start_ui"
        )

    def start_game_trigger(self, event=None):
        if not self.game_started and not self.game_over:
            self.game_started = True
            self.canvas.delete("start_ui")
            self.start_game()

    def restart_game_trigger(self, event=None):
        if self.game_over:
            self.canvas.delete("game_over_ui")
            self.start_game()

    def start_game(self):
        # Очищення та скидання параметрів гри
        self.canvas.delete("all")
        self.draw_grid()
        
        self.score = 0
        self.speed = INITIAL_SPEED
        self.direction = "right"
        self.next_direction = "right"
        self.game_over = False
        self.paused = False
        self.game_started = True
        
        self.score_label.config(text="РАХУНОК: 0")
        
        # Початкове тіло змійки (3 сегменти в центрі)
        start_x = (GRID_COLS // 2) * SPACE_SIZE
        start_y = (GRID_ROWS // 2) * SPACE_SIZE
        
        self.snake_coords = [
            [start_x, start_y],
            [start_x - SPACE_SIZE, start_y],
            [start_x - (2 * SPACE_SIZE), start_y]
        ]
        
        self.snake_parts = []
        self.draw_snake()
        
        # Створення їжі
        self.spawn_food()
        
        # Запуск ігрового циклу
        self.next_turn()

    def draw_snake(self):
        # Видалити старі елементи змійки з canvas
        for part in self.snake_parts:
            self.canvas.delete(part)
        self.snake_parts.clear()
        
        # Малюємо кожен сегмент змійки
        for i, (x, y) in enumerate(self.snake_coords):
            # Визначаємо колір для градієнту
            if i == 0:
                color = SNAKE_HEAD_COLOR
            else:
                color_idx = min(i - 1, len(SNAKE_BODY_GRADIENT) - 1)
                color = SNAKE_BODY_GRADIENT[color_idx]
            
            # Малювання тіла змійки у вигляді заокруглених кругів з відступами
            padding = 2
            part = self.canvas.create_oval(
                x + padding, y + padding,
                x + SPACE_SIZE - padding, y + SPACE_SIZE - padding,
                fill=color,
                outline="",
                tags="snake"
            )
            self.snake_parts.append(part)
            
            # Додаємо очі для голови змійки
            if i == 0:
                self.draw_eyes(x, y)

    def draw_eyes(self, head_x, head_y):
        # Очистити старі очі
        self.canvas.delete("eyes")
        
        # Розмір очей та зсув залежно від напрямку руху
        eye_size = 4
        
        if self.direction == "up":
            # Ліве око
            self.canvas.create_oval(
                head_x + 6, head_y + 6,
                head_x + 6 + eye_size, head_y + 6 + eye_size,
                fill="#000000", outline="", tags="eyes"
            )
            # Праве око
            self.canvas.create_oval(
                head_x + SPACE_SIZE - 6 - eye_size, head_y + 6,
                head_x + SPACE_SIZE - 6, head_y + 6 + eye_size,
                fill="#000000", outline="", tags="eyes"
            )
        elif self.direction == "down":
            self.canvas.create_oval(
                head_x + 6, head_y + SPACE_SIZE - 6 - eye_size,
                head_x + 6 + eye_size, head_y + SPACE_SIZE - 6,
                fill="#000000", outline="", tags="eyes"
            )
            self.canvas.create_oval(
                head_x + SPACE_SIZE - 6 - eye_size, head_y + SPACE_SIZE - 6 - eye_size,
                head_x + SPACE_SIZE - 6, head_y + SPACE_SIZE - 6,
                fill="#000000", outline="", tags="eyes"
            )
        elif self.direction == "left":
            self.canvas.create_oval(
                head_x + 6, head_y + 6,
                head_x + 6 + eye_size, head_y + 6 + eye_size,
                fill="#000000", outline="", tags="eyes"
            )
            self.canvas.create_oval(
                head_x + 6, head_y + SPACE_SIZE - 6 - eye_size,
                head_x + 6 + eye_size, head_y + SPACE_SIZE - 6,
                fill="#000000", outline="", tags="eyes"
            )
        elif self.direction == "right":
            self.canvas.create_oval(
                head_x + SPACE_SIZE - 6 - eye_size, head_y + 6,
                head_x + SPACE_SIZE - 6, head_y + 6 + eye_size,
                fill="#000000", outline="", tags="eyes"
            )
            self.canvas.create_oval(
                head_x + SPACE_SIZE - 6 - eye_size, head_y + SPACE_SIZE - 6 - eye_size,
                head_x + SPACE_SIZE - 6, head_y + SPACE_SIZE - 6,
                fill="#000000", outline="", tags="eyes"
            )

    def change_direction(self, new_dir):
        # Запобігаємо розвороту змійки на 180 градусів
        if new_dir == "left" and self.direction != "right":
            self.next_direction = new_dir
        elif new_dir == "right" and self.direction != "left":
            self.next_direction = new_dir
        elif new_dir == "up" and self.direction != "down":
            self.next_direction = new_dir
        elif new_dir == "down" and self.direction != "up":
            self.next_direction = new_dir

    def spawn_food(self):
        # Видалити стару їжу
        if self.food_item:
            self.canvas.delete(self.food_item)
        if self.food_glow_item:
            self.canvas.delete(self.food_glow_item)
            
        while True:
            # Вибір випадкової позиції на сітці
            x = random.randint(0, GRID_COLS - 1) * SPACE_SIZE
            y = random.randint(0, GRID_ROWS - 1) * SPACE_SIZE
            
            # Перевіряємо, чи їжа не з'явилася на тілі змійки
            if [x, y] not in self.snake_coords:
                self.food_coord = [x, y]
                break
        
        # Малюємо ефект світіння їжі
        glow_padding = -2
        self.food_glow_item = self.canvas.create_oval(
            x + glow_padding, y + glow_padding,
            x + SPACE_SIZE - glow_padding, y + SPACE_SIZE - glow_padding,
            fill="",
            outline=FOOD_GLOW,
            width=2,
            tags="food"
        )
        
        # Малюємо основний елемент їжі (кружечок з бліком)
        pad = 4
        self.food_item = self.canvas.create_oval(
            x + pad, y + pad,
            x + SPACE_SIZE - pad, y + SPACE_SIZE - pad,
            fill=FOOD_COLOR,
            outline="",
            tags="food"
        )
        
        # Малюємо крихітний листочок (зелений штрих) для краси
        self.canvas.create_line(
            x + SPACE_SIZE // 2, y + pad,
            x + SPACE_SIZE // 2 + 3, y + pad - 2,
            fill="#00FF88",
            width=2,
            tags="food"
        )

    def next_turn(self):
        if self.game_over or self.paused:
            return
            
        self.direction = self.next_direction
        
        # Визначаємо нову координату голови
        head_x, head_y = self.snake_coords[0]
        
        if self.direction == "up":
            head_y -= SPACE_SIZE
        elif self.direction == "down":
            head_y += SPACE_SIZE
        elif self.direction == "left":
            head_x -= SPACE_SIZE
        elif self.direction == "right":
            head_x += SPACE_SIZE
            
        # Додаємо нову голову змійки на початок списку
        self.snake_coords.insert(0, [head_x, head_y])
        
        # Перевірка на зіткнення з їжею
        if head_x == self.food_coord[0] and head_y == self.food_coord[1]:
            # Збільшення рахунку
            self.score += 1
            self.score_label.config(text=f"РАХУНОК: {self.score}")
            
            # Збільшення швидкості (кожні 5 очок)
            if self.score % 5 == 0 and self.speed > MIN_SPEED:
                self.speed -= 8
                
            # Оновлюємо рекорд, якщо потрібно
            if self.score > self.high_score:
                self.high_score = self.score
                self.high_score_label.config(text=f"РЕКОРД: {self.high_score}")
                self.save_high_score(self.high_score)
                
            # Створюємо нову їжу, хвіст змійки не видаляємо
            self.spawn_food()
        else:
            # Змійка не з'їла їжу: видаляємо останній сегмент (хвіст)
            self.snake_coords.pop()
            
        # Оновлення графічного представлення змійки
        self.draw_snake()
        
        # Перевірка на зіткнення зі стінами або собою
        if self.check_collisions():
            self.handle_game_over()
        else:
            # Плануємо наступний крок через вказаний інтервал часу
            self.root.after(self.speed, self.next_turn)

    def check_collisions(self):
        head_x, head_y = self.snake_coords[0]
        
        # Зіткнення з межами поля
        if head_x < 0 or head_x >= GAME_WIDTH or head_y < 0 or head_y >= GAME_HEIGHT:
            return True
            
        # Зіткнення з власним тілом
        for body_part in self.snake_coords[1:]:
            if head_x == body_part[0] and head_y == body_part[1]:
                return True
                
        return False

    def toggle_pause(self, event=None):
        if not self.game_started or self.game_over:
            return
            
        self.paused = not self.paused
        
        if self.paused:
            # Показати напис паузи
            self.canvas.create_text(
                GAME_WIDTH // 2, GAME_HEIGHT // 2,
                text="ПАУЗА",
                font=("Courier New", 36, "bold"),
                fill="#FFC837",
                tags="pause_ui"
            )
            self.canvas.create_text(
                GAME_WIDTH // 2, GAME_HEIGHT // 2 + 40,
                text="Натисніть SPACE для продовження",
                font=("Helvetica", 14),
                fill=TEXT_COLOR,
                tags="pause_ui"
            )
        else:
            # Видалити напис паузи та відновити цикл
            self.canvas.delete("pause_ui")
            self.next_turn()

    def handle_game_over(self):
        self.game_over = True
        self.game_started = False
        
        # Ефект червоного затемнення
        self.canvas.create_rectangle(
            0, 0, GAME_WIDTH, GAME_HEIGHT,
            fill="#120c0e", stipple="gray50",
            tags="game_over_ui"
        )
        
        # Написи Game Over
        self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2 - 50,
            text="ГРА ЗАКІНЧЕНА",
            font=("Courier New", 32, "bold"),
            fill="#FF2E93",
            tags="game_over_ui"
        )
        
        self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2 + 10,
            text=f"Ваш результат: {self.score}",
            font=("Helvetica", 18, "bold"),
            fill=TEXT_COLOR,
            tags="game_over_ui"
        )
        
        self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2 + 70,
            text="Натисніть R для початку спочатку",
            font=("Helvetica", 14),
            fill=ACCENT_COLOR,
            tags="game_over_ui"
        )

    # --- ЗБЕРЕЖЕННЯ / ЗАВАНТАЖЕННЯ РЕКОРДУ ---
    def load_high_score(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    return int(f.read().strip())
            except Exception:
                return 0
        return 0

    def save_high_score(self, score):
        try:
            with open(HIGH_SCORE_FILE, "w") as f:
                f.write(str(score))
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
