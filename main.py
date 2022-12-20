from kivymd.app import MDApp
from kivy.lang.builder import Builder

class HomePage(MDApp):
    def build(self):
        return Builder.load_file("homepage.kv")


if __name__ == '__main__':
    HomePage().run()
