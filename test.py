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