import requests
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
from kivymd.uix.label import MDLabel
from kivymd.uix.list import ThreeLineListItem

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
# finds an approximate of the user's location using ip address of user
g = geocoder.ip('me')
currentlat, currentlon = g.latlng
print(g.latlng)

USER_EMAIL = ""
user_name = ""
# used to store photo when adding location
photo_path = f""

# used to store the history info to prevent the
# same history info from appearing again when database is queried again
history_items = []
# Used to store data of an history item when going to another page
history_data = {}

# used to store the locations info to prevent the
# same location info from appearing again when database is queried again
locations_data = []
# Used to store data of a location when going to another page
location_data = {}

# this is to stop the same photo from
# reappearing when viewing the location
location_count = 0


class LoginScreen(Screen):

    def login(self):
        global USER_EMAIL
        # refers to user email without trailing or leading whitespace
        USER_EMAIL = self.ids.user_email.text.strip()
        global user_name
        # refers to username without trailing or leading whitespace
        user_name = self.ids.username.text.strip()
        user_password = self.ids.password.text
        userdata = {
            u'email': USER_EMAIL,
            u'username': user_name,
            u'password': user_password,
            u'description': ""
        }
        if USER_EMAIL == "" or user_name == "" or user_password == "":
            # Shows a popup that one of the fields is not filled
            Snackbar(text="One of the fields is not filled.").open()
            return
        userinfo_valid = True

        try:
            # reference to user on database (/Users/user_email)
            user_db_ref = db.collection(u'Users').document(USER_EMAIL)
            # getting data
            newuserdata = user_db_ref.get()
            # if user exists on the database
            if newuserdata.exists:
                tempuserdata = newuserdata.to_dict()
                # if password incorrect
                if userdata['password'] != tempuserdata['password']:
                    # returns a popup saying password is incorrect
                    Snackbar(text="Password incorrect.").open()
                    userinfo_valid = False
                # if username incorrect
                elif userdata['username'] != tempuserdata['username']:
                    # returns a popup saying username is incorrect
                    Snackbar(text="Username incorrect.").open()
                    userinfo_valid = False
                userdata = tempuserdata
                print(userdata)
            else:
                raise Exception("user does not exist")

        except Exception:
            print(Exception)
            db.collection('Users').document(USER_EMAIL).set(userdata)
            # print('Sucessfully created new user: {0}'.format(userdata.uid))
        finally:
            # Go to main page
            if not userinfo_valid:
                return
            # storing the user in the ids
            self.ids["user"] = userdata
            # go to mainpage
            self.manager.current = "mainpage"
            self.manager.transition.direction = "left"


class AddLocationScreen_1(Screen):

    # function to show the time picker for closing time
    def show_closing_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_closing_time)
        time_dialog.open()

    # function to show the time picker for opening time
    def show_opening_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_opening_time)
        time_dialog.open()

    # function to update the text for closing time when the closing time on the time picker changes
    def get_opening_time(self, instance, time):
        self.ids.opening_time.text = str(time)

    # function to update the text for closing time when the opening time on the time picker changes
    def get_closing_time(self, instance, time):
        self.ids.closing_time.text = str(time)

    # function that runs when going to addlocation2
    def to_addlocation2(self):
        location_coords = []
        try:
            # location coords of the mapmarker on the map
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
        # navigates to addlocation_2 page
        self.manager.current = "addlocation_2"
        self.manager.transition.direction = "left"

    # function that runs when you enter the page

    def on_pre_enter(self):
        # getting mapview from ids
        mapview = self.ids.addlocation_map
        # changing the lat and lon the map is focused on
        mapview.lat = currentlat
        mapview.lon = currentlon
        # running on_touch_map when map is touched
        mapview.on_touch_down = self.on_touch_map

    def on_touch_map(self, touch):
        # bbox refers to the coordinates at the top right hand corner and the bottom left hand corner
        bbox = self.ids.addlocation_map.get_bbox()
        print(bbox)

        # finding lat and lon on the map from touch location
        lat, lon = self.ids.addlocation_map.get_latlon_at(touch.x, touch.y)
        # offsetting the values because it does not work for different screen sizes (Doesnt really work very well)
        lat, lon = lat - 0.0003649793, lon - 0.0013741504
        if self.width < 700:
            lon += 0.0008598847
        elif self.width < 1100:
            lat -= -0.0000751428
            lon -= -0.000451037

        # Since clicking anywhere on the screen registers as a press on the mapview,
        #  I need to check whether the place that the user clicked on is within the mapview
        marker_within_mapview = bbox[0] < lat < bbox[2] and bbox[1] < lon < bbox[3]
        if not marker_within_mapview:
            return

        print("Touch down on", touch.x, touch.y)

        print("Tapped on", lat, lon)
        print(self.width, self.height)
        # putting the mapmarker
        marker = MapMarker(lat=lat, lon=lon)
        # if mapmarker is not on the map
        if self.ids.get("mapmarker") == None:
            self.ids.addlocation_map.add_marker(marker)
            self.ids["mapmarker"] = marker
        else:  # mapmarker is on the map
            # remove the current mapmarker
            self.ids.addlocation_map.remove_widget(
                self.ids["mapmarker"]
            )
            # add the new mapmarker with the updated coordinates
            self.ids.addlocation_map.add_marker(marker)
            self.ids["mapmarker"] = marker


