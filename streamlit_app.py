import streamlit as st
import random
import questions  # Імпортуємо твою базу питань!

# Налаштування сторінки
st.set_page_config(
    page_title="Millionaire Project Showcase",
    page_icon="🎯",
    layout="centered"
)

# Заголовок веб-додатка
st.title("🎯 Візуалізація проєкту «Хто хоче стати мільйонером?»")
st.write("""
    Цей веб-додаток демонструвальний. Він створений для візуалізації внутрішньої логіки, 
    алгоритмів рандому та підказок мого курсового проєкту, написаного на Python.
""")

st.divider()

# --- СЕКЦІЯ 1: СТАТИСТИКА БАЗИ ДАНИХ ПИТАНЬ ---
st.header("📊 1. Аналітика бази даних питань")

# Отримуємо питання з твого модуля questions.py
try:
    all_questions = questions.get_all_questions()
except AttributeError:
    # Якщо структура трохи інша, використовуємо прямий словник
    all_questions = questions.questions_dict if hasattr(questions, 'questions_dict') else {}

if all_questions:
    # Рахуємо кількість питань у кожній категорії
    stats = {level: len(q_list) for level, q_list in all_questions.items()}
    
    st.write("Розподіл питань у `questions.py` за рівнями складності:")
    # Малюємо красивий графік прямо в Streamlit
    st.bar_chart(stats)
else:
    st.warning("Не вдалося завантажити базу питань. Перевірте імпорт модуля `questions`.")

st.divider()

# --- СЕКЦІЯ 2: ДЕМОНСТРАЦІЯ КОНТРОЛЬОВАНОГО РАНДОМУ ---
st.header("🎲 2. Симуляція контрольованого рандому")
st.write("Виберіть рівень складності, щоб побачити, як функція фільтрує та випадково обирає питання:")

selected_level = st.selectbox("Оберіть рівень складності:", list(all_questions.keys()) if all_questions else ["easy", "medium", "hard"])

if all_questions and selected_level in all_questions:
    questions_list = all_questions[selected_level]
    
    if st.button("🎲 Згенерувати випадкове питання"):
        # Імітуємо роботу нашої функції get_question_by_difficulty
        random_q = random.choice(questions_list)
        
        st.info(f"**Питання:** {random_q['question']}")
        
        # Відображаємо варіанти відповідей
        cols = st.columns(2)
        cols[0].write(f"🅰️ {random_q['options'][0]}")
        cols[1].write(f"🅱️ {random_q['options'][1]}")
        cols[0].write(f"🆃 {random_q['options'][2]}")
        cols[1].write(f"🅳 {random_q['options'][3]}")
        
        st.success(f"**Правильна відповідь (для перевірки логіки):** {random_q['correct_answer']}")

st.divider()

# --- СЕКЦІЯ 3: МАТЕМАТИЧНЕ МОДЕЛЮВАННЯ ПІДКАЗОК ---
st.header("💡 3. Робота алгоритмів підказок")
st.write("Спробуйте запустити симуляцію підказки **«Помога зала»**:")

if all_questions:
    # Беремо тестове питання для демонстрації підказки
    test_q = all_questions[list(all_questions.keys())[0]][0]
    correct = test_q['correct_answer']
    options = test_q['options']
    
    if st.button("📊 Запустити підказку «Помога зала»"):
        st.write(f"**Питання:** {test_q['question']}")
        
        # Моделюємо розподіл голосів, де правильний відповідь має пріоритет
        votes = {}
        remaining_percent = 100
        
        # Даємо правильній відповіді більший випадковий відсоток (наприклад, від 50 до 75)
        correct_votes = random.randint(50, 75)
        votes[correct] = correct_votes
        remaining_percent -= correct_votes
        
        # Розподіляємо залишок між іншими трьома варіантами
        wrong_options = [opt for opt in options if opt != correct]
        v1 = random.randint(0, remaining_percent)
        remaining_percent -= v1
        v2 = random.randint(0, remaining_percent)
        v3 = remaining_percent
        
        random_wrong_votes = [v1, v2, v3]
        random.shuffle(random_wrong_votes)
        
        for i, opt in enumerate(wrong_options):
            votes[opt] = random_wrong_votes[i]
            
        # Малюємо графік результатів голосування зали
        st.bar_chart(votes)
        st.write("Результати симуляції голосування глядачів у відсотках.")

st.divider()
st.caption("© Тетяна Кохан | Розроблено для демонстрації портфоліо на Streamlit Cloud.")
