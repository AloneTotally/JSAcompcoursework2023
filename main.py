from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.mapview import MapView, MapMarkerPopup, MapMarker, MapSource
# from kivy.uix.image import AsyncImage
from kivymd.uix.button import MDRoundFlatButton


class HistoryItemScreen(Screen):
    pass


class ViewLocation(Screen):
    pass


class ReviewsPage(Screen):
    pass


class MainPage(Screen):
    def view_location(self):
        print("view_location has been run")
        self.manager.current = "viewlocation"
        self.manager.transition.direction = "left"

    def map_load(self):
        print("map_load has been run")
        self.ids.main_map.center_on(1.3784949677817633, 103.76313504803471)
        marker = MapMarkerPopup(lat=1.3784949677817633, lon=103.76313504803471)
        marker.add_widget(
            MDRoundFlatButton(
                text="python button",
                md_bg_color=[0.24705882352941178,
                             0.3176470588235294, 0.7098039215686275, 1.0],
                text_color=[1, 1, 1, 1],
                on_press=lambda x: self.view_location()
            )
        )
        self.ids.main_map.add_widget(marker)


class WindowManager(ScreenManager):
    pass


class HomePage(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Dark"
        my_app = Builder.load_file("pages/homepage.kv")
        return my_app

    def to_history_item(self):
        self.root.current = "historyitem"
        self.root.transition.direction = "left"

    def back_homepage(self):
        self.root.current = "mainpage"
        self.root.transition.direction = "right"

    def back_view_location(self):
        self.root.current = "viewlocation"
        self.root.transition.direction = "right"

    def to_reviews_page(self):
        self.root.current = "reviewspage"
        self.root.transition.direction = "left"


if __name__ == '__main__':
    HomePage().run()
