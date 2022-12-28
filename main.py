from kivymd.app import MDApp
from kivy.lang.builder import Builder


class HomePage(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Dark"
        return Builder.load_file("pages/homepage.kv")


if __name__ == '__main__':
    HomePage().run()
