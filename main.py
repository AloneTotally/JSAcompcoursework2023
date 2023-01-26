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
    def on_pre_enter(self):
        mapview = self.ids.addlocation_map
        mapview.on_touch_down = self.on_touch_map

    def on_touch_map(self, touch):
        # finding lat and lon on the map
        print("Touch down on", touch.x, touch.y)
        lat, lon = self.ids.addlocation_map.get_latlon_at(touch.x, touch.y)
        # TODO: works on computer sized screen but on phone is gg
        print("Tapped on", lat, lon)
        print(self.width, self.height)
        lat, lon = lat - 0.0003649793, lon - 0.0013741504
        if self.width < 700:
            lon += 0.0008598847
        elif self.width < 1100:
            lat -= -0.0000751428
            lon -= -0.000451037

            # putting the mapmarker
        marker = MapMarker(lat=lat, lon=lon)
        if self.ids.get("mapmarker") == None:
            self.ids.addlocation_map.add_marker(marker)
            self.ids["mapmarker"] = marker
        else:
            self.ids.addlocation_map.remove_widget(
                self.ids["mapmarker"]
            )
            self.ids.addlocation_map.add_marker(marker)
            self.ids["mapmarker"] = marker


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
        # pass
        # TODO: THIS IS NOT DONE
        # there is still mapview and is_mall
        addlocation_1_ref = self.manager.get_screen("addlocation_1")

        location_coords = (
            addlocation_1_ref.ids["mapmarker"].lat,
            addlocation_1_ref.ids["mapmarker"].lon
        )
        user_ans_dict = {
            "opening_time": addlocation_1_ref.ids.opening_time.text,
            "closing_time": addlocation_1_ref.ids.closing_time.text,
            "location_name": addlocation_1_ref.ids.location_name.text,
            "is_mall": addlocation_1_ref.ids.in_mall.active,
            "location_coords": location_coords
            # MOREEEEEEEE, maybe level?
        }
        # TODO: SEND REQUEST
        print(user_ans_dict)

    def on_pre_enter(self):
        self.ids.camera.play = True

    # in case user leaves page with camera still on
    def on_pre_leave(self, *args):
        self.ids.camera.play = False


class AddHistoryItemScreen(Screen):
    def on_pre_enter(self):
        mapview = self.ids.addhistoryitem_map
        mapview.on_touch_down = self.on_touch_map

    def on_touch_map(self, touch):
        # finding lat and lon on the map
        print("Touch down on", touch.x, touch.y)
        lat, lon = self.ids.addhistoryitem_map.get_latlon_at(touch.x, touch.y)
        # TODO: works on computer sized screen but on phone is gg
        print("Tapped on", lat, lon)
        print(self.width, self.height)
        lat, lon = lat - 0.0002737344, lon - 0.000263021
        if self.width < 650:
            lat -= 0.0000053673
            lon += 0.0001235686

            # putting the mapmarker
        marker = MapMarker(lat=lat, lon=lon)
        if self.ids.get("mapmarker") == None:
            self.ids.addhistoryitem_map.add_marker(marker)
            self.ids["mapmarker"] = marker
        else:
            self.ids.addhistoryitem_map.remove_widget(
                self.ids["mapmarker"]
            )
            self.ids.addhistoryitem_map.add_marker(marker)
            self.ids["mapmarker"] = marker

    def submit_history_item(self):
        location_coords = (
            self.ids["mapmarker"].lat,
            self.ids["mapmarker"].lon
        )

        user_ans_dict = {
            "restaurant_name": self.ids.restaurant_name.text,
            "Date_of_consumption": self.ids.date.text,
            "location_coords": location_coords
        }
        # TODO: SEND REQUEST
        print(user_ans_dict)


class HistoryItemScreen(Screen):

    def click_star(self, star):
        temp = 0
        if star == 1:
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#d6d6d6"
            self.ids.star_three.text_color = "#d6d6d6"
            self.ids.star_four.text_color = "#d6d6d6"
            self.ids.star_five.text_color = "#d6d6d6"
        if star == 2:
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#f6ae00"
            self.ids.star_three.text_color = "#d6d6d6"
            self.ids.star_four.text_color = "#d6d6d6"
            self.ids.star_five.text_color = "#d6d6d6"
        if star == 3:
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#f6ae00"
            self.ids.star_three.text_color = "#f6ae00"
            self.ids.star_four.text_color = "#d6d6d6"
            self.ids.star_five.text_color = "#d6d6d6"
        if star == 4:
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#f6ae00"
            self.ids.star_three.text_color = "#f6ae00"
            self.ids.star_four.text_color = "#f6ae00"
        if star == 5:
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#f6ae00"
            self.ids.star_three.text_color = "#f6ae00"
            self.ids.star_four.text_color = "#f6ae00"
            self.ids.star_five.text_color = "#f6ae00"
            self.ids.star_five.text_color = "#f6ae00"

        # using ids to store a number
        self.ids["starnum"] = star

    def submit_review(self):
        user_review_dict = {
            "review": self.ids.review.text,
            "rating": self.ids["starnum"]
        }
        # TODO: SEND REQUEST
        print(user_review_dict)


class ViewLocation(Screen):
    pass


class ReviewsPage(Screen):
    pass


class MainPage(Screen):
    def view_location(self):
        print("view_location has been run")
        self.manager.current = "viewlocation"
        self.manager.transition.direction = "left"

    def update_profile(self):
        new_profile_dict = {
            "username": self.ids.username_input,
            "description": self.ids.description_input
        }
        # TODO: SEND REQUEST

    def on_pre_enter(self):
        # TODO: SEND REQUEST
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
        print(value, checkbox.state)
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
