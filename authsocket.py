from hashlib import sha256
from sys import exit
import time

BUILD_FOR = "BETA"
XOR_KEY = 71


def calculateChecksum(j, secret):
    str_to_hash = ("".join([i + str(j[i])
                   for i in sorted(j)]) + secret).encode()
    hashed = sha256(str_to_hash).hexdigest()
    return hashed


def validateChecksum(j, secret):
    client_sig = j["signature"]
    del j["signature"]
    server_sig = calculateChecksum(j, secret)
    return client_sig == server_sig


def validateTimestamp(j):
    return (time.time() - 30 <= float(j["timestamp"]) <= time.time() + 30)


def deobfuscateObject(j):
    deobfuscated = {}

    for char in j:
        decoded = bytes(char, encoding="utf8").decode('unicode-escape')
        deobfuscated[unXorify(decoded)] = unXorify(
            bytes(j[char], encoding="utf8").decode('unicode-escape'))

    if validateChecksum(deobfuscated, "ClipsOntop") == False:
        exit(1)

    if validateTimestamp(deobfuscated) == False:
        exit(1)

    return deobfuscated


def obfuscateObj(obj):
    newObj = {}
    obj["builtFor"] = BUILD_FOR
    obj["timestamp"] = str(time.time())

    for char in obj:
        newObj[toHex(char)] = toHex(obj[char])

    newObj[toHex("signature")] = toHex(calculateChecksum(obj, "ClipsOntop"))
    return newObj


def unXorify(string):
    out = ""

    for char in string:
        out += chr(ord(char) ^ XOR_KEY)

    return out


def toHex(string):
    hex = "0123456789ABCDEF"
    out = ""

    for char in string:
        c = chr(ord(char) ^ XOR_KEY)
        out += "\\u00"
        out += hex[ord(c) >> 4]
        out += hex[ord(c) & 0xF]

    return out
