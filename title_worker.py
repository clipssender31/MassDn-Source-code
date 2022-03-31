import global_variables
import time
import threading
import ctypes
from websocket import create_connection
import utils
import psutil
import os

WORKER_MODE = "login"


def title(content):
    ctypes.windll.kernel32.SetConsoleTitleW(content)

def titleThread():
    while True:
        if WORKER_MODE == "login":
            title(f"{global_variables.app_data['tool_name']} | Login")

        elif WORKER_MODE == "main":
            title(
                f"{global_variables.app_data['tool_name']} | Tokens loaded: {len(global_variables.tokens)}")

        elif WORKER_MODE == "joiner":
            title(f"{global_variables.app_data['tool_name']} | Tokens loaded: {len(global_variables.tokens)} | Successful joins: {global_variables.joins_success} | Failed joins: {global_variables.joins_failed} | Progress: [{global_variables.joins_success + global_variables.joins_failed}/{len(global_variables.tokens)}]")

        elif WORKER_MODE == "scraper":
            if global_variables.approximate_member_count == None:
                scraped_members = global_variables.ids_scraped
            else:
                member_count = utils.returnApproxCount(
                    global_variables.approximate_member_count, global_variables.approximate_presence_count)
                scraped_members = f"[{global_variables.ids_scraped}/approx. {member_count}]"

            title(
                f"{global_variables.app_data['tool_name']} | Tokens loaded: {len(global_variables.tokens)} | Scraped members: {scraped_members}")

        elif WORKER_MODE == "dmer":
            title(f"{global_variables.app_data['tool_name']} | Tokens loaded: {len(global_variables.tokens)} | Successful DMs: {global_variables.messages_sent} | Failed DMs: {global_variables.messages_failed} | Progress: [{global_variables.messages_sent + global_variables.messages_failed}/{global_variables.ids_scraped_finished}]")

        time.sleep(0.1)


def websocketThread():
    while True:
        try:
            global_variables.ws.ping()
            time.sleep(7)
        except:
            global_variables.ws = create_connection("ws://gateway.discord.gg/?v=9&encoding=json")
            continue


def initializeWorker():
    threading.Thread(target=titleThread, daemon=True).start()
    threading.Thread(target=websocketThread, daemon=True).start()