class AddLocationScreen_2(Screen):
    # function runs when user clicks "take photo" button
    def take_photo(self, num, *args):
        global photo_path
        # enabling camera
        self.ids["camera"].play = False
        # export current image to png
        self.ids["camera"].export_to_png(f"./cache/location{num}.png")
        # remove the camera widget
        self.ids.camerawrapper.remove_widget(
            self.ids["camera"]
        )
        photo_path = f"./cache/location{num}.png"
        print(photo_path)

        # basically the code block below that uses cv2 is used to remove the black parts
        # of the photo that is on the sides of the image (not in the image)
        import cv2

        img = cv2.imread(photo_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnt = contours[0]
        x, y, w, h = cv2.boundingRect(cnt)
        crop = img[y:y+h, x:x+w]
        cv2.imwrite(photo_path, crop)

        # making an image of the photo that was taken
        location_image = Image(
            source=f"./cache/location{num}.png", allow_stretch=True)
        # add image widget
        self.ids.camerawrapper.add_widget(location_image)
        self.ids["location_image"] = location_image

        # remove take_photo button
        self.ids.appwrapper.remove_widget(
            self.ids["take_photo"]
        )
        # making a take_photo_again button
        take_photo_again = MDFillRoundFlatButton(
            text="Take photo again",
            on_press=lambda x: self.take_photo_again(num),
        )
        # adding the take_photo_again button
        self.ids.appwrapper.add_widget(take_photo_again)
        # assigning it an id
        self.ids["take_photo_again"] = take_photo_again

    # function runs when user clicks "take photo again" button
    def take_photo_again(self, num, *args):
        # remove the image that was taken
        os.remove(f"./cache/location{num}.png")
        # removing the image widget
        self.ids.camerawrapper.remove_widget(
            self.ids["location_image"]
        )

        # making a camera widget
        camera = Camera(play=True, resolution=(640, 480))
        # add camera widget
        self.ids.camerawrapper.add_widget(camera)
        # assigning it an id
        self.ids["camera"] = camera

        # remove take_photo_again button
        self.ids.appwrapper.remove_widget(
            self.ids["take_photo_again"]
        )

        # adding take_photo button
        take_photo = MDFillRoundFlatButton(
            text="Take photo",
            # num is different because if the path to the image taken is the same,
            # even after deleting it, it stays as the same image
            on_press=lambda x: self.take_photo(num+1)
        )
        self.ids.appwrapper.add_widget(take_photo)
        self.ids["take_photo"] = take_photo

    # function runs when submitting new lcoation
    def submit_new_location(self):
        # if no description provided, a popup would appear
        if self.ids.location_description.text == "":
            Snackbar(text="No description provided.").open()
            return

        # if no picture provided, a popup would appear
        if photo_path == "":
            Snackbar(text="No picture is uploaded.").open()
            return
        print('submit_new_location ran')

        # making a reference to the class addlocation1
        addlocation_1_ref = self.manager.get_screen("addlocation_1")

        # Represents coords of the new location
        location_coords = [
            str(addlocation_1_ref.ids["mapmarker"].lat),
            str(addlocation_1_ref.ids["mapmarker"].lon)
        ]
        # storage bucket
        bucket = storage.bucket()
        # name of image -> "<location name> <coords of the location>",
        # e.g. "macs (1.1, 101)"
        name = f"{addlocation_1_ref.ids.location_name.text} ({','.join(location_coords)})"
        # making a blob
        blob = bucket.blob(name)
        # uploading the photo to the blob
        blob.upload_from_filename(photo_path)
        blob.make_public()
        # getting public url
        url = blob.public_url
        print(url)

        from PIL import Image
        # width of image
        basewidth = 80
        img = Image.open(photo_path)
        # finding the basewidth as percentage of current width
        wpercent = (basewidth / float(img.size[0]))
        # rescaling the height based on the percentage
        hsize = int((float(img.size[1]) * float(wpercent)))
        # img should still have same aspect ratio, and this
        # resizes the image down where width is 80
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        # saving the image to the photo path
        img.save(photo_path)
        # name of image -> "<location name> <coords of the location> (smaller)",
        # e.g. "macs (1.1, 101) (smaller)"
        name = f"{addlocation_1_ref.ids.location_name.text} ({','.join(location_coords)}) (smaller)"
        # making the blob
        blob = bucket.blob(name)
        # uploading the image to the blob
        blob.upload_from_filename(photo_path)

        blob.make_public()
        # getting public url of the image
        small_url = blob.public_url
        # removing the photo_path
        os.remove(photo_path)

        # turn strings to floats (had to turn to strings so i could use .join() on them)
        location_coords[0] = float(location_coords[0])
        location_coords[1] = float(location_coords[1])

        # finding midpoint in chunk (chunk is 0.02 * 0.02 in terms of lat and lon)
        lat = round(int(location_coords[0] * 50) / 50 + 0.01, 2)
        lon = round(int(location_coords[1] * 50) / 50 + 0.01, 2)
        # chunk is represented by midpoint so its easier to find  and its easy to find boundaries
        chunk = (lat, lon)

        user_ans_dict = {
            "opening_time": addlocation_1_ref.ids.opening_time.text,
            "closing_time": addlocation_1_ref.ids.closing_time.text,
            "location_name": addlocation_1_ref.ids.location_name.text,
            "is_mall": addlocation_1_ref.ids.in_mall.active,
            "location_coords": location_coords,
            "description": self.ids.location_description.text,
            "photoURL": url,
            "smallphotoURL": small_url,
            "chunk": chunk,
            "1starcount": 0,
            "2starcount": 0,
            "3starcount": 0,
            "4starcount": 0,
            "5starcount": 0,
        }
        # reference to /Chunks/(x, y), where x and y is midpoint in chunk
        chunk_ref = db.collection(u'Chunks').document(str(chunk))
        # setting the dict {"chunk": chunk} in the document
        chunk_ref.set({"chunk": chunk})

        location_ref = db.collection(u'Chunks').document(str(chunk)).collection(
            u'Locations').document(user_ans_dict["location_name"])
        # Setting the document in /Chunks/(x, y)/Locations/location_name, where x and y is midpoint in chunk
        location_ref.set(user_ans_dict)
        print("Document set!")

        print(user_ans_dict)
        print("location set!")

        # redirects user back to mainpage
        self.manager.current = 'mainpage'
        self.manager.transition.direction = 'right'

    # runs when user enters addlocation2 screen
    def on_pre_enter(self):
        # lets the camera play
        self.ids.camera.play = True

    # runs when user leaves addlocation2 screen
    def on_pre_leave(self, *args):
        # in case user leaves page with camera still on (closes camera)
        self.ids.camera.play = False


selected_mapmarker = None


class AddHistoryItemScreen(Screen):

    # runs when user enters this screen
    def on_pre_enter(self, *args):
        # changing centre of the map to user's current lat and lon
        self.ids.addhistoryitem_map.lat = currentlat
        self.ids.addhistoryitem_map.lon = currentlon

    # runs when user enters page
    def on_enter(self):
        global locations_data
        print(locations_data)
        for i in locations_data:
            # print(f"{i['location_name']}.png")
            # making the mapmarker at the location coords
            mapmarker = MapMarker(
                lat=i['location_coords'][0],
                lon=i['location_coords'][1],
                # runs the function() when mapmarker is pressed
                on_press=self.mapmarker_pressed,
            )
            print(str(i['location_coords']))
            # adding the location
            self.ids[str(i['location_coords'])] = mapmarker
            self.ids.addhistoryitem_map.add_marker(mapmarker)

    # runs when mapmarker is pressed
    def mapmarker_pressed(self, instance):
        # gets coords of the pressed mapmarker
        coords = [instance.lat, instance.lon]
        print("Source: "+self.ids[str(coords)].source)

        # changes the source to a green mapmarker
        self.ids[str(coords)].source = ''
        self.ids[str(coords)].source = 'green_mapmarker.png'
        global selected_mapmarker
        print("Selected mapmarker:", selected_mapmarker)
        print("Keys in self.ids:", self.ids.keys())
        # checks if the previously selected mapmarker is a mapmarker
        # (sometimes there isnt a previous selected_mapmarker)
        if selected_mapmarker in self.ids.keys():
            self.ids[selected_mapmarker].source = '/Users/alonzopuah/Documents/GitHub/JSAcompcoursework2023/.env/lib/python3.10/site-packages/kivy_garden/mapview/icons/marker.png'
        # changes the selected mapmarker to the new one
        selected_mapmarker = str(coords)
        print("selected_mapmarker in self.ids.keys()")

    # function to show the date picker for when this was eaten
    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    # function to update the text that shows the date
    def on_date_save(self, instance, value, date_range):
        self.ids.date_input.text = str(value)
        print(value)

    # function to show the time picker for when this was eaten
    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_time)
        time_dialog.open()

    # function to update the text that shows the time
    def get_time(self, instance, time):
        self.ids.time_input.text = str(time)

    # runs when submitting a new history item
    def submit_history_item(self):
        global selected_mapmarker
        # if no mapmarker is on the map
        if selected_mapmarker == None:
            # returns a popup saying that location is not selected
            Snackbar(text="Location not selected.").open()
            return
        # sg_tz = pytz.timezone("Singapore")
        # current_time = datetime.now(sg_tz)
        # name of document -> e.g. "2023-02-19,00:43:00"
        date_time = self.ids.date_input.text + "," + self.ids.time_input.text
        # turns the lat and lon of selected marker into a float from a string
        local_selected_mapmarker = [
            float(x) for x in selected_mapmarker[1:-1].split(',')
        ]
        print("selected mapmarker:", local_selected_mapmarker)
        # finding current chunk by using the convert_to_bbox() function i defined
        current_chunk = self.manager.get_screen(
            'mainpage').convert_to_bbox(local_selected_mapmarker)
        print("current_chunk:", current_chunk)
        # Gets a reference to the current location that is reviewed
        location_ref = db.collection(u"Chunks").document(str(current_chunk)).collection(
            u"Locations").where(u'location_coords', u'==', local_selected_mapmarker)
        # this locations variable is actually just one location
        locations = location_ref.stream()
        location_name = ''
        # for loop only runs once
        for doc in locations:
            location = doc.to_dict()
            print("Location_dict: ", location)
            # gets the location name
            location_name = location['location_name']
        print("Location_name:", location_name)
        # the dictionary that will be sent to the server
        user_ans_dict = {
            'restaurant_name': location_name,
            'location_coords': local_selected_mapmarker,
            'date': self.ids.date_input.text,
            'time': self.ids.time_input.text,
            'servertimestamp': SERVER_TIMESTAMP
        }
        # Checks if any of the fields are not filled

        # if restaurant name not filled
        if user_ans_dict['restaurant_name'] == "":
            Snackbar(text="Name not filled.").open()
            return
        # if restaurant date not filled
        elif user_ans_dict['date'] == "":
            Snackbar(text="Date is not filled.").open()
            return
        # if restaurant time not filled
        elif user_ans_dict['time'] == "":
            Snackbar(text="Time is not filled.").open()
            return
        # TODO: SEND REQUEST
        print(user_ans_dict)

        # Gets a ref to the history document that will be submitted
        historyitem_ref = db.collection(u"Users").document(
            USER_EMAIL).collection(u"History").document(date_time)
        print(historyitem_ref)
        print(USER_EMAIL, date_time)
        # sets the document onto the database
        historyitem_ref.set(user_ans_dict)
        # navigates to the mainpage
        self.manager.current = 'mainpage'
        self.manager.transition.direction = 'left'


