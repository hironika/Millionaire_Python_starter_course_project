import questions
import random

# Список призових сум
PRIZE_TIERS = [
    1000, 2000, 3000, 5000, 10000, 16000, 24000,
    32000, 48000, 64000, 96000, 150000, 250000,
    500000, 1000000
]


def get_non_burnable_sum(correct_answers_count):
    """
    Повертає незгораєму суму на основі кількості правильних відповідей.
    """
    # Досягнення "незгораємої суми" після 5 та 10 правильних відповідей.
    if correct_answers_count >= 10:
        return PRIZE_TIERS[9]  # 64000
    elif correct_answers_count >= 5:
        return PRIZE_TIERS[4]  # 10000
    else:
        return 0


def get_question_by_difficulty(question_number, used_questions):
    """
    Отримує випадкове питання відповідного рівня складності, яке ще не було використано.
    """
    if 1 <= question_number <= 5:
        difficulty = "easy"
    elif 6 <= question_number <= 10:
        difficulty = "medium"
    elif 11 <= question_number <= 15:
        difficulty = "hard"
    else:
        return None

    questions_list = questions.get_all_questions().get(difficulty)
    if not questions_list:
        return None

    available_questions = [q for q in questions_list if q['question'] not in used_questions]

    if not available_questions:
        print(f"Питання рівня '{difficulty}' закінчились.")
        return None

    selected_question = random.choice(available_questions)

    # Додано: вказуємо рівень складності у словнику питання
    selected_question['difficulty'] = difficulty

    return selected_question


def check_answer(player_answer, correct_answer):
    """
    Перевіряє, чи є відповідь гравця правильною.
    """
    return player_answer == correct_answer


def handle_answer_logic(player_answer, current_question, correct_answers_count):
    """
    Перевіряє відповідь і повертає стан гри:
    - is_correct (bool): True, якщо відповідь правильна, False - якщо ні.
    - final_prize (int): Зароблена незгораєма сума у разі програшу.
    """
    if check_answer(player_answer, current_question["correct_answer"]):
        return True, None
    else:
        # У разі неправильної відповіді розраховуємо фінальний приз
        final_prize = get_non_burnable_sum(correct_answers_count)
        return False, final_prize


def use_50_50_lifeline(current_question):
    correct_answer = current_question["correct_answer"]
    options = list(current_question["options"])

    # Видаляємо правильну відповідь зі списку для вибору неправильних
    incorrect_options = [opt for opt in options if opt != correct_answer]

    # Вибираємо дві випадкові неправильні відповіді, щоб видалити їх
    options_to_remove = random.sample(incorrect_options, 2)

    # Створюємо новий список, що містить правильну і одну випадкову неправильну відповідь
    new_options = [opt for opt in options if opt not in options_to_remove]
    random.shuffle(new_options)

    return new_options


def use_phone_a_friend_lifeline(current_question):
    """
    Симулює дзвінок другу.
    Повертає правильну відповідь з імовірністю 85% або випадкову неправильну з імовірністю 15%.
    """
    correct_answer = current_question["correct_answer"]
    options = list(current_question["options"])

    if random.random() < 0.85:  # 85% шанс на правильну відповідь
        return f"Я вважаю, що це {correct_answer}."
    else:  # 15% шанс на неправильну відповідь
        incorrect_options = [opt for opt in options if opt != correct_answer]
        return f"Я думаю, що це {random.choice(incorrect_options)}, але не впевнений."

def use_ask_the_audience_lifeline(current_question):
    """
    Симулює "Допомогу зали".
    Генерує розподіл голосів у відсотках, де правильна відповідь отримує найбільший відсоток.
    """
    correct_answer = current_question["correct_answer"]
    options = list(current_question["options"])
    percentages = {}
    remaining_percentage = 100

    # Визначаємо відсоток для правильної відповіді в залежності від складності
    # (просте питання - більше впевненості, складне - менше)
    if current_question["difficulty"] == "easy":
        correct_percentage = random.randint(65, 90)
    elif current_question["difficulty"] == "medium":
        correct_percentage = random.randint(45, 75)
    else:  # "hard"
        correct_percentage = random.randint(30, 60)

    percentages[correct_answer] = correct_percentage
    remaining_percentage -= correct_percentage
    incorrect_options = [opt for opt in options if opt != correct_answer]

    # Розподіляємо решту відсотків між неправильними відповідями
    if len(incorrect_options) > 0:
        incorrect_percentages = [0] * len(incorrect_options)
        for _ in range(remaining_percentage):
            incorrect_percentages[random.randint(0, len(incorrect_options) - 1)] += 1

        for i, opt in enumerate(incorrect_options):
            percentages[opt] = incorrect_percentages[i]

    return percentages
