import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import game_logic
import questions
import json
import os
import pygame

# Ініціалізуємо pygame mixer
pygame.mixer.init()
pygame.mixer.music.set_endevent(pygame.USEREVENT)

# Глобальні змінні для відстеження стану
used_questions = []
current_question_number = 1
correct_answers_count = 0
current_prize_money = 1000
current_music = "hello.mp3"

is_50_50_used = False
is_phone_a_friend_used = False
is_ask_the_audience_used = False
after_id = None

# Глобальні словники для іконок і кнопок
lifeline_icons = {}
lifeline_buttons = {}
money_icon = None

# Глобальні змінні для анімації GIF
gif_frames = []
gif_label = None
gif_index = 0
gif_delay = 0
animation_job = None  # Нова глобальна змінна для відстеження анімації


def load_all_icons():
    """Завантажує всі іконки в глобальні змінні після ініціалізації Tkinter."""
    global lifeline_icons, money_icon
    try:
        image_size = (30, 30)
        lifeline_icons["50/50"] = {
            "blue": ImageTk.PhotoImage(Image.open("images/50_50_blue.png").resize(image_size)),
            "yellow": ImageTk.PhotoImage(Image.open("images/50_50_yellow.png").resize(image_size)),
            "red": ImageTk.PhotoImage(Image.open("images/50_50_red.png").resize(image_size))
        }
        lifeline_icons["Дзвінок другу"] = {
            "blue": ImageTk.PhotoImage(Image.open("images/phone_blue.png").resize(image_size)),
            "yellow": ImageTk.PhotoImage(Image.open("images/phone_yellow.png").resize(image_size)),
            "red": ImageTk.PhotoImage(Image.open("images/phone_red.png").resize(image_size))
        }
        lifeline_icons["Допомога зали"] = {
            "blue": ImageTk.PhotoImage(Image.open("images/audience_blue.png").resize(image_size)),
            "yellow": ImageTk.PhotoImage(Image.open("images/audience_yellow.png").resize(image_size)),
            "red": ImageTk.PhotoImage(Image.open("images/audience_red.png").resize(image_size))
        }
        money_icon = ImageTk.PhotoImage(Image.open("images/money.png").resize(image_size))
    except FileNotFoundError:
        print("Помилка: Не знайдено файли іконок. Переконайтеся, що вони в тій самій папці.")
        lifeline_icons.clear()
        money_icon = None


def play_background_music(music_file):
    """Функція для відтворення музики. Приймає ім'я файлу."""
    pygame.mixer.music.load(os.path.join("sounds", music_file))
    pygame.mixer.music.play(-1)  # Відтворення музики у нескінченному циклі


def play_sound_effect(sound_file):
    """Відтворює одноразовий звуковий ефект."""
    sound = pygame.mixer.Sound(os.path.join("sounds", sound_file))
    sound.play()