class HistoryItemScreen(Screen):
    starcount = 0

    def click_star(self, star):
        if star == 1:
            # changes the first star to yellow and rest to grey
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#d6d6d6"
            self.ids.star_three.text_color = "#d6d6d6"
            self.ids.star_four.text_color = "#d6d6d6"
            self.ids.star_five.text_color = "#d6d6d6"
        if star == 2:
            # changes the second star to yellow and rest to grey
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#f6ae00"
            self.ids.star_three.text_color = "#d6d6d6"
            self.ids.star_four.text_color = "#d6d6d6"
            self.ids.star_five.text_color = "#d6d6d6"
        if star == 3:
            # changes the third star to yellow and rest to grey
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#f6ae00"
            self.ids.star_three.text_color = "#f6ae00"
            self.ids.star_four.text_color = "#d6d6d6"
            self.ids.star_five.text_color = "#d6d6d6"
        if star == 4:
            # changes the fourth star to yellow and rest to grey
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#f6ae00"
            self.ids.star_three.text_color = "#f6ae00"
            self.ids.star_four.text_color = "#f6ae00"
        if star == 5:
            # changes the fifth star to yellow and rest to grey
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#f6ae00"
            self.ids.star_three.text_color = "#f6ae00"
            self.ids.star_four.text_color = "#f6ae00"
            self.ids.star_five.text_color = "#f6ae00"
            self.ids.star_five.text_color = "#f6ae00"

        # using self to store the starcount
        self.starcount = star

    # runs when user enters the historyitemscreen page
    def on_enter(self, *args):
        global history_data
        print("Keys of ids:", self.ids.keys())
        print("Entered historyitem: ", history_data)
        # storing info (history chunk and history page) about the history item which will be used in reviews
        self.history_chunk = self.manager.get_screen(
            'mainpage').convert_to_bbox(history_data['location_coords'])
        self.history_name = history_data['restaurant_name']

        # changing ui

        # setting location name in the places that it will be used
        self.ids.location_name.text = history_data['restaurant_name']
        self.ids.location_name_review.text = history_data['restaurant_name']
        # setting the time at which the food was eaten
        self.ids.eaten_time.text = "Eaten at: " + str(history_data['time'])
        # setting the map to center on the coordinates of the location
        self.ids.historyitem_map.center_on(
            history_data['location_coords'][0], history_data['location_coords'][1])

        # making the mapmarker which will be on the map
        marker = MapMarkerPopup(
            lat=history_data['location_coords'][0], lon=history_data['location_coords'][1])
        # giving this mapmarker an id
        self.ids['mapmarker'] = marker
        # adding this mapmarker
        self.ids.historyitem_map.add_widget(marker)
        # getting a reference to the document where the location is stored
        location_ref = db.collection(u"Chunks").document(f"({self.history_chunk[0]}, {self.history_chunk[1]})").collection(
            u'Locations').document(history_data['restaurant_name'])
        # getting the data from the reference
        doc = location_ref.get()
        # setting a total reviews var which will be used later
        total_reviews = 0
        if doc.exists:
            # this variable refers to the location data
            location_data = doc.to_dict()

            # this is the total reviews by adding the 1starcount, 2starcount, etc together
            total_reviews = location_data['1starcount'] + location_data['2starcount'] + \
                location_data['3starcount'] + \
                location_data['4starcount'] + location_data['5starcount']
            print(total_reviews)
        else:
            print("Location doesnt exist")
        # setting the number of reviews on the name
        self.ids.num_reviews.text = f"{total_reviews} Reviews"

    # this function runs when the user submits a review
    def submit_review(self):
        global user_name
        # this refers to the review that will be uploaded to the database
        user_review_dict = {
            u"review": self.ids.review.text,
            u"rating": self.starcount,
            u'servertimestamp': SERVER_TIMESTAMP,
            u'user': user_name
        }
        print(user_review_dict)
        # sets the timezone to singapore
        sg_tz = pytz.timezone("Singapore")
        # sets the current time with reference to the timezone
        current_time = str(datetime.now(sg_tz))

        # check if review too long
        if len(user_review_dict[u"review"]) > 100:
            Snackbar(text="Review too long.").open()
            return
        # check if no stars are inputted
        elif self.starcount == 0:
            Snackbar(text="Rating not filled.").open()
            return
        # check if there is a review in the first place
        elif user_review_dict[u"review"] == "":
            Snackbar(text="Review not filled.").open()
            return
        # refers to the history data that was updated when the historypage was entered
        global history_data

        # is a reference to the location
        review_ref = db.collection('Chunks').document(str(self.history_chunk)).collection(
            'Locations').document(self.history_name)
        # gets the location data from the database
        doc = review_ref.get()
        if doc.exists:
            doc = doc.to_dict()
        # adds one to the starcount of whatever rating it was
        doc[f'{self.starcount}starcount'] = doc[f'{self.starcount}starcount'] + 1
        # sets the document with the newly updated data (replacing)
        review_ref.set(doc)
        # Sets the data on the review page
        review_ref.collection('Reviews').document(
            current_time).set(user_review_dict)

        # redirects back to mainpage
        self.manager.current = 'mainpage'
        self.manager.transition.direction = 'right'

    # runs when the user leaves the historyitem screen
    def on_leave(self):
        # removes the mapamarker so that when you reenter the page the mapmarker will not stay there
        self.ids.historyitem_map.remove_widget(self.ids['mapmarker'])


