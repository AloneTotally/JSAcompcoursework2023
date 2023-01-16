from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.mapview import MapView, MapMarkerPopup, MapMarker, MapSource
# from kivy.uix.image import AsyncImage
from kivymd.uix.button import MDRoundFlatButton


class AddHistoryItemScreen(Screen):
    pass


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
        self.ids.main_map.center_on(1.3784949677817633, 103.76313504803471)
        marker = MapMarkerPopup(
            lat=1.3784949677817633, lon=103.76313504803471)
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


# class WindowManager(ScreenManager):
#     pass


class HomePage(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Dark"

        # load the kv files
        # This the main kv file
        Builder.load_file("pages/mainpage.kv")

        # These are the other pages which the main pages lead to
        Builder.load_file("pages/otherpages/historyitem.kv")
        Builder.load_file("pages/otherpages/addhistoryitem.kv")
        Builder.load_file("pages/otherpages/reviews.kv")
        Builder.load_file("pages/otherpages/viewlocation.kv")

        sm = ScreenManager()
        sm.add_widget(MainPage())
        sm.add_widget(AddHistoryItemScreen(name="addhistoryitem"))
        sm.add_widget(HistoryItemScreen(name="historyitem"))
        sm.add_widget(ViewLocation(name="viewlocation"))
        sm.add_widget(ReviewsPage(name="reviewspage"))
        return sm

    def on_checkbox_active(self, checkbox, value):
        if value:
            print('The checkbox', checkbox, 'is active',
                  'and', checkbox.state, 'state')
        else:
            print('The checkbox', checkbox, 'is inactive',
                  'and', checkbox.state, 'state')

    # Screen transition functions

    def to_history_item(self):
        self.root.current = "historyitem"
        self.root.transition.direction = "left"

    def to_add_history_item(self):
        self.root.current = "addhistoryitem"
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
