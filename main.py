import os

from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.mapview import MapView, MapMarkerPopup, MapMarker, MapSource
# from kivy.uix.image import AsyncImage
from kivymd.uix.button import MDRoundFlatButton, MDFillRoundFlatButton
from kivy.uix.image import Image
from kivy.uix.camera import Camera


class AddLocationScreen_1(Screen):
    pass


class AddLocationScreen_2(Screen):

    def take_photo(self, num, *args):
        self.ids["camera"].play = False
        self.ids["camera"].export_to_png(f"./location{num}.png")
        self.ids.camerawrapper.remove_widget(
            self.ids["camera"]
        )  # remove camera widget

        location_image = Image(source=f"./location{num}.png")
        self.ids.camerawrapper.add_widget(
            location_image)  # add image widget
        self.ids["location_image"] = location_image

        # remove stuff from appwrapper
        self.ids.appwrapper.remove_widget(
            self.ids["take_photo"]
        )  # remove take_photo button

        take_photo_again = MDFillRoundFlatButton(
            text="Take photo again",
            on_press=lambda x: self.take_photo_again(num),
        )
        self.ids.appwrapper.add_widget(take_photo_again)
        self.ids["take_photo_again"] = take_photo_again

    def take_photo_again(self, num, *args):
        os.remove(f"./location{num}.png")
        self.ids.camerawrapper.remove_widget(
            self.ids["location_image"]
        )  # remove image widget

        camera = Camera(play=True, resolution=(640, 480))
        self.ids.camerawrapper.add_widget(camera)  # add camera widget
        self.ids["camera"] = camera

        # remove stuff from appwrapper
        self.ids.appwrapper.remove_widget(
            self.ids["take_photo_again"]
        )  # remove take_photo_again button
        take_photo = MDFillRoundFlatButton(
            text="Take photo",
            on_press=lambda x: self.take_photo(num+1)
        )
        self.ids.appwrapper.add_widget(take_photo)
        self.ids["take_photo"] = take_photo

    def submit_new_location(self):
        # TODO: THIS IS NOT DONE
        # there is still mapview and is_mall
        user_ans_dict = {
            "opening_time": self.root.addlocation_1.ids.opening_time,
            "closing_time": self.root.addlocation_1.ids.closing_time,
            "location_name": self.root.addlocation_1.ids.location_name,
            # MOREEEEEEEE
        }

    def on_pre_enter(self):
        self.ids.camera.play = True

    # in case user leaves page with camera still on
    def on_pre_leave(self, *args):
        self.ids.camera.play = False


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

    def on_pre_enter(self):
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
        Builder.load_file("pages/otherpages/addlocation_1.kv")
        Builder.load_file("pages/otherpages/addlocation_2.kv")

        sm = ScreenManager()
        sm.add_widget(MainPage())
        sm.add_widget(AddHistoryItemScreen(name="addhistoryitem"))
        sm.add_widget(HistoryItemScreen(name="historyitem"))
        sm.add_widget(ReviewsPage(name="reviewspage"))
        sm.add_widget(ViewLocation(name="viewlocation"))
        sm.add_widget(AddLocationScreen_1(name="addlocation_1"))
        sm.add_widget(AddLocationScreen_2(name="addlocation_2"))

        return sm

    def on_checkbox_active(self, checkbox, value):
        if value:
            print('The checkbox', checkbox, 'is active',
                  'and', checkbox.state, 'state')
        else:
            print('The checkbox', checkbox, 'is inactive',
                  'and', checkbox.state, 'state')

    # Screen transition functions

    def page_change(self, name, direction):
        self.root.current = name
        self.root.transition.direction = direction

    # The functions for going back to certain pages

    def back_homepage(self):
        self.root.current = "mainpage"
        self.root.transition.direction = "right"


if __name__ == '__main__':
    HomePage().run()