class ViewLocation(Screen):

    # runs when the user enters the viewlocation screen
    def on_enter(self):
        # refers to the location data of the location that is clicked
        global location_data
        print(location_data)
        # location has a description
        if 'description' in location_data:
            # if is_mall is true
            if location_data['is_mall']:
                # adds an "in mall" before everything else
                self.ids.location_description.text = f"(In mall)\n{location_data['description']}"
            else:
                # shows the description of the location
                self.ids.location_description.text = location_data['description']
        else:
            # since no description provided, sets text as "No description provided"
            self.ids.location_description.text = "No description provided"
        # sets the location name
        self.ids.location_name.text = location_data['location_name']
        # gets the photourl in the location
        response = requests.get(
            location_data['photoURL']
        )
        # if the response is successful
        if response.status_code:
            global location_count
            # the location_count is used to stop the same photo from
            # reappearing when viewing the same path
            photo_path = f"./cache/location{location_count}.png"
            # saves the photo to the photo_path variable which represents the path of the photo
            with open(photo_path, 'wb') as fp:
                fp.write(response.content)
            # sets the source of the image in the ui to the photo path
            self.ids.location_image.source = photo_path
            location_count += 1
        # centers the map onto the coords of the location
        self.ids.view_location_map.center_on(
            location_data['location_coords'][0],
            location_data['location_coords'][1]
        )
        # sets the mapmarker to the coords of the location
        locationmapmarker = MapMarker(
            lat=location_data['location_coords'][0],
            lon=location_data['location_coords'][1],
        )
        # gives the mapmarker an id
        self.ids['mapmarker'] = locationmapmarker

        self.ids.view_location_map.add_widget(locationmapmarker)
        # refers to total reviews of the location (by adding up 1starcount, 2starcount, etc)
        total_reviews = location_data['1starcount'] + location_data['2starcount'] + \
            location_data['3starcount'] + \
            location_data['4starcount'] + location_data['5starcount']
        # refers to total reviews of the location (by adding up 1starcount * 1, 2starcount * 2, etc)
        total_rating = location_data['1starcount'] + location_data['2starcount'] * 2 + \
            location_data['3starcount'] * 3 + \
            location_data['4starcount'] * 4 + location_data['5starcount'] * 5

        # sets the review count
        self.ids.review_count.text = f"{total_reviews} Reviews"
        # configuring the max of each progressbar
        self.ids.rating_one.max = total_reviews
        self.ids.rating_two.max = total_reviews
        self.ids.rating_three.max = total_reviews
        self.ids.rating_four.max = total_reviews
        self.ids.rating_five.max = total_reviews
        # sets to 0 to prevent zerodivision error
        if total_reviews == 0:
            self.ids.rating.text = "0.0"
        else:
            # represents the average rating
            self.ids.rating.text = str(round(total_rating / total_reviews, 1))
        # configuring the value of each progressbar
        self.ids.rating_one.value = location_data['1starcount']
        self.ids.rating_two.value = location_data['2starcount']
        self.ids.rating_three.value = location_data['3starcount']
        self.ids.rating_four.value = location_data['4starcount']
        self.ids.rating_five.value = location_data['5starcount']

    # runs when the user leaves the viewlocation page
    def on_leave(self, *args):
        # sets the image source to nothing (removing the image basically)
        self.ids.location_image.source = ''
        # removes the mapmarker from the map
        self.ids.view_location_map.remove_widget(self.ids['mapmarker'])
        print(f"./cache/location{location_count-1}.png")
        # minus 1 becuase the location_count was changed later on
        os.remove(f"./cache/location{location_count-1}.png")


