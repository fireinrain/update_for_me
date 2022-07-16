#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Description: 
@Author  : fireinrain
@Site    : https://github.com/fireinrain
@File    : automate.py
@Software: PyCharm
@Time    : 2022/7/13 10:13 AM
"""
import sys
import time

import pyautogui

if __name__ == '__main__':
    # position = pyautogui.position()
    # print(position)
    # size = pyautogui.size()
    # print(size)
    # pyautogui.moveTo(100, 200, duration=3)
    # pyautogui_position = pyautogui.position()
    # print(pyautogui_position)

    # pyautogui.typewrite('Hello world!\n', interval=5)  # useful for entering text, newline is Enter

    pyautogui.hotkey('command', ' ')
    time.sleep(20)

    sys.exit(0)
