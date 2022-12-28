from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen


class HistoryItemScreen(Screen):
    pass


class MainPage(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class HomePage(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Dark"
        return Builder.load_file("pages/homepage.kv")

    def back_homepage(self):
        self.root.current = "mainpage"
        self.root.transition.direction = "right"


if __name__ == '__main__':
    HomePage().run()