review_data = {}
current_reviews = []


class ReviewsPage(Screen):
    # runs when the user wants to go to the review page
    def to_review_page(self, instance):
        global review_data
        # gets the review data from the review that was clicked
        review_data = instance.reviewdata
        # goes to the reviewitem screem
        self.manager.current = 'reviewitem'
        self.manager.transition.direction = 'left'

    # rus when the user enters the reviewspage screen
    def on_enter(self):
        global location_data
        # refers to reviews that have been loaded
        global current_reviews
        # shows a popup which reminds the user on how to review the location they are viewing from
        Snackbar(
            text="To review this, you need to add it to your history first, then review it on the history item page"
        ).open()
        # changing the location label to the location name
        self.ids.location_label.text = location_data['location_name']
        # refers to total reviews of the location (by adding up 1starcount, 2starcount, etc)
        total_reviews = location_data['1starcount'] + location_data['2starcount'] + \
            location_data['3starcount'] + \
            location_data['4starcount'] + location_data['5starcount']
        # refers to total reviews of the location (by adding up 1starcount * 1, 2starcount * 2, etc)
        total_rating = location_data['1starcount'] + location_data['2starcount'] * 2 + \
            location_data['3starcount'] * 3 + \
            location_data['4starcount'] * 4 + location_data['5starcount'] * 5

        # if no reviews yet
        if total_reviews == 0:
            # shows no reviews yet to avoid zero division error when calculating average reviews
            self.ids.average_rating.text = "Average: No reviews yet"
        else:
            # calculates average reviews and puts it into the label which contains the average
            self.ids.average_rating.text = f"Average: {str(round(total_rating / total_reviews, 1))} of 5 stars"

        # gets reference to 'review' collection in the database
        reviews_ref = db.collection(u'Chunks').document(f"({location_data['chunk'][0]}, {location_data['chunk'][1]})").collection(
            u'Locations').document(location_data['location_name']).collection(u'Reviews')
        # getting all reviews from database
        reviews = reviews_ref.stream()
        # has_list refers to whether reviews are present
        has_list = False
        # looping through each review
        for doc in reviews:
            # reviews present
            has_list = True
            review_dict = doc.to_dict()
            print(review_dict)
            # if review has not been loaded already
            if review_dict not in current_reviews:
                # defines a listitem
                listitem = ThreeLineListItem(
                    text=review_dict['user'],
                    secondary_text=review_dict['review'],
                    tertiary_text=f"{review_dict['rating']} of 5 stars",
                    on_press=self.to_review_page,
                )
                # gives listitem a property which has the
                # data that has been gotten from the database
                listitem.reviewdata = review_dict
                # adds the listitem
                self.ids.review_list.add_widget(listitem)
                # give it an id
                self.ids[review_dict['review']] = listitem
                # appends loaded listitem to the loaded reviews list
                current_reviews.append(review_dict)
        # in the scenario that no reviews have been added
        if not has_list:
            # adds a label which shows that no reviews have been added yet
            self.ids.review_list.add_widget(
                MDLabel(text="No reviews yet", halign="center")
            )

    def on_leave(self):
        global current_reviews
        for i in current_reviews:
            self.ids.review_list.remove_widget(self.ids[i['review']])


