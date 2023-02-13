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
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.pickers import MDTimePicker
from kivymd.uix.list import TwoLineAvatarIconListItem

# from kivy.uix.image import AsyncImage
from kivy.uix.camera import Camera

# firebase
import firebase_admin
from firebase_admin import credentials, storage, firestore

# date
import geocoder
from datetime import datetime, tzinfo
import pytz
from firebase_admin.firestore import SERVER_TIMESTAMP

cred = credentials.Certificate(
    "foodie-804d6-firebase-adminsdk-b0buj-0424ea77a6.json")
# intitialise the app
firebase_admin.initialize_app(cred, {
    'storageBucket': "foodie-804d6.appspot.com",
})
# intitialise firestore
db = firestore.client()

g = geocoder.ip('me')
currentlat, currentlon = g.latlng
print(g.latlng)

USER_EMAIL = ""
photo_path = f""
history_data = {}
history_items = []
location_data = {}


class LoginScreen(Screen):

    def login(self):
        global USER_EMAIL
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
        password_correct = True

        try:
            # User exists
            # user = auth.get_user_by_email(USER_EMAIL)
            # print("user exists")
            # CHECK WHETHER PW CORRECT
            user_db_ref = db.collection(u'Users').document(USER_EMAIL)
            newuserdata = user_db_ref.get()
            if newuserdata.exists:
                if userdata['password'] != newuserdata.to_dict()['password']:
                    Snackbar(text="Password incorrect.").open()
                    password_correct = False
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
            if not password_correct:
                return
            self.ids["user"] = userdata
            self.manager.current = "mainpage"
            self.manager.transition.direction = "left"
        # TODO: SEND REQUEST to firestore??


class AddLocationScreen_1(Screen):
    def show_closing_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_closing_time)
        time_dialog.open()

    def show_opening_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_opening_time)
        time_dialog.open()

    def get_opening_time(self, instance, time):
        self.ids.opening_time.text = str(time)

    def get_closing_time(self, instance, time):
        self.ids.closing_time.text = str(time)

    def to_addlocation2(self):
        location_coords = []
        try:
            location_coords = [
                self.ids["mapmarker"].lat,
                self.ids["mapmarker"].lon
            ]

        except Exception:
            Snackbar(text="Location not selected.").open()
            return
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
        mapview.lat = currentlat
        mapview.lon = currentlon
        mapview.on_touch_down = self.on_touch_map

    def on_touch_map(self, touch):
        bbox = self.ids.addlocation_map.get_bbox()
        print(bbox)

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
        global photo_path
        self.ids["camera"].play = False
        self.ids["camera"].export_to_png(f"./location{num}.png")
        self.ids.camerawrapper.remove_widget(
            self.ids["camera"]
        )  # remove camera widget
        photo_path = f"./location{num}.png"
        print(photo_path)
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
        if self.ids.location_description.text == "":
            Snackbar(text="No description provided.").open()
            return

        if photo_path == "":
            Snackbar(text="No picture is uploaded.").open()
            return
        print('submit_new_location ran')

        # TODO: THIS IS NOT DONE
        # there is still mapview and is_mall
        addlocation_1_ref = self.manager.get_screen("addlocation_1")
        location_coords = [
            str(addlocation_1_ref.ids["mapmarker"].lat),
            str(addlocation_1_ref.ids["mapmarker"].lon)
        ]

        bucket = storage.bucket()  # storage bucket
        name = f"{addlocation_1_ref.ids.location_name.text} ({','.join(location_coords)})"
        blob = bucket.blob(name)
        blob.upload_from_filename(photo_path)

        blob.make_public()
        url = blob.public_url
        print(url)

        os.remove(photo_path)

        # finding midpoint in chunk
        location_coords[0] = float(location_coords[0])
        location_coords[1] = float(location_coords[1])

        lat = round(int(location_coords[0] * 50) / 50 + 0.01, 2)
        lon = round(int(location_coords[1] * 50) / 50 + 0.01, 2)
        chunk = (lat, lon)
        print(self.ids.location_description.text)
        user_ans_dict = {
            "opening_time": addlocation_1_ref.ids.opening_time.text,
            "closing_time": addlocation_1_ref.ids.closing_time.text,
            "location_name": addlocation_1_ref.ids.location_name.text,
            "is_mall": addlocation_1_ref.ids.in_mall.active,
            "location_coords": location_coords,
            "description": self.ids.location_description.text,
            "photoURL": url,
            "chunk": chunk,
            "1starcount": 0,
            "2starcount": 0,
            "3starcount": 0,
            "4starcount": 0,
            "5starcount": 0,
            # "chunk": chunk
            # MOREEEEEEEE, maybe level?
        }
        chunk_ref = db.collection(u'Chunks').document(str(chunk))
        chunk_ref.set({"chunk": chunk})
        # Setting the document
        location_ref = db.collection(u'Chunks').document(str(chunk)).collection(
            u'Locations').document(user_ans_dict["location_name"])
        location_ref.set(user_ans_dict)
        print("Document set!")

        print(user_ans_dict)
        # db.collection(u'Chunks').document(name).set(user_ans_dict)
        print("location set!")
        self.manager.current = 'mainpage'
        self.manager.transition.direction = 'right'

    def on_pre_enter(self):
        self.ids.camera.play = True

    # in case user leaves page with camera still on
    def on_pre_leave(self, *args):
        self.ids.camera.play = False


