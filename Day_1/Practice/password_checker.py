# -*- coding: utf-8 -*-
"""
Задача №1. Проверка «правильного» пароля.

Модуль содержит:
  * check_password(password) -> tuple[bool, str] — проверка пароля по правилам;
  * main() — интерактивный ввод пароля (не более 5 попыток).

Правила пароля:
  1. Длина от 8 до 15 символов включительно.
  2. Пароль должен состоять ТОЛЬКО из символов четырёх наборов:
       - цифры               (string.digits)
       - латиница строчная   (string.ascii_lowercase)
       - латиница прописная  (string.ascii_uppercase)
       - спецсимволы         '_!@#$%^&'
  3. Хотя бы один символ из КАЖДОГО набора.
"""

import string as st

# --- Четыре набора допустимых символов -------------------------------
DIGITS = st.digits            # '0123456789'
LOWER = st.ascii_lowercase    # 'a'..'z'
UPPER = st.ascii_uppercase    # 'A'..'Z'
SPECIAL = '_!@#$%^&'

ALLOWED = DIGITS + LOWER + UPPER + SPECIAL   # всё допустимое сразу

MIN_LEN = 8
MAX_LEN = 15
MAX_ATTEMPTS = 5


def check_password(password: str) -> tuple[bool, str]:
    """Проверяет пароль по всем правилам.

    Возвращает кортеж (ok, reasons):
      ok      — True, если пароль подходит;
      reasons — строка с результатом: 'пароль подходит' или
                пояснение, почему пароль не принят и что исправить.
    """
    # Проверка типа: из main() приходит str, но подстрахуемся.
    if not isinstance(password, str):
        return False, 'Пароль должен быть строкой'

    # --- Правило 1: длина -------------------------------------------
    if not (MIN_LEN <= len(password) <= MAX_LEN):
        return (
            False,
            f'Пароль не принят: длина {len(password)} символов, '
            f'а должна быть от {MIN_LEN} до {MAX_LEN} включительно. '
            f'Добавьте или уберите символы.'
        )

    # --- Правило 2: только допустимые символы -----------------------
    wrong = sorted({ch for ch in password if ch not in ALLOWED})
    if wrong:
        shown = ''.join(wrong)
        return (
            False,
            f'Пароль не принят: недопустимые символы: {shown}. '
            'Разрешены только цифры, латинские буквы '
            '(строчные и прописные) и спецсимволы из набора _!@#$%^&. '
            'Уберите лишние символы.'
        )

    # --- Правило 3: хотя бы один символ из каждого набора -----------
    missing = []
    if not any(ch in DIGITS for ch in password):
        missing.append('цифру (0-9)')
    if not any(ch in LOWER for ch in password):
        missing.append('строчную латинскую букву (a-z)')
    if not any(ch in UPPER for ch in password):
        missing.append('прописную латинскую букву (A-Z)')
    if not any(ch in SPECIAL for ch in password):
        missing.append('спецсимвол из набора _!@#$%^&')
    if missing:
        need = ', '.join(missing)
        return (
            False,
            f'Пароль не принят: не хватает символов из следующих наборов: '
            f'{need}. Добавьте их в пароль.'
        )

    return True, 'пароль подходит'


def main() -> None:
    """Интерактивный ввод пароля: максимум 5 попыток."""
    print('Придумайте пароль по правилам:')
    print(f'  - длина от {MIN_LEN} до {MAX_LEN} символов;')
    print('  - только цифры, латинские буквы (a-z, A-Z)')
    print(f'    и спецсимволы из набора {SPECIAL};')
    print('  - хотя бы один символ из каждого набора.')
    print(f'Попыток ввода: {MAX_ATTEMPTS}.\n')

    for attempt in range(1, MAX_ATTEMPTS + 1):
        password = input(f'Попытка {attempt} из {MAX_ATTEMPTS}. Введите пароль: ')

        ok, reasons = check_password(password)
        print(reasons.rstrip('.') + '.', end='\n\n')

        if ok:
            print('Пароль принят.')
            break
    else:
        # Цикл завершился без break — все попытки исчерпаны.
        print('Попытки закончились. Пароль так и не был принят.')


if __name__ == '__main__':
    main()
