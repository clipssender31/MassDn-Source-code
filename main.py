from itertools import cycle
from tasksio import TaskPool
from colorama import Fore, Back, Style
from scrape import scrape
from websocket import create_connection
import authsocket
import subprocess
import hashlib
import json
import psutil
import os
import global_variables
import asyncio
import utils
import api
import title_worker
import random
import emoji
import traceback

async def GPUtil():
    try:
        title_worker.WORKER_MODE = "main"
        global_variables.tokens = [line.rstrip(
            "\n") for line in open("data/tokens.txt", "r")]
        print()

        count = input("LIMITER> Limit tokens? (blank if not): ")
        if count != "":
            global_variables.tokens = global_variables.tokens[:int(count)]

        # CUSTOM SCRIPT
        print()
        if global_variables.app_data["customScripts"] == "true":
            if input("LUA> Use custom scripts? Y/N: ").lower() == "y":
                pass

        guild_info = None

        # JOINER
        if input("JOINER> Run Joiner? Y/N: ").lower() == "y":
            title_worker.WORKER_MODE = "joiner"
            invite = input("JOINER> Invite: ")
            delay = input("JOINER> Delay? (blank if not): ")
            if delay == "":
                delay = 0
            else:
                delay = float(delay)

            if invite.endswith("/"):
                invite = invite[:-1]
            if 'discord' in invite and '/' in invite and 'http' in invite:
                splitter = invite.split('/')
                invite = splitter[len(splitter)-1]

            guild_info = await api.getInviteInfo(invite)
            if guild_info == {"message": "Unknown Invite", "code": 10006}:
                print("JOINER> ERROR, Unknown invite.")
                return await GPUtil()

            global_variables.current_guild_info = guild_info
            if 'approximate_member_count' in guild_info and 'approximate_presence_count' in guild_info:
                member_count = utils.returnApproxCount(
                    guild_info["approximate_member_count"], guild_info["approximate_presence_count"])
                print("JOINER> Recommended token count: approx. " + str(round(member_count / 4)
                                                                        ) + ", risk mode: approx. " + str(round((member_count / 9))))

                global_variables.approximate_presence_count = guild_info["approximate_presence_count"]
                global_variables.approximate_member_count = guild_info["approximate_member_count"]

            count = input("JOINER> Limit tokens? (blank if not): ")
            if count != "":
                global_variables.tokens = global_variables.tokens[:int(count)]
            print(
                f"JOINER> Attempting to join: {Fore.CYAN}{guild_info['guild']['name']}{Fore.RESET}")
            print()

            #global_variables.ws.send(json.dumps(authsocket.obfuscateObj({"op": "science", "event": "guild_joiner", "guild_id": guild_info["guild"]["id"], "guild_name": guild_info["guild"]["name"], "invite": invite})))

            async with TaskPool(10_000) as pool:
                for token in global_variables.tokens:
                    await pool.put(api.joinGuild(invite, token, guild_info))
                    await asyncio.sleep(delay)

        print()
        token_list_scraping_token = global_variables.tokens
        if len(global_variables.joined_tokens) != 0:
            token_list_scraping_token = global_variables.joined_tokens
        scrapingToken = input(
            "SCRAPER> Scraping token? (blank to pick one from the list): ")
        if scrapingToken == "":
            scrapingToken = random.choice(token_list_scraping_token)

        # EMOJI VERIFICATOR
        if input("REACTOR> Run emoji verificator? Y/N: ").lower() == "y":
            channels = None
            selected_channel = None

            if guild_info != None:
                channels = await api.getGuildChannels(scrapingToken, guild_info["guild"]["id"])
            else:
                channels = await api.getGuildChannels(scrapingToken, input("REACTOR> Guild ID: "))

            while True:
                id = input("REACTOR> Channel ID: ")
                for channel in channels:
                    if str(channel["id"]) == id:
                        selected_channel = channel
                        break

                if selected_channel != None:
                    break
                print("REACTOR> Invalid ID! ")

            reactions = []

            channelReactions = await api.getReactions(scrapingToken, selected_channel["id"])
            # print(channelReactions)
            if len(channelReactions) != 0:
                reactions.append({"channel": {
                    "id": selected_channel["id"], "name": selected_channel["name"]}, "reactions": channelReactions})

                emojis = []
                for reaction in reactions:
                    obj = {"channel_id": reaction["channel"]["id"],
                           "channel_name": reaction["channel"]["name"], "reactions": []}
                    for reactionEmojis in reaction["reactions"]:
                        emojiList = {
                            "message_id": reactionEmojis["message"]["id"], "reactions": []}

                        for reactionEmoji in reactionEmojis["reactions"]:
                            if reactionEmoji["emoji"]["id"] == None:
                                emojiOutput = emoji.demojize(
                                    reactionEmoji["emoji"]["name"])
                            else:
                                emojiOutput = reactionEmoji["emoji"]["name"] + \
                                    ":" + reactionEmoji["emoji"]["id"]
                            emojiList["reactions"].append(emojiOutput)
                        obj["reactions"].append(emojiList)
                    obj["reactions"].reverse()
                    emojis.append(obj)

                print()
                choices = {}
                choosen = None
                i = 1

                emojis.reverse()

                for avaiableMessage in emojis:
                    for avaiableReactions in avaiableMessage["reactions"]:
                        for reaction in avaiableReactions["reactions"]:
                            print(
                                f"REACTOR> Choice #{i} {avaiableMessage['channel_name']} - messageID: {avaiableReactions['message_id']} - {reaction}")

                            choices[i] = {"channel_id": avaiableMessage["channel_id"],
                                          "message_id": avaiableReactions["message_id"], "emoji": reaction}
                            i += 1

                while True:
                    choice = input("\nREACTOR> Choice: ")
                    if choice.isdigit() and int(choice) in choices:
                        choosen = choices[int(choice)]
                        break
                    else:
                        print("REACTOR> Invalid choice.")

                if choosen["emoji"][0] == ":" and choosen["emoji"][len(choosen["emoji"]) - 1] == ":":
                    choosen["emoji"] = emoji.emojize(choosen["emoji"])

                res = await api.addReaction(scrapingToken, choosen)
                if res.status_code == 204:
                    print(
                        f"{Fore.GREEN}REACTOR> Successfully added reaction{Fore.RESET} from scraping token '{utils.getTokenId(scrapingToken)}'")
            else:
                print("REACTOR> No reactions found.")

        # SCRAPER
        print()
        loading_method = input(
            "SCRAPER> Load ID's from ids.txt? Y/N: ").lower()
        if loading_method == "y":
            with open("data/ids.txt", "r") as ids:
                ids = ids.read().split("\n")
        else:
            title_worker.WORKER_MODE = "scraper"
            if guild_info != None:
                guild_id = str(guild_info["guild"]["id"])
            else:
                guild_id = input("SCRAPER> Guild ID: ")
            channels = await api.getGuildChannels(scrapingToken, guild_id)
            print()

            choices = {}
            choosen = None
            i = 1

            for channel in channels:
                print(
                    f"SCRAPER> Choice #{i} #{channel['name']} - {channel['id']}")
                choices[i] = channel["id"]
                i += 1

            while True:
                choice = input(
                    "\nSCRAPER> Choice (either on list or channelID): ")
                if choice.isdigit() and len(str(choice)) == 18:
                    choosen = choice
                    break

                if choice.isdigit() and int(choice) in choices:
                    choosen = choices[int(choice)]
                    break
                else:
                    print("SCRAPER> Invalid choice.")

            print("SCRAPER> See title for updates.")
            ids = scrape(scrapingToken, guild_id, str(choosen))

        #ids = list(dict.fromkeys(ids))
        print(f"{Fore.GREEN}SCRAPER> {len(ids)} IDs loaded.{Fore.RESET}")
        global_variables.ids_scraped_finished = len(ids)

        # DMER
        print()
        embed_msg = None
        use_embeds = input("MASS DM> Use embeds? Y/N: ").lower()
        if use_embeds == "y":
            with open("data/embed_data.json", "r", encoding="utf-8-sig") as embed:
                embed = json.loads(embed.read())

            embed_msg = input(
                "MASS DM> Embed message? (leave empty if just the embed): ")
        else:
            msg_loading_method = input(
                "MASS DM> Load message from message.txt? Y/N: ").lower()
            if msg_loading_method == "y":
                with open("data/message.txt", "r", encoding="utf-8-sig") as msgs:
                    message = msgs.read()
            else:
                message = input("MASS DM> Message: ")

        mdm_delay = input("MASS DM> Delay? (blank if not): ")
        if mdm_delay == "":
            mdm_delay = 0
        else:
            mdm_delay = float(mdm_delay)
        title_worker.WORKER_MODE = "dmer"

        token_list = global_variables.tokens
        if len(global_variables.joined_tokens) != 0:
            token_list = global_variables.joined_tokens
        blacklisted_ids = [utils.getTokenId(token) for token in token_list] + [
            line.rstrip('\n') for line in open('data/blacklist.txt')]

        maxDms = input(
            "MASS DM> Limit DM's? (if yes input a DM count, else leave blank): ")
        if maxDms == '':
            maxDms = -1
        global_variables.successful_dm_limit = int(maxDms)

        print()

        async with TaskPool(10_000) as pool:
            for id in ids:
                if global_variables.successful_dm_limit == 0:
                    break
                if id in blacklisted_ids or id in global_variables.dmed_users: continue
                additionalData = {
                    "user_id": id
                }

                if use_embeds == "y":
                    payload = {
                        "content": utils.prepareMessage(embed_msg, additionalData),
                        "embeds": [ utils.prepareEmbed(embed, additionalData) ],
                        "nonce": utils.generateNonce()
                    }

                    await pool.put(utils.sendDm(utils.getToken(), id, payload))
                else:
                    payload = {
                        "content": utils.prepareMessage(message, additionalData), 
                        "nonce": utils.generateNonce()    
                    }
                    
                    await pool.put(utils.sendDm(utils.getToken(), id, payload))

                await asyncio.sleep(mdm_delay)

        print(
            f"\nOUTPUT> Successfully sent {str(global_variables.messages_sent)} messages and {str(global_variables.messages_failed)} failed. Checking tokens...")

        with open("data/dmed_ids.txt", "w") as f:
            f.write('\n'.join(global_variables.dmed_users))
            f.close()

        async with TaskPool(10_000) as pool:
            for token in token_list_scraping_token:
                await pool.put(api.checkToken(token))

        print(
            f"OUTPUT> Tokens checked, {global_variables.valid_tokens_count}/{len(token_list_scraping_token)} valid.")
        with open("data/tokens.txt", "w") as f:
            f.write('\n'.join(global_variables.valid_tokens))
            f.close()

        input()

    except Exception as e:
        print(
            f"{global_variables.app_data['tool_name']}> A unexpected error occured. Please report it in the {Fore.CYAN}discord server{Fore.RESET}.", e)
        return await GPUtil()


