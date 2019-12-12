#!/usr/env/bin python3
# created by Atalanta (Atty)

from collections import OrderedDict
import os, pickle, sys

from discord.ext import commands




class Program_Settings:
    """class to handle loading, adding, and updating settings"""
    settings = {}

    def __init__(self, reset=False, test_mode=False):
        """opens settings file if exists, creates otherwise"""
        self.reset = reset
        self.test_mode = test_mode
        if (not os.path.exists("settings")) or (self.reset == True):
            self.settings = self.default_settings()
            self.set_settings(self.settings)
        else:
            self.load_settings()


    def default_settings(self, settings_file="settings"):
        """reset settings to default values"""
        test_mode = self.test_mode
        settings = {
            "setting_version": "0.1.5a",
            "db_file": "creepydb",
            "secret_file": "secret.json",
            "settings_file": "settings",
            "test_mode":self.test_mode,
            "reset":self.reset,
            # settings used and saved to bot memory. 
            # These are absolutely vital to the bot's operation, 
            # don't change them unless needed.
            "bot_settings":{
                "voters": 5,
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
                "ignore_errors": (
                    commands.errors.MissingPermissions,
                    commands.CheckFailure,
                    commands.CommandNotFound,
                    commands.MissingRole,
                    commands.NoPrivateMessage
                ),
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

    def settings_integrity(self):
        """check settings to ensure they contain default settings"""
        default_settings = self.default_settings()
        self.load_settings()
        setting_version = self.settings.get(
            "setting_version", None)
        if (setting_version != default_settings["setting_version"]):
            answer = input("Settings mismatch detected, do you want to\n"
                + " obtain missing default values (Y/N): ").lower()
            if answer.startswith("n"):
                print("Attempting to continue, errors may occur with\n"
                    +" certain commands or at unexpected times")
                return
            for setting_key, setting_val in self.settings.items():
                if setting_key != "setting_version":
                    default_settings[setting_key] = setting_val
            self.set_settings(default_settings)

    def set_settings(self, settings):
        """function to update the settings file and instance settings"""
        settings_file = settings.get(
            "settings_file", "settings")
        self.settings = settings
        with open(settings_file, "wb") as fd:
            pickle.dump(settings, fd)
        self.load_settings()

    def load_settings(self):
        if self.settings:
            settings_file = self.settings.get(
                "settings_file", "settings")
        else:
            settings_file = "settings"
        with open(settings_file, "rb") as fd:
            self.settings = pickle.load(fd)