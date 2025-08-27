def open_telegram_profile():
        webbrowser.open_new("https://t.me/tatyanakohan") # <-- Твоє посилання

    telegram_link_label = tk.Label(root, text="Розробник у Telegram",
                                   font=("Helvetica", 12, "underline"),
                                   fg="#D3D3D3", bg="#00001B", cursor="hand2")
    # Використовуємо .place() для точного позиціонування
    telegram_link_label.place(relx=1.0, rely=1.0, x=-10, y=-20, anchor="se")
    telegram_link_label.bind("<Button-1>", lambda e: open_telegram_profile())
    # --- КІНЕЦЬ БЛОКУ З ПОСИЛАННЯМ ---

    button_container = tk.Frame(root, bg="#00001B")
    button_container.pack(pady=10)