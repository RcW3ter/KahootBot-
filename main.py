import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from user_agent import generate_user_agent
import threading
import random
import string
import secrets
import time

def generate_pseudo(length=4):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

root = ctk.CTk()
root.geometry("400x600")
root.title("KahootRaid! - Main")
root.resizable(False, False)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BotScrollbar = ctk.CTkScrollableFrame(root, width=360, height=530)
BotScrollbar.place(x=10, y=10)

button_frame = ctk.CTkFrame(BotScrollbar, height=50)
button_frame.pack(side="bottom", fill="x")

bots = []

def add_bot():
    bot_card = ctk.CTkFrame(BotScrollbar, corner_radius=10, border_width=2, border_color="#3A7FF6")
    bot_card.pack(fill="x", pady=10, padx=10)

    top_frame = ctk.CTkFrame(bot_card, fg_color="transparent")
    top_frame.pack(fill="x", padx=5, pady=5)

    name_entry = ctk.CTkEntry(top_frame, placeholder_text="Nom du Bot")
    name_entry.pack(side="left", fill="x", expand=True, padx=5)

    def on_generate():
        name_entry.delete(0, "end")
        name_entry.insert(0, generate_pseudo())
    gen_button = ctk.CTkButton(top_frame, text="Générer Pseudo", command=on_generate, width=120)
    gen_button.pack(side="right", padx=5)

    output_frame = ctk.CTkScrollableFrame(bot_card, width=330, height=80)
    output_frame.pack(padx=5, pady=5)
    
    def bot_log(message):
        log_label = ctk.CTkLabel(output_frame, text=message, anchor="w", justify="left", wraplength=310)
        log_label.pack(anchor="w", padx=5, pady=1)
        output_frame.update_idletasks()

    def delete_bot():
        bot_card.destroy()
        bots.remove(bot_info)

    delete_button = ctk.CTkButton(bot_card, text="Supprimer", command=delete_bot, width=100)
    delete_button.pack(side="bottom", anchor="e", padx=5, pady=5)

    bot_info = {"entry": name_entry, "log": bot_log, "card": bot_card}
    bots.append(bot_info)

def Bot(code, bot_info):
    pseudo = bot_info["entry"].get()
    if not pseudo:
        pseudo = generate_pseudo(6)
    bot_info["log"](f"[+]Pseudo: {pseudo}")

    ua = generate_user_agent()
    bot_info["log"](f"[+]User Agent: {ua}")

    options = Options()
    options.add_argument(f'--user-agent={ua}')
    options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)

    try:
        driver.get("https://kahoot.it/join")
        bot_info["log"]("[+]Load Kahoot Website")

        game_placeholder = driver.find_element(By.ID, "game-input")
        game_placeholder.send_keys(code)

        enter_btn = driver.find_element(By.CSS_SELECTOR, ".button__Button-sc-vzgdbz-0.cOYBIH.enter-pin-form__SubmitButton-sc-z047z0-2.eHMrdk")
        enter_btn.click()

        nickname_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nickname")))
        nickname_input.send_keys(pseudo)

        join_btn = driver.find_element(By.CSS_SELECTOR, '[data-functional-selector="join-button-username"]')
        join_btn.click()

        bot_info["log"](f"[+]Log as {pseudo}")

        while True:
            try:
                podium = driver.find_element(By.CSS_SELECTOR, ".podium__PageWrapper-sc-siupzf-0.kfwUDm")
                bot_info["log"](f"[-]{pseudo} Log out")
                break
            except NoSuchElementException:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, '[data-functional-selector^="answer-"]')
                    valid_buttons = [b for b in buttons if b.get_attribute("data-functional-selector") in ["answer-0","answer-1","answer-2","answer-3"]]
                    if valid_buttons:
                        choice = secrets.choice(valid_buttons)
                        selector = choice.get_attribute("data-functional-selector")
                        bot_info["log"](f"[+]{pseudo} Answer : {selector}")
                        choice.click()
                except (StaleElementReferenceException, NoSuchElementException):
                    pass
                time.sleep(1)

    finally:
        driver.quit()
        bot_info["log"](f"[+]Driver close :  {pseudo}")

def start_bots():
    CodeInput = ctk.CTkInputDialog(text="Kahoot's Party Code :", title="KahootRaid! - PlaceHolder")
    code = CodeInput.get_input()
    if not code:
        return

    def run_all():
        for bot_info in bots:
            threading.Thread(target=Bot, args=(code, bot_info), daemon=True).start()

    threading.Thread(target=run_all, daemon=True).start()

AddBot = ctk.CTkButton(button_frame, command=add_bot, text="+ Add Bot")
AddBot.pack(pady=5, padx=5, fill="x")

StartButton = ctk.CTkButton(root, command=start_bots, text="Start")
StartButton.place(x=10, y=565)

root.mainloop()