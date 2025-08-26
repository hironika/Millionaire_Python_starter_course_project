import tkinter as tk
from PIL import Image, ImageTk
import game_logic
import questions

# Глобальні змінні для відстеження стану
used_questions = []
current_question_number = 1
correct_answers_count = 0
current_prize_money = 1000
is_50_50_used = False
is_phone_a_friend_used = False
is_ask_the_audience_used = False

# Глобальні словники для іконок і кнопок
lifeline_icons = {
    "50/50": {"blue": None, "yellow": None, "red": None},
    "Дзвінок другу": {"blue": None, "yellow": None, "red": None},
    "Допомога зали": {"blue": None, "yellow": None, "red": None}
}
lifeline_buttons = {}


def create_intro_window():
    root = tk.Tk()
    root.title("Хто хоче стати мільйонером?")
    root.geometry("800x500")
    root.configure(bg="#00001B")

    def start_game():
        root.destroy()
        show_question_window()

    title_label = tk.Label(root, text='Вітаємо на грі "Хто хоче стати мільйонером!"', font=("Helvetica", 21, "bold"),
                           padx=40, fg="#fff", bg="#B75F07")
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

    start_button = tk.Button(root, text="Розпочати гру", font=("Helvetica", 16, "bold"), bg="#E89200",
                             relief="raised", command=start_game)
    start_button.pack(pady=20)

    root.mainloop()


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


def show_result_window(is_winner, final_prize=None):
    result_root = tk.Tk()
    result_root.title("Результат гри")
    result_root.geometry("800x600")
    result_root.configure(bg="#00001B")

    if is_winner:
        result_text = "Вітаємо! Ви перемогли та виграли 1 000 000 гривень!"
        label_color = "green"
    else:
        final_prize_text = f"{final_prize} гривень" if final_prize else "0 грн"
        result_text = f"На жаль, ви програли. Ваш виграш - {final_prize_text}."
        label_color = "red"

    result_label = tk.Label(
        result_root,
        text=result_text,
        font=("Helvetica", 21, "bold"),
        fg=label_color,
        bg="#00001B"
    )
    result_label.pack(pady=50)

    result_root.mainloop()


