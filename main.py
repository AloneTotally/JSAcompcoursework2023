import geocoder
import os
import datetime

# kivy imports
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.mapview import MapView, MapMarkerPopup, MapMarker, MapSource
from kivymd.uix.button import MDRoundFlatButton, MDFillRoundFlatButton
from kivy.uix.image import Image
from kivymd.uix.snackbar import Snackbar
from kivy.app import App
# from kivy.uix.image import AsyncImage
from kivy.uix.camera import Camera

# firebase
import firebase_admin
from firebase_admin import credentials, auth, firestore

# date
import geocoder
from datetime import datetime, tzinfo
import pytz
from firebase_admin.firestore import SERVER_TIMESTAMP

cred = credentials.Certificate(
    "woah-data-firebase-adminsdk-1n466-971a25d354.json")
# intitialise the app
firebase_admin.initialize_app(cred)
# intitialise firestore
db = firestore.client()

g = geocoder.ip('me')
currentlat, currentlon = g.latlng
print(g.latlng)

USER_EMAIL = ""


class LoginScreen(Screen):

    def login(self):
        USER_EMAIL = self.ids.user_email.text
        user_name = self.ids.username.text
        user_password = self.ids.password.text
        userdata = {
            u'email': USER_EMAIL,
            u'username': user_name,
            u'password': user_password,
            u'description': ""
        }
        if USER_EMAIL == "" or user_name == "" or user_password == "":
            # Snackbar(text="One of the fields is not filled",
            #          button_text="BUTTON", button_callback=lambda: self.callback).show()
            Snackbar(text="One of the fields is not filled.").open()
            return

        try:
            # User exists
            # user = auth.get_user_by_email(USER_EMAIL)
            # print("user exists")
            # CHECK WHETHER PW CORRECT
            user_db_ref = db.collection(u'Users').document(USER_EMAIL)
            newuserdata = user_db_ref.get()
            if newuserdata.exists:
                userdata = newuserdata.to_dict()
                print(userdata)
            else:
                raise Exception("user does not exist")

        except Exception:
            print(Exception)
            # User does not have an account
            # user = auth.create_user(
            #     email=USER_EMAIL,
            #     email_verified=False,
            #     password=user_password,
            #     display_name=user_name,
            #     disabled=False
            # )
            db.collection('Users').document(USER_EMAIL).set(userdata)
            # print('Sucessfully created new user: {0}'.format(userdata.uid))
        finally:
            # Go to main page
            # storing the user in the ids part
            self.ids["user"] = userdata
            self.manager.current = "mainpage"
            self.manager.transition.direction = "left"

        # TODO: SEND REQUEST to firestore??


class AddLocationScreen_1(Screen):
    def to_addlocation2(self):
        location_coords = []
        try:
            location_coords = [
                self.ids["mapmarker"].lat,
                self.ids["mapmarker"].lon
            ]

        except Exception:
            Snackbar(text="One of the fields is not filled.").open()
        user_ans_dict = {
            "opening_time": self.ids.opening_time.text,
            "closing_time": self.ids.closing_time.text,
            "location_name": self.ids.location_name.text,
            "is_mall": self.ids.in_mall.active,
            "location_coords": location_coords
            # MOREEEEEEEE, maybe level?
        }
        if user_ans_dict["closing_time"] == "" or user_ans_dict["location_name"] == "" or user_ans_dict["opening_time"] == "":
            Snackbar(text="One of the fields is not filled.").open()
            return

        self.manager.current = "addlocation_2"
        self.manager.transition.direction = "left"

    def on_pre_enter(self):
        mapview = self.ids.addlocation_map
        mapview.on_touch_down = self.on_touch_map

    def on_touch_map(self, touch):
        bbox = self.ids.addlocation_map.get_bbox()

        # finding lat and lon on the map
        lat, lon = self.ids.addlocation_map.get_latlon_at(touch.x, touch.y)
        lat, lon = lat - 0.0003649793, lon - 0.0013741504
        if self.width < 700:
            lon += 0.0008598847
        elif self.width < 1100:
            lat -= -0.0000751428
            lon -= -0.000451037

        marker_within_mapview = bbox[0] < lat < bbox[2] and bbox[1] < lon < bbox[3]
        if not marker_within_mapview:
            return

        print("Touch down on", touch.x, touch.y)

        # TODO: works on computer sized screen but on phone is gg

        print("Tapped on", lat, lon)
        print(self.width, self.height)
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
        # TODO: REMOVE PHOTO in storage
        print(user_ans_dict)
        # db.collection(u'Locations').document()

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
        sg_tz = pytz.timezone("Singapore")

        user_ans_dict = {
            u"restaurant_name": self.ids.restaurant_name.text,
            u"Date_of_consumption": self.ids.date.text,
            u"location_coords": location_coords,
            u'localtime': datetime.now(sg_tz),
            u'servertimestamp': SERVER_TIMESTAMP

        }
        # TODO: SEND REQUEST
        print(user_ans_dict)

        # NOT FINALISED YET
        # db.collection("Users").document(USER_EMAIL).collection(
        #     "History").add(user_ans_dict)


class HistoryItemScreen(Screen):

    def click_star(self, star):
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
            u"review": self.ids.review.text,
            u"rating": self.ids["starnum"]
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
            u"username": self.ids.username_input.text,
            u"description": self.ids.description_input.text
        }
        # TODO: SEND REQUEST
        user = self.manager.get_screen('login').ids['user']
        print(user)
        profile_ref = db.collection('Users').document(user['email'])
        profile_ref.update(new_profile_dict)

    def on_pre_enter(self):
        # TODO: SEND REQUEST
        print("entered mainpage")
        user = self.manager.get_screen('login').ids['user']
        print(user)
        self.ids.username_input.text = user['username']
        self.ids.description_input.text = user['description']

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
        Builder.load_file("pages/login.kv")

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MainPage(name="mainpage"))
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

    # Close an error popup
    def callback(self, instance):
        from kivymd.toast import toast

        toast(instance.text)


if __name__ == '__main__':
    HomePage().run()
