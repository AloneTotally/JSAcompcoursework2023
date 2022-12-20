from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.widget import Widget

Builder.load_file("homepage.kv")


class MyLayout(Widget):
    pass


class HomePage(MDApp):
    def build(self):
        return MyLayout()


if __name__ == "main":
    HomePage().run()
