from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv
import tkinter as tk
from tkinter import simpledialog, messagebox

# Функция для ввода продукта
def get_product_input():
    ROOT = tk.Tk()
    ROOT.withdraw()  # Скрываем основное окно
    product = simpledialog.askstring(title="Введите продукт", prompt="Какой продукт вы хотите найти?")
    if not product:
        messagebox.showerror("Ошибка", "Вы не ввели продукт!")
        exit()
    return product

# Получаем продукт от пользователя
product = get_product_input()

# Настройки для Chrome
options = Options()
options.add_argument('start_maximized')
driver = webdriver.Chrome(options=options)

# Открываем сайт
driver.get("https://www.citilink.ru/")
time.sleep(2)

# Поиск по запросу
# input_field = driver.find_element(By.ID, 'title-search-input')
input_field = driver.find_element(By.NAME, 'text')
# time.sleep(2)
# input_field = driver.find_element(By.NAME, 'q')'
input_field.send_keys(product)
input_field.send_keys(Keys.ENTER)
print()
# Список для хранения данных
data = []

# Основной цикл для сбора данных
while True:
    wait = WebDriverWait(driver, timeout=30)

    # Ждем, пока загрузятся карточки товаров
    cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-meta-name='SnippetProductHorizontalLayout']")))

    # Если карточки не найдены, завершаем выполнение
    if not cards:
        print("Нет доступных карточек товаров. Завершение выполнения.")
        break
    print()
    # Прокрутка страницы для загрузки дополнительных карточек
    last_count = 0
    while True:
        driver.execute_script('window.scrollBy(0, 200)')
        time.sleep(2)  # Даем время на загрузку новых элементов
        cards = driver.find_elements(By.XPATH, "//div[@data-meta-name='SnippetProductHorizontalLayout']")  # Обновляем список карточек
        if len(cards) == last_count:  # Если количество карточек не изменилось, выходим из цикла
            break
        last_count = len(cards)

    # Извлечение данных из карточек
    for card in cards:
        try:
            price = card.find_element(By.XPATH, './/span[@data-meta-price]').text.replace(" ", "")
            try:
                rating = card.find_element(By.XPATH, ".//div[@data-meta-name='MetaInfo_rating']").text
            except Exception as e:
                rating = ""
            name = card.find_element(By.XPATH, ".//a[@data-meta-name='Snippet__title']").get_attribute('title')
            url = card.find_element(By.XPATH, ".//a[@data-meta-name='Snippet__title']").get_attribute('href')
            data.append([name, price, rating, url])  # Сохраняем данные в список
        except Exception as e:
            print(f"Ошибка при извлечении данных: {e}")
    print(data)
    print()

    # Переход к следующей странице
    try:
        # button = driver.find_element(By.CLASS_NAME, "app-catalog-peotpw")
        button = driver.find_element(By.XPATH, ".//a[@data-meta-name='PageLink__page-page-next']")
        actions = ActionChains(driver)
        actions.move_to_element(button).click()
        actions.perform()
    except Exception as e:
        print(f"Ошибка при переходе на следующую страницу: {e}")
        break  # Если кнопка не найдена, выходим из цикла

# Сохранение данных в CSV файл
with open(f'citilink-{product}_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Описание', 'Цена', 'Рейтинг', 'Ссылка'])  # Заголовки колонок
    writer.writerows(data)  # Записываем данные

print(f"Данные успешно сохранены в citilink-{product}_data.csv")

# Закрываем браузер
driver.quit()