class ReviewItemScreen(Screen):
    # runs when the user enters the reviewitemscreen
    def on_pre_enter(self, *args):
        # this is the data of the review item
        global review_data
        # refers to the rating of the review
        star = review_data['rating']
        if star == 1:
            # changes the first star to yellow and the rest to grey
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#d6d6d6"
            self.ids.star_three.text_color = "#d6d6d6"
            self.ids.star_four.text_color = "#d6d6d6"
            self.ids.star_five.text_color = "#d6d6d6"
        if star == 2:
            # changes the second star to yellow and the rest to grey
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#f6ae00"
            self.ids.star_three.text_color = "#d6d6d6"
            self.ids.star_four.text_color = "#d6d6d6"
            self.ids.star_five.text_color = "#d6d6d6"
        if star == 3:
            # changes the third star to yellow and the rest to grey
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#f6ae00"
            self.ids.star_three.text_color = "#f6ae00"
            self.ids.star_four.text_color = "#d6d6d6"
            self.ids.star_five.text_color = "#d6d6d6"
        if star == 4:
            # changes the fourth star to yellow and the rest to grey
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#f6ae00"
            self.ids.star_three.text_color = "#f6ae00"
            self.ids.star_four.text_color = "#f6ae00"
        if star == 5:
            # changes the fifth star to yellow and the rest to grey
            self.ids.star_one.text_color = "#f6ae00"
            self.ids.star_two.text_color = "#f6ae00"
            self.ids.star_three.text_color = "#f6ae00"
            self.ids.star_four.text_color = "#f6ae00"
            self.ids.star_five.text_color = "#f6ae00"
            self.ids.star_five.text_color = "#f6ae00"

        # sets the review text to the review text from database
        self.ids.review_text.text = review_data['review']
        # sets the review user to the review user from database
        self.ids.reviewer.text = review_data['user']
        # sets the review rating to the review rating from database
        self.ids.rating.text = f"{star} of 5 stars"


