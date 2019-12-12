#!/usr/bin/python3
# create, store, retrieve, and edit secret file

import copy
import json
import os
import sys


class Secrets:
    """class to hold and edit secret file"""
    secret = {
        "token":"",
        "time": 0
    }
    secret_file=r""
    def __init__(self, secret_file):
        """
            Loads token, and other things from the secret file
        """
        from __init__ import bot
        token = ""
        self.secret_file = secret_file
        if not os.path.exists(secret_file):
            answer = input("Secret file does not exist, and is required,\n"
                +"Create create secret_file now? (Y/N): ").lower()
            if (answer.startswith('y')):
                #create new secret file
                self.set_secret()
            else:
                print("A secret file is required if one does not exist")
                bot.loop.create_task(bot.http.close())
                sys.exit()
        else:
            self.load_secret()

    def load_secret(self):
        try:
            with open(self.secret_file,"r") as fd:
                self.secret = json.load(fd)
        except EOFError:
            print("Token missing or corrupt")
            self.set_secret()

    def set_secret(self):
        from __init__ import bot
        help_msg = """
For help setting up and retrieving the token of a bot go to
https://discordpy.readthedocs.io/en/latest/discord.html"""
        token = ""
        time = ""
        token = input("Enter a token or help: ")
        try:
            time = input("Enter time until youngling removed (days): ")
            time = int(time)
        except:
            print("invalid entry for days ({})".format(time))
            sys.exit()
        if token == "help":
            print(help_msg)
            bot.loop.create_task(bot.http.close())
            sys.exit()
        else:
            self.secret["token"] = token
            self.secret["time"] = time
            with open(self.secret_file, "w") as fd:
                json.dump(self.secret, fd)
            print("Secret file named {secret_file} created.".format(
                secret_file=self.secret_file))
            self.load_secret()