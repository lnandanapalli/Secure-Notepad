import sqlite3
import textwrap
import os
import sys
from kivy.app import App
from kivy.graphics import Color, Rectangle, Canvas
from kivy.properties import BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.base import EventLoop
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from cryptography.fernet import Fernet

key = Fernet.generate_key()
notedatabase = sqlite3.connect("notlar.db")
cur = notedatabase.cursor()
select_id = None


class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
    pass


class SelectableButton(RecycleDataViewBehavior, Button):
    def on_press(self):
        app = App.get_running_app()
        ScreenManager.get_screen(App.get_running_app().lokesh, "NotesScreen").ids.metin.text = self.textLong
        global select_id
        select_id = self.id
        print(self.text)
        Builder.load_file("notes.kv")


class HomeScreen(Screen):
    window_sizes = Window.size[1] / 9    
    
    def newnote(self):
        app = App.get_running_app()
        global select_id
        select_id = None
        ScreenManager.get_screen(App.get_running_app().lokesh, "NotesScreen").ids.metin.text = ""
        self.data_items = ListProperty([])

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.notes_get()

    def notes_get(self):
        self.data_items = []
        sql_command = """CREATE TABLE IF NOT EXISTS notelar(
        id integer PRIMARY KEY AUTOINCREMENT,
        note text NOT NULL
        );"""
        cur.execute(sql_command)
        cur.execute("SELECT * FROM notelar")
        allnotes = cur.fetchall()
        #self.data_items.clear()
        print(self.data_items)
        for i in allnotes:
            decrypttemp = str(i[1])
            fernetobj = Fernet.decrypt(decrypttemp)
            i1 = decrypttemp.decode()
            d = {"text": str(i1), "id": i[0]}
            self.data_items.append(d)
        print(self.data_items)
        self.ids.rv.data = [{'text': (str(x['text'])[:20] + '..') if len(str(x['text'])) > 15 else str(x['text']),
                             'id': str(x['id']), 'textLong': str(x['text'])} for x in self.data_items]
        self.ids.rv.refresh_from_data()


class NotesScreen(Screen):
    window_sizes = Window.size[1] / 5.7
    window_sizesx = Window.size[1] / 10

    def addf(self):
        print("add called")
        print(select_id)
        if select_id == None:
            note = self.ids.metin.text
            note = note.encode()
            fernetobj = Fernet(key)
            encryptednote = fernetobj.encrypt(note)
            note = [encryptednote]
            cur.execute("insert into notlar(note) values(?)", (note,))
            notedatabase.commit()
        else:
            cur.execute("update notlar set note = (?) where id = (?)", [(self.ids.metin.text), (select_id)])
            notedatabase.commit()
        ScreenManager.get_screen(App.get_running_app().lokesh, "HomeScreen").notes_get()

    def deletef(self):
        if select_id != None:
            cur.execute("delete from notlar where id = (?)", [select_id])
            notedatabase.commit()
        ScreenManager.get_screen(App.get_running_app().lokesh, "HomeScreen").notes_get()


class NotesApp(App):
    selected_text = StringProperty("")

    def build(self):
        self.lokesh = ScreenManager()
        self.lokesh.add_widget(HomeScreen(name="HomeScreen"))
        self.lokesh.add_widget(NotesScreen(name="NotesScreen"))
        from kivy.core.window import Window
        Window.clearcolor = (0.60, 0.63, 0.62, 1)
        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        return self.lokesh

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            self.lokesh.current = "HomeScreen"
            return True


if __name__ == "__main__":
    Window.clearcolor = (1, 0.5, 1, 0)
    NotesApp().run()