class MainPage(Screen):
    # this function actually means to convert to chunk im just lazy to change every occurrence
    def convert_to_bbox(self, coords):
        # finds the lowest possible lat in the chunk
        bottom_lat = round(int(coords[0] * 50) / 50, 2)
        # finds the lowest possible lon in the chunk
        bottom_lon = round(int(coords[1] * 50) / 50, 2)
        # returns midpoint of the chunk in terms of lat and lon (chunk is 0.02 * 0.02)
        return (
            round(bottom_lat + 0.01, 2),
            round(bottom_lon + 0.01, 2)
        )
    # runs when the user clicks on the location button

    def view_location(self, instance):
        global location_data
        # refers to the location data
        location_data = instance.location_data
        print(location_data)
        print("view_location has been run")

        # redirects user to viewlocation page
        self.manager.current = "viewlocation"
        self.manager.transition.direction = "left"

    # runs when user pressed "update profile" button
    def update_profile(self):
        # refers to updated username and description
        new_profile_dict = {
            u"username": self.ids.username_input.text,
            u"description": self.ids.description_input.text
        }
        # find the user if
        user = self.manager.get_screen('login').ids['user']

        # gets a reference to the document which has info about the user
        profile_ref = db.collection('Users').document(user['email'])
        # updates the username and description
        profile_ref.update(new_profile_dict)

        # change username and description
        user[u'username'] = new_profile_dict[u"username"]
        user[u'description'] = new_profile_dict[u"description"]
        # popup showing that it has been updated
        Snackbar(text="Username and description updated.").open()
        print(user)

    # runs when the user clicks on a history item
    def to_historyitem(self, instance):
        global history_data
        # this refers to the history data of the clicked element
        history_data = instance.history_data
        print(history_data)

        # redirects user to historyitem
        self.manager.current = "historyitem"
        self.manager.transition.direction = "left"

    # initialise global variables
    images_list = []
    loaded_chunks = []
    coords = []

    # runs when the user opens the mainpage
    def load_locations(self):
        bbox = self.ids.main_map.get_bbox()
        bottom_lat = round(int(bbox[0] * 50) / 50, 2)
        bottom_lon = round(int(bbox[1] * 50) / 50, 2)
        top_lat = round(int(bbox[2] * 50) / 50 + 0.02, 2)
        top_lon = round(int(bbox[3] * 50) / 50 + 0.02, 2)
        print(bottom_lat, bottom_lon, top_lat, top_lon)

        arr_coords = []
        # finds the midpoint of the bottom-left chunk
        temp_lat = round(bottom_lat + 0.01, 2)
        temp_lon = round(bottom_lon + 0.01, 2)

        # finds all the chunks in the current view of the mapview
        while temp_lat < top_lat:
            temp_lon = round(bottom_lon + 0.01, 2)
            while temp_lon < top_lon:
                arr_coords.append((temp_lat, temp_lon))
                temp_lon = round(temp_lon + 0.02, 2)
            temp_lat = round(temp_lat + 0.02, 2)

        print(arr_coords)
        # a reference to the chunk
        chunk_ref = db.collection(u"Chunks")
        location_num = 0
        for i in arr_coords:
            # if current arr_coords is not loaded
            if i not in self.loaded_chunks:
                self.loaded_chunks.append(i)
                # gets reference to the locations
                chunk_locations_ref = chunk_ref.document(
                    str(i)).collection(u'Locations')
                # gets all the locations
                docs = chunk_locations_ref.stream()
                for doc in docs:
                    locationdata = doc.to_dict()
                    # represents the loaded locations
                    global locations_data
                    # appends to the loaded locations list
                    locations_data.append(locationdata)
                    print(f'\n{doc.id} => {locationdata}')

                    # Get image
                    if 'smallphotoURL' in locationdata.keys():
                        response = requests.get(
                            locationdata['smallphotoURL']
                        )
                        # the path that the photo will be stored in
                        location_path = ""
                        # if request is successful
                        if response.status_code:
                            location_path = f"./cache/location{locationdata['location_name']}.png"
                            # writes the image data into the path
                            with open(location_path, 'wb') as fp:
                                fp.write(response.content)
                        # if image not in list that represents loaded images
                        if location_path not in self.images_list:
                            # append the photo_path to the list
                            self.images_list.append(location_path)

                        # mapmarker popup which represents the coordinates
                        marker = MapMarkerPopup(
                            lat=locationdata['location_coords'][0],
                            lon=locationdata['location_coords'][1],
                            # source is the image that has been loaded
                            source=location_path
                        )
                    # if no image
                    else:
                        # just loads the mapmarker with no image
                        marker = MapMarkerPopup(
                            lat=locationdata['location_coords'][0],
                            lon=locationdata['location_coords'][1],
                        )
                    # represents the button that shows up when the mapmarker popup is clicked
                    button = MDRoundFlatButton(
                        text=locationdata['location_name'],
                        md_bg_color=[0.24705882352941178,
                                     0.3176470588235294, 0.7098039215686275, 1.0],
                        text_color=[1, 1, 1, 1],
                        on_release=self.view_location
                    )
                    # stores button data as a property
                    button.location_data = locationdata
                    # add button to the mapmarker
                    marker.add_widget(button)
                    # add mapmarker to the main map
                    self.ids.main_map.add_widget(marker)
                    print("widget added")

    def on_enter(self):
        # if map has not been loaded already
        if self.ids.main_map.lon == 0 and self.ids.main_map.lat == 0:
            # center the map on the user's location
            self.ids.main_map.center_on(currentlat, currentlon)
        # loads locations
        self.load_locations()

        print("entered mainpage")
        # gets reference to the history document of the current user
        history_ref = db.collection(u"Users").document(
            USER_EMAIL).collection(u"History")
        # gets all history items
        docs = history_ref.stream()
        global history_items
        currentdate = ''
        for doc in docs:
            # represents the data from the database
            historyitemdata = doc.to_dict()
            # represents the list item in the history screen
            listitem = TwoLineAvatarIconListItem(
                text=historyitemdata["restaurant_name"],
                secondary_text=historyitemdata["time"],
                on_release=self.to_historyitem)
            # adds history data as a property
            listitem.history_data = historyitemdata
            # if it has previously not been loaded
            if historyitemdata not in history_items:
                # append it to the list which represents the loaded history itesm
                history_items.append(historyitemdata)
                if historyitemdata['date'] != currentdate:
                    # represents the date at which the history item was posted
                    datelabel = MDLabel(
                        padding=(20, 0),
                        text=historyitemdata['date'],
                        font_size=50,
                        bold=True
                    )
                    # add datelabel to the historylist
                    self.ids.historylist.add_widget(datelabel)
                    # change current date (so that this date wont appear for those that are on the same day)
                    currentdate = historyitemdata['date']

                self.ids.historylist.add_widget(listitem)
            # making currentdate something other than ''
            currentdate = 'currentdate'
            # append historyitemdata to the loaded history items list
            history_items.append(historyitemdata)
            print(historyitemdata)
        # if there is a "no history yet" label in the history list
        if 'nohistorylabel' in self.ids.keys():
            self.ids.historylist.remove_widget(self.ids['nohistorylabel'])
            # making currentdate something other than ''
            currentdate = 'currentdate'
        # when there are no history items
        if currentdate == '':
            # represents a text saying "no history item yet"
            nohistorylabel = MDLabel(
                halign='center',
                text="No history yet",
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            # add the nohistorylabel to the historylist
            self.ids.historylist.add_widget(nohistorylabel)
            # assigning it an id
            self.ids['nohistorylabel'] = nohistorylabel

        # represents a user
        user = self.manager.get_screen('login').ids['user']
        print(user)
        # setting the username and description on the profile page to be equal
        # to the user's username and description
        self.ids.username_input.text = user['username']
        self.ids.description_input.text = user['description']

    # def on_leave(self):
    #     print(self.images_list)
    #     for i in self.images_list:
    #         try:
    #             os.remove(i)
    #         except Exception:
    #             print(Exception)
    #             pass


# class WindowManager(ScreenManager):
#     pass


class HomePage(MDApp):

    def build(self):
        # setting the theme of the whole app in general
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

        # screenman
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

    # when the checkbox in addlocation is active
    def on_checkbox_active(self, checkbox, value):
        print(value, checkbox.state)
        if value:
            print('The checkbox', checkbox, 'is active',
                  'and', checkbox.state, 'state')
        else:
            print('The checkbox', checkbox, 'is inactive',
                  'and', checkbox.state, 'state')

    # Screen transition functions

    # function for going to any page
    def page_change(self, name, direction):
        self.root.current = name
        self.root.transition.direction = direction

    # The functions for going back to homepage
    def back_homepage(self):
        self.root.current = "mainpage"
        self.root.transition.direction = "right"

    # Close a popup
    def callback(self, instance):
        from kivymd.toast import toast

        toast(instance.text)


if __name__ == '__main__':
    HomePage().run()