def center_window(window, width, height):
    """Центрує вікно на екрані."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')


def load_game():
    global current_question_number, correct_answers_count, current_prize_money
    global is_50_50_used, is_phone_a_friend_used, is_ask_the_audience_used, used_questions
    if os.path.exists("savegame.json"):
        try:
            with open("savegame.json", "r") as f:
                game_state = json.load(f)
            current_question_number = game_state.get("current_question_number", 1)
            correct_answers_count = game_state.get("correct_answers_count", 0)
            current_prize_money = game_state.get("current_prize_money", 1000)
            is_50_50_used = game_state.get("is_50_50_used", False)
            is_phone_a_friend_used = game_state.get("is_phone_a_friend_used", False)
            is_ask_the_audience_used = game_state.get("is_ask_the_audience_used", False)
            used_questions = game_state.get("used_questions", [])
            return True
        except (IOError, json.JSONDecodeError):
            return False
    return False


# Функції для відтворення GIF-анімації
def load_gif_frames(gif_path):
    global gif_frames, gif_delay
    gif_frames = []
    try:
        gif = Image.open(os.path.join("images", gif_path))
        for frame in ImageSequence.Iterator(gif):
            gif_frames.append(ImageTk.PhotoImage(frame.resize((256, 256))))
        gif_delay = gif.info['duration']
    except Exception as e:
        print(f"Помилка завантаження GIF: {e}")
        gif_frames.clear()


def animate_gif():
    global gif_frames, gif_index, gif_label, gif_delay, animation_job
    if not gif_frames or not gif_label.winfo_exists():
        return

    gif_index = (gif_index + 1) % len(gif_frames)
    gif_label.configure(image=gif_frames[gif_index])

    # Використовуємо глобальну змінну для відстеження анімації
    animation_job = gif_label.winfo_toplevel().after(gif_delay, animate_gif)


def create_intro_window(root):
    # Очищуємо попередній контент
    for widget in root.winfo_children():
        widget.destroy()

    root.deiconify()
    root.title("Хто хоче стати мільйонером?")
    center_window(root, 800, 550)
    root.configure(bg="#00001B")

    # Музика запускається тільки тут і більше не зупиняється
    if not pygame.mixer.music.get_busy():
        play_background_music("background.mp3")

    def start_new_game():
        global current_question_number, correct_answers_count, current_prize_money
        global is_50_50_used, is_phone_a_friend_used, is_ask_the_audience_used, used_questions
        global after_id
        if after_id:
            root.after_cancel(after_id)
            after_id = None
        current_question_number = 1
        correct_answers_count = 0
        current_prize_money = 1000
        is_50_50_used = False
        is_phone_a_friend_used = False
        is_ask_the_audience_used = False
        used_questions = []

        play_sound_effect("klick.mp3")
        show_question_window(root)

    def continue_game():
        global after_id
        if load_game():
            if after_id:
                root.after_cancel(after_id)
                after_id = None

            play_sound_effect("klick.mp3")
            show_question_window(root)
        else:
            tk.messagebox.showinfo("Помилка", "Збережена гра не знайдена.")

    title_label = tk.Label(root, text='Вітаємо на грі "Хто хоче стати мільйонером!"', font=("Helvetica", 19, "bold"),
                           padx=80, fg="#fff", bg="#B75F07")
    title_label.pack(pady=40)

    rules_text = (
        "Правила гри прості:\n\n\n"
        "1. Вам буде поставлено 15 запитань, на які потрібно відповісти.\n\n"
        "2. На кожному етапі виграшна сума збільшується. Мета - отримати головний приз.\n\n"
        "3. Ви можете використати три підказки: '50/50', 'Дзвінок другу', 'Допомога зали'.\n\n"
        "4. Щоб відповісти - натисніть на вірну відповідь."
    )

    rules_label = tk.Label(root, text=rules_text, font=("Helvetica", 14), fg="#F0F0F0", bg="#00001B", justify="left")
    rules_label.pack(pady=20)

    button_container = tk.Frame(root, bg="#00001B")
    button_container.pack(pady=10)

    start_button = tk.Button(button_container, text="Розпочати нову гру", font=("Helvetica", 16, "bold"), bg="#E89200",
                             relief="raised", command=start_new_game)
    start_button.pack(side="left", padx=(0, 15), pady=40)

    load_button = tk.Button(button_container, text="Завантажити гру", font=("Helvetica", 16, "bold"), bg="#17AAB8",
                            relief="raised", command=continue_game, padx=20)
    load_button.pack(side="left", padx=(15, 0), pady=40)


def create_answer_buttons(root, options, command):
    button_frame = tk.Frame(root, bg="#00001B")
    button_frame.pack(pady=20, fill="x")

    buttons = []
    for i, option in enumerate(options):
        button_text = f"  {chr(65 + i)}: {option}"
        button = tk.Button(
            button_frame,
            text=button_text,
            font=("Helvetica", 12, "bold"),
            fg="white",
            bg="#1E3F90",
            activebackground="#0056b3",
            relief="raised",
            anchor="w",
            command=lambda o=option: command(o)
        )
        buttons.append(button)
        button.pack(side="top", padx=10, pady=15, fill="x")

    return buttons


def show_result_window(root, is_winner, final_prize=None):
    global gif_frames, gif_label, gif_index, animation_job

    for widget in root.winfo_children():
        widget.destroy()

    root.deiconify()
    root.title("Результат гри")
    center_window(root, 800, 550)
    root.configure(bg="#00001B")

    if is_winner:
        title_text = "Вітаємо, ви стали Мільйонером!"
        load_gif_frames("victory.gif")
    else:
        final_prize_text = f"{final_prize} грн" if final_prize else "0 грн"
        title_text = f"Гру закінчено.\nВаш виграш складає - {final_prize_text}."
        load_gif_frames("go.gif")

    title_label = tk.Label(root, text=title_text, font=("Helvetica", 19, "bold"),
                           padx=80, fg="#fff", bg="#B75F07")
    title_label.pack(pady=40)

    if gif_frames:
        gif_label = tk.Label(root, image=gif_frames[0], bg="#00001B")
        gif_label.pack(pady=20)
        gif_index = 0
        animation_job = root.after(gif_delay, animate_gif)  # Запускаємо анімацію з відстеженням

    button_container = tk.Frame(root, bg="#00001B")
    button_container.pack(pady=10)

    def handle_play_again():
        global animation_job
        play_sound_effect("klick.mp3")
        if animation_job:
            root.after_cancel(animation_job)
        create_intro_window(root)

    def handle_exit_game():
        global animation_job
        play_sound_effect("klick.mp3")
        if animation_job:
            root.after_cancel(animation_job)
        root.destroy()

    start_button = tk.Button(button_container, text="Зіграти ще раз", font=("Helvetica", 16, "bold"), bg="#E89200",
                             relief="raised", command=handle_play_again)
    start_button.pack(side="left", padx=(0, 15), pady=40)

    exit_button = tk.Button(button_container, text="Вийти з гри", font=("Helvetica", 16, "bold"), bg="#17AAB8",
                            relief="raised", command=handle_exit_game, padx=20)
    exit_button.pack(side="left", padx=(15, 0), pady=40)


def show_question_window(root):
    global current_question_number
    global correct_answers_count
    global current_prize_money
    global is_50_50_used
    global is_phone_a_friend_used
    global is_ask_the_audience_used
    global lifeline_icons, lifeline_buttons, money_icon
    global used_questions

    # Очищуємо попередній контент
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Вікно питань")
    center_window(root, 900, 650)
    root.configure(bg="#00001B")

    def handle_take_money_click(prize_amount):
        global after_id
        if after_id:
            root.after_cancel(after_id)
            after_id = None

        play_sound_effect("klick.mp3")
        root.after(200, lambda: show_result_window(root, is_winner=False, final_prize=prize_amount))

    def save_game():
        play_sound_effect("klick.mp3")
        game_state = {
            "current_question_number": current_question_number,
            "correct_answers_count": correct_answers_count,
            "current_prize_money": current_prize_money,
            "is_50_50_used": is_50_50_used,
            "is_phone_a_friend_used": is_phone_a_friend_used,
            "is_ask_the_audience_used": is_ask_the_audience_used,
            "used_questions": used_questions
        }
        with open("savegame.json", "w") as f:
            json.dump(game_state, f)
        create_popup_message("Гра успішно збережена!")

    def create_popup_message(message):
        popup = tk.Toplevel(root)
        popup.title("Підказка")
        center_window(popup, 400, 150)
        popup.configure(bg="#00001B")
        label = tk.Label(popup, text=message, font=("Helvetica", 14), fg="white", bg="#00001B", wraplength=350,
                         justify="center")
        label.pack(pady=20)
        ok_button = tk.Button(popup, text="OK", command=popup.destroy, font=("Helvetica", 12), bg="#E89200", fg="white")
        ok_button.pack(pady=10)

    def create_audience_popup(percentages):
        popup = tk.Toplevel(root)
        popup.title("Допомога зали")
        center_window(popup, 400, 250)
        popup.configure(bg="#00001B")
        title_label = tk.Label(popup, text="Результати голосування:", font=("Helvetica", 16, "bold"), fg="white",
                               bg="#00001B")
        title_label.pack(pady=10)
        for option, percentage in percentages.items():
            label_text = f"  {option}: {percentage}%"
            label = tk.Label(popup, text=label_text, font=("Helvetica", 12), fg="white", bg="#1E3F90", wraplength=350,
                             justify="left", padx=10)
            label.pack(pady=5, fill="x")
        ok_button = tk.Button(popup, text="OK", command=popup.destroy, font=("Helvetica", 12), bg="#E89200", fg="white")
        ok_button.pack(pady=10)

    def handle_phone_a_friend_click():
        play_sound_effect("klick.mp3")
        advice = game_logic.use_phone_a_friend_lifeline(current_question)
        create_popup_message(advice)

    def handle_ask_the_audience_click():
        play_sound_effect("klick.mp3")
        audience_results = game_logic.use_ask_the_audience_lifeline(current_question)
        create_audience_popup(audience_results)

    def handle_50_50_click():
        play_sound_effect("klick.mp3")
        new_options = game_logic.use_50_50_lifeline(current_question)
        for widget in answer_button_frame.winfo_children():
            widget.destroy()
        create_answer_buttons(answer_button_frame, new_options, check_and_proceed_answer)

    def update_lifeline_state(lifeline_name, action_command):
        global lifeline_buttons, is_50_50_used, is_phone_a_friend_used, is_ask_the_audience_used
        if (lifeline_name == "50/50" and is_50_50_used) or \
                (lifeline_name == "Дзвінок другу" and is_phone_a_friend_used) or \
                (lifeline_name == "Допомога зали" and is_ask_the_audience_used):
            return
        lifeline_buttons[lifeline_name].config(image=lifeline_icons[lifeline_name]["yellow"])
        root.after(250, lambda: finalize_lifeline_use(lifeline_name, action_command))

    def finalize_lifeline_use(lifeline_name, action_command):
        global is_50_50_used, is_phone_a_friend_used, is_ask_the_audience_used
        global lifeline_buttons
        lifeline_buttons[lifeline_name].config(image=lifeline_icons[lifeline_name]["red"])
        lifeline_buttons[lifeline_name].config(state=tk.DISABLED)
        if lifeline_name == "50/50":
            is_50_50_used = True
        elif lifeline_name == "Дзвінок другу":
            is_phone_a_friend_used = True
        elif lifeline_name == "Допомога зали":
            is_ask_the_audience_used = True
        action_command()

    decor_text = "─" * 20
    prize_label = tk.Label(
        root,
        text=f"{decor_text} ▸ Питання {current_question_number}. Сума: {current_prize_money} ◂ {decor_text}",
        font=("Helvetica", 16, "bold"),
        fg="#F0F0F0",
        bg="#00001B"
    )
    prize_label.pack(pady=20)

    # Призове дерево
    prize_tree_frame = tk.Frame(root, bg="#00001B")
    prize_tree_frame.pack(side="right", padx=20, pady=20, fill="y")

    # Кнопка збереження гри
    save_button = tk.Button(
        root,
        text="Зберегти гру",
        font=("Helvetica", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        relief="raised",
        command=save_game,
        padx=10
    )
    save_button.place(relx=1.0, rely=0.0, x=-20, y=50, anchor="ne")

    # Відображення призових сум
    prize_labels = []
    for i in range(14, -1, -1):
        prize = game_logic.PRIZE_TIERS[i]
        label_bg = "#00001B"
        label_fg = "#F0F0F0"
        if i == current_question_number - 1:
            label_bg = "#B75F07"
            label_fg = "white"
        elif i == 4 or i == 9:
            if current_question_number > i + 1:
                label_bg = "#00A300"
            else:
                label_bg = "#404EE6"
            label_fg = "black"
        label = tk.Label(
            prize_tree_frame,
            text=f"{i + 1:02}. {prize:9,d} грн",
            font=("Helvetica", 12, "bold"),
            bg=label_bg,
            fg=label_fg,
            anchor="e"
        )
        label.pack(fill="x", pady=2)
        prize_labels.append(label)

    current_question = game_logic.get_question_by_difficulty(current_question_number, used_questions)

    if current_question:
        used_questions.append(current_question["question"])
        question_label = tk.Label(
            root,
            text=current_question["question"],
            font=("Helvetica", 18, "bold"),
            fg="white",
            bg="#B75F07",
            wraplength=700,
            padx=0,
        )
        question_label.pack(pady=10)

        def check_and_proceed_answer(player_answer):
            global current_question_number, correct_answers_count, current_prize_money, after_id

            play_sound_effect("klick.mp3")

            if after_id:
                root.after_cancel(after_id)
                after_id = None

            is_correct, final_prize = game_logic.handle_answer_logic(
                player_answer,
                current_question,
                correct_answers_count
            )
            if is_correct:
                correct_answers_count += 1
                if correct_answers_count == 15:
                    show_result_window(root, is_winner=True)
                else:
                    current_question_number += 1
                    current_prize_money = game_logic.PRIZE_TIERS[current_question_number - 1]
                    root.after(200, lambda: show_question_window(root))
            else:
                show_result_window(root, is_winner=False, final_prize=final_prize)

        answer_button_frame = tk.Frame(root, bg="#00001B")
        answer_button_frame.pack(pady=20, fill="x")
        create_answer_buttons(answer_button_frame, current_question["options"], check_and_proceed_answer)

        lifeline_frame = tk.Frame(root, bg="#00001B")
        lifeline_frame.pack(side="bottom", pady=30, ipadx=200)

        if current_question_number > 1:
            take_away_prize = game_logic.PRIZE_TIERS[current_question_number - 2]
        else:
            take_away_prize = 0
        button_state = tk.NORMAL if current_question_number > 1 else tk.DISABLED

        take_money_button = tk.Button(
            root,
            text="Забрати гроші",
            font=("Helvetica", 12, "bold"),
            bg="#FF3333",
            fg="white",
            relief="raised",
            image=money_icon,
            compound=tk.LEFT,
            command=lambda: handle_take_money_click(take_away_prize),
            state=button_state
        )
        take_money_button.place(relx=1.0, rely=1.0, x=-15, y=-30, anchor="se")

        lifelines_info = [
            ("50/50", "50/50", handle_50_50_click),
            ("Дзвінок другу", "Дзвінок другу", handle_phone_a_friend_click),
            ("Допомога зали", "Допомога зали", handle_ask_the_audience_click),
        ]

        button_width = 180
        button_height = 30
        container_50_50 = tk.Frame(lifeline_frame, bg="#00001B")
        container_50_50.pack(side="left", padx=10, expand=True)
        container_phone = tk.Frame(lifeline_frame, bg="#00001B")
        container_phone.pack(side="left", expand=True)
        container_audience = tk.Frame(lifeline_frame, bg="#00001B")
        container_audience.pack(side="left", padx=10, expand=True)

        for name, text, command in lifelines_info:
            is_used = False
            if name == "50/50":
                is_used = is_50_50_used
                parent_frame = container_50_50
            elif name == "Дзвінок другу":
                is_used = is_phone_a_friend_used
                parent_frame = container_phone
            elif name == "Допомога зали":
                is_used = is_ask_the_audience_used
                parent_frame = container_audience
            button = tk.Button(
                parent_frame,
                text=text,
                font=("Helvetica", 12),
                bg="#1E3F90",
                fg="white",
                image=lifeline_icons[name]["red"] if is_used else lifeline_icons[name]["blue"],
                compound=tk.LEFT,
                command=lambda n=name, cmd=command: update_lifeline_state(n, cmd),
                state=tk.DISABLED if is_used else tk.NORMAL,
                width=button_width,
                height=button_height,
                padx=5
            )
            button.pack()
            lifeline_buttons[name] = button

    else:
        error_label = tk.Label(root, text="Помилка: Питання не знайдено.", fg="red", bg="#00001B")
        error_label.pack()