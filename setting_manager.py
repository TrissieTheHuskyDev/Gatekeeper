#!/usr/env/bin python3
# created by Atalanta (Atty)

import os
from collections import OrderedDict
import pickle, sys


class Secrets:
    """class to hold and edit secret file"""
    secret = {"token":""}
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
            with open(self.secret_file,"rb") as fd:
                self.secret = pickle.load(fd)
        except EOFError:
            print("Token missing or corrupt")
            self.set_secret()
                 
    def set_secret(self):
        from __init__ import bot
        help_msg = """
For help setting up and retrieving the token of a bot go to
https://discordpy.readthedocs.io/en/latest/discord.html"""
        token = ""
        token = input("Enter a token or help: ")
        if token == "help":
            print(help_msg)
            bot.loop.create_task(bot.http.close())
            sys.exit()
        else:
            self.secret["token"] = token
            with open(self.secret_file, "wb") as fd:
                pickle.dump(self.secret, fd)
            print("Secret file named {secret_file} created.".format(
                secret_file=self.secret_file))
            self.load_secret()                


class Program_Settings:
    """class to handle loading, adding, and updating settings"""
    settings = {}
   
    def __init__(self, reset=False, test_mode=False):
        """opens settings file if exists, creates otherwise"""
        if (not os.path.exists("settings")) or (reset):
            self.settings = self.default_settings(test_mode=test_mode)
            self.set_settings(self.settings)
        else:
            self.load_settings()
            
            
    def default_settings(self, settings_file="settings", test_mode=False):
        """reset settings to default values"""
        settings = {
            "setting_version": "v0.1.4",
            "db_file": r"creepydb",
            "secret_file": ".\\secret",
            "settings_file": ".\\settings",
            # settings used and saved to bot memory. These are absolutely vital to the bot's operation, don't change them unless needed.
            "bot_settings":{
                "num_messages": 5,
                "gaius": 356878329602768897,
                "logs": (627500108618924052 if not test_mode else 
                    652492330942595082),
                "guild": (539925898128785460 if not test_mode else 
                    517928216040833038),
                "whitelist": [
                    "www.youtube.com"
                    ],
                "temp_decay": 900,
                "roles": OrderedDict(
                   [["chirper"  , (539929792938770436 if 
                        not test_mode else 651519729961271309)],
                    ["chirper2" , (595248545930412042 if 
                        not test_mode else 651519766799974400)],
                    ["chirper3" , (612926101144207381 if 
                        not test_mode else 651719605965946880)],
                    ["chirper4" , (612926108723314688 if 
                        not test_mode else 651719649444233217)],
                    ["freeze"   , (627499927299424266 if 
                        not test_mode else 651719686399983626)],
                    ["youngling", (627860154276118551 if 
                        not test_mode else 651719728917774337)]],
                    ),
                "warm_responses": [
                    "is now wearing an oversized warm hoodie",
                    "is now warm and toasty",
                    "is now enjoying a cup of cocoa under the covers",
                    "is now roasting chestnuts over an open fire",
                    "is now covered in blankets",
                    "is now snuggled up with their favorite stuffy",
                    "is now snuggling their favorite pet",
                    "is now cozy by the fire",
                    "is now warm and fuzzy inside",
                ],
                "cool_responses": [
                    "is now cold and shivering", 
                    "is freezing",
                ],
                "fun_roles":{
                    "warm":       (651435846821609472 if not test_mode else 652140899597549578),
                    "cold":       (652101965014106122 if not test_mode else 652141236026605608),
                    "heatproof":  (652112606886232084 if not test_mode else 652141262891122718),
                    "burning":    (652109890206171145 if not test_mode else 652139500054642726),
                    "permafrost": (652109752465358851 if not test_mode else 652139780490002462),
                }
            }
        }
        return settings
        
    def settings_integrity(self, test_mode=False):
        """check settings to ensure they contain default settings"""
        default_settings = self.default_settings(test_mode=test_mode)
        setting_version = self.settings.get(
            "setting_version", None)
        if setting_version != default_settings["setting_version"]:
            answer = input("Settings mismatch detected, do you want to\n"
                + " reset to default (Y/N): ").lower()
            if answer.startswith("n"):
                print("Attempting to continue, errors may occur with\n"
                    +" certain commands or at unexpected times")
                return
            self.set_settings(default_settings)

    def set_settings(self, settings):
        """function to update the settings file and instance settings"""
        settings_file = settings.get("settings_file", ".\\settings")
        with open(settings_file, "wb") as fd:
            self.settings = pickle.dump(settings, fd)
        self.load_settings()
            
    def load_settings(self):
        if self.settings:
            settings_file = self.settings.get("settings_file", ".\\settings")
        else:
            settings_file = ".\\settings"
        with open(settings_file, "rb") as fd:
            self.settings = pickle.load(fd)