def FrozerImporter():
    global_variables.ws = create_connection("ws://91.244.197.101:6942")
    global_variables.ws.send(json.dumps(
        authsocket.obfuscateObj({"op": "app_init"})))
    global_variables.app_data = authsocket.deobfuscateObject(
        json.loads(global_variables.ws.recv()))

    title_worker.initializeWorker()

    hwid = hashlib.md5(subprocess.check_output(
        'wmic csproduct get uuid').decode().split('\n')[1].strip().encode()).hexdigest()
    utils.clearConsole()
    print(f"> HWID: {Fore.CYAN}{hwid}{Style.RESET_ALL}")
    print(
        f"> Discord Server: {Fore.CYAN}{global_variables.app_data['discord']}{Style.RESET_ALL}")
    print(
        f"> Telegram Group: {Fore.CYAN}{global_variables.app_data['telegram']}{Style.RESET_ALL}")
    print(
        f"> MOTD: {Fore.CYAN}{global_variables.app_data['motd']}{Style.RESET_ALL}")

    if float(global_variables.app_data["app_lock"]) >= global_variables.current_version:
        print(f"> {Fore.RED}WARNING: {Style.RESET_ALL}Application is currently locked for this version. Please download an update.")
        input()
        exit()

    global_variables.ws.send(json.dumps(
        authsocket.obfuscateObj({"op": "auth", "hwid": hwid})))
    auth_data = authsocket.deobfuscateObject(
        json.loads(global_variables.ws.recv()))

    if auth_data["status"] == "loggedIn":
        print(f"> {Fore.CYAN}Successfully logged in!{Style.RESET_ALL}")
        Fernet()
    else:
        print(
            f"> You are not authenticated, please create a ticket in {Fore.CYAN}discord server{Style.RESET_ALL}.")
        input()


def Fernet():
    asyncio.run(GPUtil())

if __name__ == '__main__':
    FrozerImporter()