def show_question_window():
    global current_question_number
    global correct_answers_count
    global current_prize_money
    global is_50_50_used
    global is_phone_a_friend_used
    global is_ask_the_audience_used
    global lifeline_icons, lifeline_buttons
    global used_questions

    question_root = tk.Tk()
    question_root.title("Вікно питань")
    question_root.geometry("900x600")
    question_root.configure(bg="#00001B")

    def create_popup_message(message):
        popup = tk.Toplevel(question_root)
        popup.title("Підказка")
        popup.geometry("400x150")
        popup.configure(bg="#00001B")

        label = tk.Label(popup, text=message, font=("Helvetica", 14), fg="white", bg="#00001B", wraplength=350,
                         justify="center")
        label.pack(pady=20)

        ok_button = tk.Button(popup, text="OK", command=popup.destroy, font=("Helvetica", 12), bg="#E89200", fg="white")
        ok_button.pack(pady=10)

    def create_audience_popup(percentages):
        popup = tk.Toplevel(question_root)
        popup.title("Допомога зали")
        popup.geometry("400x250")
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
        advice = game_logic.use_phone_a_friend_lifeline(current_question)
        create_popup_message(advice)

    def handle_ask_the_audience_click():
        audience_results = game_logic.use_ask_the_audience_lifeline(current_question)
        create_audience_popup(audience_results)

    def handle_50_50_click():
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

        question_root.after(250, lambda: finalize_lifeline_use(lifeline_name, action_command))

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

        # Виконуємо команду, яка тепер викликає правильну логіку
        action_command()

    try:
        image_size = (30, 30)
        lifeline_icons["50/50"]["blue"] = ImageTk.PhotoImage(Image.open("images/50_50_blue.png").resize(image_size))
        lifeline_icons["50/50"]["yellow"] = ImageTk.PhotoImage(Image.open("images/50_50_yellow.png").resize(image_size))
        lifeline_icons["50/50"]["red"] = ImageTk.PhotoImage(Image.open("images/50_50_red.png").resize(image_size))

        lifeline_icons["Дзвінок другу"]["blue"] = ImageTk.PhotoImage(Image.open("images/phone_blue.png").resize(image_size))
        lifeline_icons["Дзвінок другу"]["yellow"] = ImageTk.PhotoImage(Image.open("images/phone_yellow.png").resize(image_size))
        lifeline_icons["Дзвінок другу"]["red"] = ImageTk.PhotoImage(Image.open("images/phone_red.png").resize(image_size))

        lifeline_icons["Допомога зали"]["blue"] = ImageTk.PhotoImage(Image.open("images/audience_blue.png").resize(image_size))
        lifeline_icons["Допомога зали"]["yellow"] = ImageTk.PhotoImage(Image.open("images/audience_yellow.png").resize(image_size))
        lifeline_icons["Допомога зали"]["red"] = ImageTk.PhotoImage(Image.open("images/audience_red.png").resize(image_size))

    except FileNotFoundError:
        print("Помилка: Не знайдено файли іконок. Переконайтеся, що вони в тій самій папці.")
        lifeline_icons = {key: {"blue": None, "yellow": None, "red": None} for key in lifeline_icons.keys()}

    decor_text = "─" * 20

    prize_label = tk.Label(
        question_root,
        text=f"{decor_text} ▸ Питання {current_question_number}. Сума: {current_prize_money} ◂ {decor_text}",
        font=("Helvetica", 16, "bold"),
        fg="#F0F0F0",
        bg="#00001B"
    )
    prize_label.pack(pady=20)

    # Призове дерево
    prize_tree_frame = tk.Frame(question_root, bg="#00001B")
    prize_tree_frame.pack(side="right", padx=20, pady=20, fill="y")

    # Відображення призових сум
    prize_labels = []
    for i in range(14, -1, -1):
        prize = game_logic.PRIZE_TIERS[i]

        # Логіка кольорів
        label_bg = "#00001B"  # Колір за замовчуванням
        label_fg = "#F0F0F0"  # Колір тексту за замовчуванням

        # Виділяємо поточне питання
        if i == current_question_number - 1:
            label_bg = "#B75F07"
            label_fg = "white"

        # Виділяємо незгораючі суми, якщо вони ще не досягнуті
        elif i == 4 or i == 9:
            # Якщо поточне питання далі, ніж незгораюча сума, вона стає зеленою
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
            question_root,
            text=current_question["question"],
            font=("Helvetica", 18, "bold"),
            fg="white",
            bg="#B75F07",
            wraplength=700,
            padx=0,
        )
        question_label.pack(pady=10)

        def check_and_proceed_answer(player_answer):
            global current_question_number
            global correct_answers_count
            global current_prize_money

            is_correct, final_prize = game_logic.handle_answer_logic(
                player_answer,
                current_question,
                correct_answers_count
            )

            question_root.destroy()

            if is_correct:
                correct_answers_count += 1
                if correct_answers_count == 15:
                    show_result_window(is_winner=True)
                else:
                    current_question_number += 1
                    current_prize_money = game_logic.PRIZE_TIERS[current_question_number - 1]
                    show_question_window()
            else:
                show_result_window(is_winner=False, final_prize=final_prize)

        answer_button_frame = tk.Frame(question_root, bg="#00001B")
        answer_button_frame.pack(pady=20, fill="x")

        create_answer_buttons(answer_button_frame, current_question["options"], check_and_proceed_answer)

        # Фрейм для підказок
        lifeline_frame = tk.Frame(question_root, bg="#00001B")
        lifeline_frame.pack(side="bottom", pady=30, ipadx=200)

        lifelines_info = [
            ("50/50", "50/50", handle_50_50_click),
            ("Дзвінок другу", "Дзвінок другу", handle_phone_a_friend_click),
            ("Допомога зали", "Допомога зали", handle_ask_the_audience_click),
        ]

        button_width = 180
        button_height = 30

        # Створення контейнерів для кожної кнопки
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
        error_label = tk.Label(question_root, text="Помилка: Питання не знайдено.", fg="red", bg="#00001B")
        error_label.pack()

    question_root.mainloop()


if __name__ == "__main__":
    create_intro_window()