class AddHistoryItemScreen(Screen):
    def on_pre_enter(self):
        mapview = self.ids.addhistoryitem_map
        mapview.on_touch_down = self.on_touch_map

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        self.ids.date_input.text = str(value)
        print(value)

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_time)
        time_dialog.open()

    def get_time(self, instance, time):
        self.ids.time_input.text = str(time)

    def on_touch_map(self, touch):
        bbox = self.ids.addhistoryitem_map.get_bbox()

        # finding lat and lon on the map
        lat, lon = self.ids.addhistoryitem_map.get_latlon_at(touch.x, touch.y)
        lat, lon = lat - 0.0002737344, lon - 0.000263021
        if self.width < 650:
            lat -= 0.0000053673
            lon += 0.0001235686

        # TODO: works on computer sized screen but on phone is gg
        marker_within_mapview = bbox[0] < lat < bbox[2] and bbox[1] < lon < bbox[3]
        if not marker_within_mapview:
            return
        print("Tapped on", lat, lon)
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
        location_coords = []
        try:
            location_coords = [
                self.ids["mapmarker"].lat,
                self.ids["mapmarker"].lon
            ]
        except Exception:
            Snackbar(text="Location not selected.").open()
            return
        # sg_tz = pytz.timezone("Singapore")
        # current_time = datetime.now(sg_tz)
        date_time = self.ids.date_input.text + "," + self.ids.time_input.text
        user_ans_dict = {
            'restaurant_name': self.ids.restaurant_name.text,
            # 'Date_of_consumption': self.ids.date.text,
            'location_coords': location_coords,
            'date': self.ids.date_input.text,
            'time': self.ids.time_input.text,
            'servertimestamp': SERVER_TIMESTAMP
        }
        if user_ans_dict['restaurant_name'] == "" or user_ans_dict['date'] == "" or user_ans_dict['time'] == "":
            Snackbar(text="One of the fields is not filled.").open()
            return
        # TODO: SEND REQUEST
        print(user_ans_dict)

        # NOT FINALISED YET
        historyitem_ref = db.collection(u"Users").document(
            USER_EMAIL).collection(u"History").document(date_time)
        print(historyitem_ref)
        print(USER_EMAIL, date_time)
        historyitem_ref.set(user_ans_dict)


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

    def on_enter(self, *args):
        global history_data
        print("Entered historyitem: ", history_data)
        self.ids.location_name.text = history_data['restaurant_name']
        self.ids.location_name_review.text = history_data['restaurant_name']
        self.ids.eaten_time.text = "Eaten at: " + str(history_data['time'])
        self.ids.historyitem_map.lat = currentlat
        self.ids.historyitem_map.lon = currentlon
        # TODO: SET BBOX
        marker = MapMarkerPopup(
            lat=history_data['location_coords'][0], lon=history_data['location_coords'][1])
        self.ids.historyitem_map.add_widget(marker)
        # self.ids.num_reviews = "Reviews"

        # self.ids.history_map.

    def submit_review(self):
        user_review_dict = {
            u"review": self.ids.review.text,
            u"rating": self.ids["starnum"]
        }
        # TODO: SEND REQUEST
        print(user_review_dict)


class ViewLocation(Screen):
    def on_enter(self, *args):
        global location_data
        print(location_data)
        self.ids.location_description.text = location_data['description']
        self.ids.location_name.text = location_data['location_name']
        self.ids.view_location_map.center_on(
            location_data['location_coords'][0],
            location_data['location_coords'][1]
        )
        self.ids.view_location_map.add_widget(
            MapMarker(
                lat=location_data['location_coords'][0],
                lon=location_data['location_coords'][1]
            )
        )
        return super().on_pre_enter(*args)


class ReviewsPage(Screen):
    pass


class ReviewItemScreen(Screen):
    def on_pre_enter(self, *args):
        star = 3
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


