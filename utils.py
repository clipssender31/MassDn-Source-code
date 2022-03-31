from itertools import cycle
import os
from base64 import b64decode as b64d
import api
import random
import string
from httpx import AsyncClient
import spintax
from itertools import cycle
import global_variables
import time
import threading
from colorama import Fore, Style, Back

token_pool = None


def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)


def getTokenId(token):
    try:
        return b64d(token.split('.')[0].encode()).decode()
    except:
        return "0" * 18


proxies = [line.rstrip('\n') for line in open("data/proxies.txt", 'r')]
proxy_pool = cycle(proxies)


def getProxy():
    if len(proxies) == 0:
        return None

    proxy = next(proxy_pool)
    if len(proxy.split(':')) == 4:
        splitted = proxy.split(':')
        proxy = f"{splitted[2]}:{splitted[3]}@{splitted[0]}:{splitted[1]}"

    return {'https://': 'http://' + proxy}


def generateNonce():
    return "".join(random.choice(string.digits) for i in range(18))


def prepareMessage(message, additionalData):
    if message == "": return ""

    msg = spintax.spin(message)
    msg = msg.replace("@user", f"<@{additionalData['user_id']}>")
    msg = msg.replace("\\n", "\n")

    return msg


def prepareEmbed(embed, additionalData):
    if 'title' in embed:
        embed['title'] = prepareMessage(embed['title'], additionalData)

    if 'description' in embed:
        embed['description'] = prepareMessage(
            embed['description'], additionalData)

    if 'footer' in embed:
        embed['footer']['text'] = prepareMessage(
            embed['footer']['text'], additionalData)

    if 'fields' in embed:
        for index, element in enumerate(embed['fields']):
            if 'name' in element:
                embed['fields'][index]['name'] = prepareMessage(
                    element['name'], additionalData)

            if 'value' in element:
                embed['fields'][index]['value'] = prepareMessage(
                    element['value'], additionalData)

    return embed


def getToken():
    global token_pool

    if token_pool == None:
        if len(global_variables.joined_tokens) == 0:
            token_pool = cycle(global_variables.tokens)
        else:
            token_pool = cycle(global_variables.joined_tokens)

    while True:
        choosen_token = next(token_pool)
        if choosen_token in global_variables.quarantined_tokens:
            continue
        if choosen_token in global_variables.blacklisted_tokens:
            continue
        return choosen_token


def removeFromQuarantine(token):
    time.sleep(10 * 60)
    global_variables.quarantined_tokens.remove(token)


def returnApproxCount(offlineMembers, onlineMembers):
    if offlineMembers <= 1000:
        return offlineMembers
    else:
        return onlineMembers


async def sendDm(token, userId, payload, try_count=0, error=""):
    async with AsyncClient(proxies=getProxy()) as session:
        if try_count == 4:
            print(f"{Fore.RED}MASS DM> Failed to send DM{Style.RESET_ALL}, error: {error}")
            global_variables.messages_failed += 1
            return

        chatId = await api.getChatId(session, token, userId)
        if chatId == None:
            return await sendDm(getToken(), userId, payload, try_count + 1)

        res = await api.sendMessage(session, token, chatId, payload)

        try:
            if 'content' in res.text:
                print(
                    f"{Fore.GREEN}MASS DM> Sent a message{Fore.RESET} from '{getTokenId(token)}' to '{userId}' (messageID: '{res.json()['id']}')")
                global_variables.messages_sent += 1
                global_variables.successful_dm_limit += -1
                global_variables.dmed_users.append(userId)

            elif 'You need to verify your account in order to perform this action.' in res.text or '401: Unauthorized' in res.text:
                print(
                    f"{Fore.RED}MASS DM> Token '{getTokenId(token)}' is locked.{Fore.RESET} Retrying...")
                global_variables.blacklisted_tokens.append(token)
                return await sendDm(getToken(), userId, payload, try_count + 1, "token is locked")

            elif 'Cannot send messages to this user' in res.text:
                print(
                    f"{Fore.RED}MASS DM> User '{userId}' has closed DM's.{Fore.RESET} Skipping...")
                global_variables.messages_failed += 1
                return

            elif 'You are opening direct messages too fast.' in res.text:
                print(
                    f"{Fore.RED}MASS DM> Token opened too many DM's{Fore.RESET}, quarantined token '{getTokenId(token)}'")
                global_variables.quarantined_tokens.append(token)
                threading.Thread(target=removeFromQuarantine,
                                 args=(token,)).start()
                return await sendDm(getToken(), userId, payload, try_count + 1, "quarantined token")

            elif 'Channel verification level is too high' in res.text:
                print(f"{Fore.RED}MASS DM> Token is not fully verified{Fore.RESET}, blacklisted token '{getTokenId(token)}'")
                global_variables.blacklisted_tokens.append(token)
                return await sendDm(getToken(), userId, payload, try_count + 1, "blacklisted token")

            else:
                print(
                    f"{Fore.RED}MASS DM> An unrecognised error occured.{Fore.RESET} {res.text}")
                global_variables.messages_failed += 1
                return

        except Exception as e:
            return await sendDm(getToken(), userId, payload, try_count + 1, str(e))

def areEqual(arr1, arr2, n, m):
    if (n != m):
        return False
 
    arr1.sort()
    arr2.sort()
 
    for i in range(0, n - 1):
        if (arr1[i] != arr2[i]):
            print("fail")
            return False
 
    return True