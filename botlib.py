import cv2
import pyautogui
import numpy as np
import time
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from pynput import keyboard, mouse
import random



class GameOverlay(QWidget):
    def __init__(self,matchesprovider):
        super().__init__()
        self.matchesprovider = matchesprovider
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.botlib = botlib()
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        self.setGeometry(0, 0, screen_width, screen_height)  # Set the overlay size to match the screen
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a transparent background
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.drawRect(self.rect())
        outline_color = Qt.red
        painter.setPen(QColor(outline_color))
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        for match in self.matchesprovider():
            painter.drawRect(match.x, match.y, match.w, match.h)
 
class Match():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

import keyboard
class botlib():
    def click(self):
        pyautogui.click()

    def set_hotkey(self,hotkey_string,func):
        keyboard.add_hotkey(hotkey_string, func)

    def listen_key(self,key_string,func):
        keyboard.on_press(lambda event: func() if event.name == key_string else None)
        keyboard.wait()


 

    def add_listener_to_mouse_event(self,clickfunc,key):
        def subcheck(x, y, button, pressed):
            if button == key and pressed:
                clickfunc()
        with mouse.Listener(on_click=subcheck) as listener:
            listener.join()

    def send_key(self,key_string):
        pyautogui.typewrite(key_string)

    def send_hotkey(self,*params):
        pyautogui.hotkey(*params)

    def is_key_pressed(self,key_string):
        return keyboard.is_pressed(key_string)
    
    def show_coordinate(self):
        pyautogui.displayMousePosition()

    def draw_on_screen(self,matchesprovider):
        app = QApplication(sys.argv)
        overlay = GameOverlay(matchesprovider=matchesprovider)

        timer = QTimer()
        timer.timeout.connect(overlay.update)
        timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)

        sys.exit(app.exec_())

    def on_press(self,key):
        try:
            print(f'Klavye tuşuna basıldı: {key.char}')
        except AttributeError:
            print(f'Özel klavye tuşuna basıldı: {key}')

    # Klavye olaylarını dinlemek için bir geri çağırma (callback) işlevi
    def on_click(self,x, y, button, pressed):
        if pressed:
            print(f'Fareye {button} tıklanıldı ({x}, {y})')

    def start_listening_mouse_and_keyboard(self):
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        mouse_listener = mouse.Listener(on_click=self.on_click)

        # Dinleyicileri başlat
        keyboard_listener.start()
        mouse_listener.start()

        # Dinleyicilerin çalışmaya devam etmesini sağla
        keyboard_listener.join()
        mouse_listener.join()


    def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        screenshot_as_np = np.array(screenshot)
        return screenshot_as_np


    def get_matchlist(self,entity,search_in, threshold=0.8):
        img_gray = cv2.cvtColor(search_in, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(entity, cv2.IMREAD_GRAYSCALE)
        w, h = template.shape[::-1]
        
        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
        loc = np.where( res >= threshold)
        matchlist = []
        for pt in zip(*loc[::-1]):
            matchlist.append(Match(pt[0],pt[1],w,h))
        return matchlist    
            
        
    
    def visualize_matches(self,match_list,image,color=(255,0,0), thickness=1):
        for match in match_list:
            image = cv2.rectangle(image, (match.x, match.y), (match.x + match.w, match.y + match.h), color, thickness)
        return image
    
    def cv2_showimage(self,image):
        cv2.imshow('image',image)
        cv2.waitKey(0)

    def bgr2rgb(self,image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    def rgb2bgr(self,image):
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    def save_image(self,image, image_name="image.png"):
        cv2.imwrite(image_name,image)


    def video_show(self,pict_provider):
        while True:
            photo_to_show = pict_provider()
            frame = np.array(photo_to_show)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            original_height, original_width = frame.shape[:2]

            new_width = int(original_width // 1.6)
            new_height = int(original_height // 1.6)

            resized_image = cv2.resize(frame, (new_width, new_height))

            cv2.imshow("Screen Capture", resized_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    def save_screenshot(self,photo_name="screenshot.png"):
        pyautogui.screenshot().save(photo_name)

    def random_delay(self,start=0,end=1):
        random_delay = random.uniform(start,end)
        time.sleep(random_delay)

    def find_in_region(self,entity_photo, region, threshold=0.8):
        data = pyautogui.locateOnScreen(entity_photo,grayscale=True,confidence=threshold,region=region)
        if data is not None:
            datum = Match()
            datum.x = data.left
            datum.y = data.top
            datum.w = data.width
            datum.h = data.height
            return datum
        return None

    def pixel_match(self,color,pixel_x, pixel_y):
        return pyautogui.pixelMatchesColor(pixel_x,pixel_y,color)

    def pixel_match_in_region(self,color,region):
        for x in range(region[0],region[2]):
            for y in range(region[1],region[3]):
                if pyautogui.pixelMatchesColor(x,y,color):
                    return True
    

    

from pymem import Pymem
from pymem.ptypes import RemotePointer

class botlib_memoryops():
    def __init__(self,application_id):
        self.pm = Pymem(application_id)

    def read_from_memory(self,address):
        self.pm.read_int(address)

    def calculate_with_offsets(self,base, offsets):
        remote_pointer = RemotePointer(self.pm.process_handle, base)
        for offset in offsets:
            if offset != offsets[-1]:
                remote_pointer = RemotePointer(self.pm.process_handle, remote_pointer.value + offset)
            else:
                return remote_pointer.value + offset
        


bot = botlib()
# bot.start_listening_mouse_and_keyboard()
def fnc():
    bot.send_hotkey("ctrl","g")

bot.add_listener_to_mouse_event(fnc,mouse.Button.x1)



# bot.listen_key("x1", lambda: print("x1 pressed"))

# print(bot.find_image(entity = "test_seek.jpg",search_in="test_photo_basic.jpg"))
# matches = [Match(0,0,20,30),Match(0,0,40,50)] 

# # bot.save_image(bot.visualize_matches(matches))

# def pict_provider():
#     return bot.visualize_matches(matches,bot.take_screenshot())

# bot.save_image(bot.bgr2rgb(bot.take_screenshot()),"sex.png")

# bot.save_screenshot("abc.png")

# def pict_provider_2():
#     ss = bot.take_screenshot()
#     return bot.visualize_matches(bot.get_matchlist(entity="test_seek.jpg",search_in=ss),image=ss)

# bot.video_show(pict_provider_2)

# def matchesprovider():
#     return bot.get_matchlist(entity="test_seek.jpg",search_in=bot.take_screenshot())

# bot.draw_on_screen(matchesprovider=matchesprovider)