class MainPage(Screen):
    def convert_to_bbox(self, coords):
        return (
            round(coords[0]-0.01, 2),
            round(coords[1]-0.01, 2),
            round(coords[0]+0.01, 2),
            round(coords[1]+0.01, 2)
        )

    def view_location(self, instance):
        print(dir(instance))
        global location_data
        location_data = instance.location_data
        print(location_data)
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

        profile_ref = db.collection('Users').document(user['email'])
        profile_ref.update(new_profile_dict)

        user[u'username'] = new_profile_dict[u"username"]
        user[u'description'] = new_profile_dict[u"description"]
        print(user)

    def to_historyitem(self, instance):
        print(dir(instance))
        global history_data
        history_data = instance.history_data
        print(history_data)

        self.manager.current = "historyitem"
        self.manager.transition.direction = "left"

    def on_enter(self):
        self.ids.main_map.center_on(currentlat, currentlon)
        # TODO: comment out this later
        # self.ids.main_map.center_on(1.31, 103.85)
        bbox = self.ids.main_map.get_bbox()
        bottom_lat = round(int(bbox[0] * 50) / 50, 2)
        bottom_lon = round(int(bbox[1] * 50) / 50, 2)
        top_lat = round(int(bbox[2] * 50) / 50 + 0.02, 2)
        top_lon = round(int(bbox[3] * 50) / 50 + 0.02, 2)
        print(bottom_lat, bottom_lon, top_lat, top_lon)
        # lat_diff = top_lat - bottom_lat
        # lon_diff = top_lon - bottom_lon

        arr_coords = []
        temp_lat = round(bottom_lat + 0.01, 2)
        temp_lon = round(bottom_lon + 0.01, 2)

        while temp_lat < top_lat:
            temp_lon = round(bottom_lon + 0.01, 2)
            while temp_lon < top_lon:
                arr_coords.append((temp_lat, temp_lon))
                temp_lon = round(temp_lon + 0.02, 2)
            temp_lat = round(temp_lat + 0.02, 2)

        print(arr_coords)
        # Sending request
        chunk_ref = db.collection(u"Chunks")
        # chunk_ref = chunk_ref.where(u'chunk', u'in', arr_coords)
        # docs = chunk_ref.stream()
        # # print(docs)
        # for doc in docs:
        #     print(f'{doc.id} => {doc.to_dict()}')
        #     print(dir(doc.get))
        for i in arr_coords:
            # doc = chunk_ref.document(str(i)).get()
            # if doc.exists:
            chunk_locations_ref = chunk_ref.document(
                str(i)).collection(u'Locations')
            docs = chunk_locations_ref.stream()
            for doc in docs:
                locationdata = doc.to_dict()
                print(f'\n{doc.id} => {locationdata}')
                marker = MapMarkerPopup(
                    lat=locationdata['location_coords'][0],
                    lon=locationdata['location_coords'][1]
                )
                button = MDRoundFlatButton(
                    text=locationdata['location_name'],
                    md_bg_color=[0.24705882352941178,
                                 0.3176470588235294, 0.7098039215686275, 1.0],
                    text_color=[1, 1, 1, 1],
                    # on_release=lambda x: self.view_location(locationdata)
                    on_release=self.view_location
                )
                button.location_data = locationdata
                marker.add_widget(button)
                self.ids.main_map.add_widget(marker)

        # TODO: render chunks

        print("entered mainpage")
        # GET data from firestore
        history_ref = db.collection(u"Users").document(
            USER_EMAIL).collection(u"History")
        docs = history_ref.stream()
        global history_items
        for doc in docs:
            historyitemdata = doc.to_dict()
            listitem = TwoLineAvatarIconListItem(
                text=historyitemdata["restaurant_name"],
                secondary_text=historyitemdata["time"],
                on_release=self.to_historyitem)

            listitem.history_data = historyitemdata
            # TODO: add a date to the widget
            if historyitemdata not in history_items:
                history_items.append(historyitemdata)
                self.ids.historylist.add_widget(listitem)
            # self.ids.historylist is the history wrapper

            history_items.append(historyitemdata)
            print(historyitemdata)
        user = self.manager.get_screen('login').ids['user']
        print(user)
        self.ids.username_input.text = user['username']
        self.ids.description_input.text = user['description']

        # marker = MapMarkerPopup(
        #     lat=1.3784949677817633, lon=103.76313504803471)
        # marker.add_widget(
        #     MDRoundFlatButton(
        #         text="python button",
        #         md_bg_color=[0.24705882352941178,
        #                      0.3176470588235294, 0.7098039215686275, 1.0],
        #         text_color=[1, 1, 1, 1],
        #         on_press=lambda x: self.view_location()
        #     )
        # )
        # self.ids.main_map.add_widget(marker)


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
        Builder.load_file("pages/otherpages/reviewitem.kv")
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
        sm.add_widget(ReviewItemScreen(name="reviewitem"))
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
