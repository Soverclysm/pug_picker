# build.py
import PyInstaller.__main__
import os
import shutil


# Define the path to your main script
MAIN_SCRIPT = 'main.py'

PyInstaller.__main__.run([
    MAIN_SCRIPT,
    '--name=PugPicker',
    '--onedir',
    # Removed --noconsole to see error messages
    '--add-data=src/bot/__init__.py;src/bot',
    '--add-data=src/bot/queue.py;src/bot',
    '--add-data=src/bot/twitch_bot.py;src/bot',
    '--add-data=src/config/__init__.py;src/config',
    '--add-data=src/config/config.ini;src/config',
    '--add-data=src/config/settings.py;src/config',
    '--add-data=src/__init__.py;src',
    '--hidden-import=src.bot.queue',
    '--hidden-import=src.bot.twitch_bot',
    '--hidden-import=src.config.settings',
    '--clean'
])