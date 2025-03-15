# import tkinter and pandas and datetime for GUI building and option to user profiles
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox, ttk
import pandas as pd
from datetime import datetime
# import Helvetica as part of the app design
import tkinter.font
# import tkmacosx to make song titles appear more Spotify-like
from tkmacosx import Button
# import webbrowser to open Spotify and other website such as Ultimate Guitar, Chordify and YouTube
import webbrowser
# import libraries for spotify API interaction
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import auth

# create basic window
root = tk.Tk()
root.title("Spotichord")
root.wm_minsize(375, 812)
root.wm_geometry('375x812')
# replace following variable with the correctly named file and the correct path if necessary
userdatafile = "user_data/users_data.csv"

# set up two fonts for easy and consistent design language
helv16 = tkinter.font.Font(family="Helvetica", size=16, weight="normal")
helv28 = tkinter.font.Font(family="Helvetica", size=28, weight="bold")

# define scope for spotipy API
scope = "playlist-read-private playlist-read-collaborative"
default_user_id = "316x3nwc2vnxr3azoeldv5wrn2p4?si=dba409d76a7348a2"
all_uri = []
all_names = []
full_gallery = {'name': [], 'href': []}

# create variables for user profile
name = tk.StringVar
password = tk.StringVar
spotify_id = tk.StringVar
loggedin = False
read_terms = False
user_gallery = ["No Song saved yet ☕︎"]
change_info = None
newinfo = None

'''For simplicity reasons, my own User ID is already selected.

Later, the users will be able to log into their personal Spotify account.
They will not alter be hardcoded default_user_id above, but
the program does change the global variable if the spotipy interaction fails with the hardcoded variable,
so that the new developer profile can be loaded and they can access their own playlists
'''
# use spotipy's authentication to access the account — this was taken over from TBI class & project
# the authentication process was taught in TBI class and used in the TBI project
spot = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=auth.client_id_spot,
    client_secret=auth.secret_spot,
    redirect_uri=auth.redir_spot,
    scope=scope
))

'''this function loads the spotify account to create lists of the playlists and playlist-uris that will be used later on
in order to not load all of the playlists' contents unnecessarily, they will be fetched only when a user decides to open
a specific, chosen playlist.
this code was taken from my TBI project and modified slightly for the purpose of this app
'''

# this function loads the linked spotify account and fetches the linked playlists
def load_account():
    global all_uri, all_names, full_gallery, full_gallery_df, default_user_id
    # create user profile referencing Spotify's API
    '''
    The “try“ method is used to make sure the code works both with only the default profile but also
    with the user-specific spotify profile, if they changed the default settings through the app's settings page.
    '''
    try:
        user_info = spot.user_playlists(default_user_id)
    except Exception as e1:
        try:
            user_info = spot.user_playlists(default_user_id)
        except Exception as e2:
            tk.messagebox.showerror('Error', '⌛︎ Please make sure the Spotify Authorization is'
                                             ' set up properly and you’re connected to the internet. ⚠︎ ⚡︎')
    playlists = spot.user_playlists(user_info['id'])
    # enumerating the playlists (also taken from TBI submission, originally based on Spotipy documentation)
    while playlists:  # The code in line 88 to 90 comes from the spotipy documentation and was slightly adjusted
        for i, playlist in enumerate(playlists['items']):
            all_names.append(playlist['name'])
            playlist['index'] = i + 1 + playlists['offset']
            all_uri.append(playlist['uri'])  # This list is created to retrieve the URI later on.
        if playlists['next']:
            playlists = spot.next(playlists)
        else:
            playlists = None
    # create dict and pandas-dataframe in order to be able to open the playlist link by name later
    full_gallery = {'name': all_names, 'href': all_uri}
    full_gallery_df = pd.DataFrame(full_gallery)


# this function loads a specific playlist that the user will have selected in the full-gallery overview ('playlists')
# this code was taken from the TBI project to ennumerate playlists and songs within playlists
def load_playlist(selected_playlist_df):
    global full_gallery, full_gallery_df, tracks
    uri = selected_playlist_df.iloc[0]['href']  # This gets the URI of the chosen playlist.
    # “try:“ is used to make sure the app tells the user clearly what is most likely going wrong if there is an error
    try:
        results = spot.playlist_tracks(uri)
    except:
        tk.messagebox.showerror('Error',
                                '⌛︎ Please make sure the Spotify Authorization is set up properly and you’re connected '
                                'to the internet. ⚠︎ ⚡︎')
    songs = results['items']
    tracks = []
    for i in songs:
        info = i['track']
        append = info['name']
        tracks.append(append)


# this function is taken from the class materials and the example project
def set_background(root, image_name):
    """This function was inspired by Robin Paul and sets the background image
    """
    image_file_path = f"backgrounds_img/{image_name}"
    img = Image.open(image_file_path)
    photo = ImageTk.PhotoImage(img)
    label = tk.Label(root, image=photo)
    label.image = photo  # To prevent garbage collection
    label.place(x=0, y=0, relwidth=1, relheight=1)


# this function is taken from the class materials and the example project
def clear_widgets():
    for i in root.winfo_children():
        i.destroy()


# this function displays the logged-in username as a messagebox to engage users playfully when interacting with the app
def greetings():
    tk.messagebox.showerror('Hey there!', f'You are logged in as: {name.get()}    ♬ ☺︎♪︎')


# this function builds the main homepage of the app (therefore the grid is laid out here)
# it lets the users go to log-in or sign-up pages respectively
def login():
    clear_widgets()
    # configure rows for easier and somewhat more scalable placement
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=4)
    root.columnconfigure(2, weight=1)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)
    root.rowconfigure(3, weight=1)
    root.rowconfigure(4, weight=1)
    root.rowconfigure(5, weight=1)
    root.rowconfigure(6, weight=1)
    root.rowconfigure(7, weight=1)

    set_background(root, "Home – 2.jpg")

    # refer to global variable to set user to be logged out
    global loggedin
    loggedin = False
    # place elements
    b_logon = tk.Button(root, text="👤 Log on", command=logon, font=helv28, borderwidth=0, relief="flat",
                        highlightthickness=0)
    b_logon.grid(column=1, row=2, padx=10, pady=5)
    b_gallery = tk.Button(root, text="♫ Gallery", command=error, font=helv28, borderwidth=0, relief="flat",
                          highlightthickness=0)
    b_gallery.grid(column=1, row=3, padx=10, pady=0)
    b_about = tk.Button(root, text="️︎︎ℹ︎ About Spotichord", command=about, font=helv28, borderwidth=0, relief="flat",
                        highlightthickness=0)
    b_about.grid(column=1, row=4, padx=10, pady=0)
    b_yourenew = tk.Button(root, text="You're new?     Sign up! ✍︎️", font=helv16, command=signup, borderwidth=0,
                           relief="flat", highlightthickness=0)
    b_yourenew.grid(column=1, row=5, sticky="s", padx=10, pady=0)


# create function for info-popup ('Spotify ID')
def whatisspotifyid():
    tk.messagebox.showinfo('ℹ︎ What is your Spotify_ID',
                           'Every Spotify account has a "Spotify-ID". This is not the same as the account name and can '
                           'be found under https://www.spotify.com/account/profile/. Please paste it in the according '
                           'field in order to be able to access your playlists and songs.')


# create function for into-popup ('Terms and Conditions')
def showmemyrights():
    tk.messagebox.showinfo('Terms and conditions',
                           'This project only exists for the purpose of my Python class. These terms are not truly'
                           ' legally binding. Any information that you put into the app will be stored locally on '
                           'your device. You may look into the Spotify Developer and/or Spotipy Documentation for '
                           'reference. This app does not access your account currently, '
                           'unless you change the default profile.')


# create sign-up page for new users
def signup():
    clear_widgets()
    global name, password, spotify_id, loggedin, read_terms

    set_background(root, "Login – 2.jpg")
    # back button
    b_back1 = tk.Button(root, text="🔙", command=login, font=helv16, borderwidth=0, relief="flat", highlightthickness=0)
    b_back1.grid(column=1, row=7, sticky="n", padx=10, pady=5)
    # username instruction
    b_username_label = tk.Label(root, text=" enter username: ", fg="black", bg="lightgreen", font=helv16, borderwidth=0,
                                relief="flat", highlightthickness=0)
    b_username_label.grid(column=1, row=2, sticky="s", padx=10, pady=5)
    # username input field
    name = tk.StringVar()
    b_username_input = tk.Entry(root, textvariable=name, fg="black", bg="white", font=helv16, borderwidth=0,
                                relief="flat", highlightthickness=0)
    b_username_input.grid(column=1, row=3, sticky="new", padx=47, pady=5)
    b_username_input.focus_set()
    # password instruction
    b_password_label = tk.Label(root, text=" enter password: ", fg="black", bg="lightgreen", font=helv16, borderwidth=0,
                                relief="flat", highlightthickness=0)
    b_password_label.grid(column=1, row=3, sticky="s", padx=10, pady=5)
    # password input field
    password = tk.StringVar()
    b_password_input = tk.Entry(root, textvariable=password, fg="black", bg="white", font=helv16, borderwidth=0,
                                relief="flat", highlightthickness=0)
    b_password_input.grid(column=1, row=4, sticky="new", padx=47, pady=5)
    # spotify ID instruction
    b_spotify_id_label = tk.Label(root, text=" enter Spotify ID: ", fg="black", bg="lightgreen", font=helv16,
                                  borderwidth=0, relief="flat", highlightthickness=0)
    b_spotify_id_label.grid(column=1, row=5, sticky="s", padx=10, pady=5)
    # spotify ID input field
    spotify_id = tk.StringVar()
    b_spotify_id_input = tk.Entry(root, textvariable=spotify_id, fg="black", bg="white", font=helv16, borderwidth=0,
                                  relief="flat", highlightthickness=0)
    b_spotify_id_input.grid(column=1, row=6, sticky="nw", padx=47, pady=5)
    # spotify ID info button ('i')
    b_spotify_info = tk.Button(root, text="ℹ︎", command=lambda: whatisspotifyid(), font=helv16, borderwidth=0,
                               relief="flat", highlightthickness=0, fg="orange")
    b_spotify_info.grid(column=1, row=6, sticky="ne", padx=47, pady=5)
    # terms and conditions button
    b_termsandconditions = tk.Button(root, text="Terms and conditions", command=lambda: showmemyrights(), fg="black",
                                     bg="lightgreen", font=helv16, borderwidth=0, relief="flat", highlightthickness=0)
    b_termsandconditions.grid(column=1, row=4, sticky="sew", padx=47, pady=5)
    # create read_terms variable to check status of having accepted the terms or not
    read_terms = tk.BooleanVar()
    # I followed this Youtube-Tutorial to learn the checkbox options of TKinter https://youtu.be/mPQdJDVtev0?t=558
    # set up checkbox
    check = tk.Checkbutton(root, text='I accept the terms and conditions. ✍︎', variable=read_terms,
                           selectcolor="darkblue", fg="black", bg="lightgreen", font=helv16, borderwidth=0,
                           relief="flat")  # for debugging add: # command = lambda: print(read_terms.get())
    check.grid(column=1, row=4, sticky="ew", padx=47, pady=5)
    # enter button
    b_enter_logon = tk.Button(root, text="         ✓   Enter   ➤️        ", command=lambda: signup_new_user_data(),
                              font=helv16, borderwidth=0, relief="flat", highlightthickness=0, fg='green')
    b_enter_logon.grid(column=1, row=6, padx=10, pady=0)


# this function uses the input new user data as well as the time to be saved in the .csv file
# it excessively checks whether the input data is according to the app's requirements
def signup_new_user_data():
    # refer to global variables in order to store new user data
    global password, name, spotify_id, user_gallery, read_terms
    # add timestamp like in the example to track when a user is being created
    current_timestamp = datetime.now()
    # read csv file
    user_ids = list(pd.read_csv(userdatafile).user_id)
    # create user_data dict to save userdata to csv file later
    user_data = {
        "user_id": name.get(),
        "password": password.get(),
        "spotify_id": spotify_id.get(),
        "created_at": current_timestamp,
        "gallery": user_gallery
    }
    # no password, name or spotify ID
    if len(password.get()) == 0 and len(name.get()) == 0 and len(spotify_id.get()) == 0:
        tk.messagebox.showerror('Warning', 'Please enter a name, password and your Spotify ID')
    # no password and name
    elif len(password.get()) == 0 and len(name.get()) == 0:
        tk.messagebox.showerror('Warning', 'Please enter a name and a password')
    # no password and spotify_id
    elif len(password.get()) == 0 and len(spotify_id.get()) == 0:
        tk.messagebox.showerror('Warning', 'Please enter a password and your Spotify ID')
    # no name and spotify_id
    elif len(name.get()) == 0 and len(spotify_id.get()) == 0:
        tk.messagebox.showerror('Warning', 'Please enter a name and your Spotify ID')
    # no name
    elif len(name.get()) == 0 or (len(name.get()) == 0 and len(password.get()) == 0) or (
            len(name.get()) == 0 and len(spotify_id.get()) == 0):
        tk.messagebox.showerror('Warning', 'Please enter your name.')
    # no password
    elif len(password.get()) == 0 or (len(name.get()) == 0 and len(password.get()) == 0) or (
            len(password.get()) == 0 and len(spotify_id.get()) == 0):
        tk.messagebox.showerror('Warning', 'Please enter a password.')
    elif len(spotify_id.get()) == 0 or (len(name.get()) == 0 and len(spotify_id.get()) == 0) or (
            len(password.get()) == 0 and len(spotify_id.get()) == 0):
        # no spotify_id
        tk.messagebox.showerror('Warning', 'You need to put in your Spotify ID in order to load your playlists.')
    # check if name is too long to be displayed on home screen
    # also to keep the length within reason
    elif len(name.get()) >= 11:
        tk.messagebox.showerror('Error', 'Your username is too long. Please choose up to 10 characters. ')
    # check if password is too long
    elif len(password.get()) >= 21:
        tk.messagebox.showerror('Error',
                                'Your password is too long. Please choose up to 20 characters. Even 10 are difficult'
                                ' to remember, no? ☃︎')
    else:
        # username is already taken
        if name.get() in user_ids:
            tk.messagebox.showwarning("WARNING", f"⚠︎ The username «{name.get()}» is already taken ⚠︎")
        # write data into the csv here
        else:
            if read_terms.get():
                # convert the dictionary into a user_data frame
                user_data_df = pd.DataFrame([user_data])
                # import the existing user data in order to combine them in pandas manually
                # this is because of a bug where the new user would not be stored
                # in a new line despite using the approach from the example GUI
                old_data_df = pd.read_csv(userdatafile)
                updated_userdata_df = pd.concat([old_data_df, user_data_df], ignore_index=True, sort=False)
                # write csv (using open and close as a safer method)
                with open(userdatafile, 'w') as f:
                    updated_userdata_df.to_csv(f, header=True, index=False)
                # close the file to prevent errors
                f.close()
                # add thank you message as in the example GUI, here as a messagebox
                tk.messagebox.showinfo('✧★︎✵ Congratulations! ✵★︎✧', f'New user created. Welcome, {name.get()}!  ✌︎☺︎')
                # go to welcome page
                welcome()
            else:
                # display warning if terms and conditions checkbox is not checked
                tk.messagebox.showwarning('WARNING', 'You need to accept the terms and conditions')


# this function is for the settings page in which users can make several changes to account settings and personal data
def settings():
    clear_widgets()
    set_background(root, "Settings.jpg")
    # back button
    b_back1 = tk.Button(root, text="🔙",
                        command=welcome, font=helv16, borderwidth=0, relief="flat", highlightthickness=0)
    b_back1.grid(column=1, row=7, sticky="n", padx=10, pady=5)
    # place buttons to edit specific attributes of the profile
    b_logon = tk.Button(root, text="Change username",
                        command=change_username, font=helv28, borderwidth=0, relief="flat", highlightthickness=0)
    b_logon.grid(column=1, row=2, padx=10, pady=5)
    b_gallery = tk.Button(root, text="Change password",
                          command=change_password, font=helv28, borderwidth=0, relief="flat", highlightthickness=0)
    b_gallery.grid(column=1, row=3, padx=10, pady=0)
    b_about = tk.Button(root, text="Change Spotify ID",
                        command=change_id, font=helv28, borderwidth=0, relief="flat", highlightthickness=0)
    b_about.grid(column=1, row=4, padx=10, pady=0)
    # create button that opens Spotify in a web browser and looks for the user's profile
    b_findaccount = tk.Button(root, text="♪ Find my account on Spotify ⇢",
                              command=find_user_on_spotify, font=helv16, fg='green', borderwidth=0, relief="flat",
                              highlightthickness=0)
    b_findaccount.grid(column=1, row=6, sticky='n', padx=10, pady=5)
    # place button that lets users change the default profile for Spotify in order to add their personal playlists
    b_change_default = tk.Button(root, text="Change default profile", command=change_default_profile, font=helv16,
                                 fg='darkred', borderwidth=0, relief="flat", highlightthickness=0)
    b_change_default.grid(column=1, row=6, padx=10, pady=0)


# this function makes sure the users really wants to change the default settings and open helpful pages in a web browser
def change_default_profile():
    # ensure the user is not accidentally making changes
    if tk.messagebox.askyesno('Change the default', 'Would you like to change the default profile?'):
        # instructing and warning the user about what they will need to do
        if tk.messagebox.askokcancel('WARNING',
                                     'You will have to go to the Spotify Developer Page and log into your account to'
                                     ' apply as a developer.'):
            # provide helpful Tutorrial for clear instructions on how to set up the developer account
            tutorial = tk.messagebox.askyesnocancel('Tutorial',
                                                    'Would you like to watch "Imdad Code"‘s Youtube Tutorial on how to'
                                                    ' get the Client-ID and the Client Secret?')
            if tutorial:
                webbrowser.open('https://youtu.be/2if5xSaZJlg?t=1159&feature=shared')
            elif not tutorial:
                # instruct user to use the correct address for Redirect URIs on the developer website
                tk.messagebox.showwarning('Note', '⚠ IMPORTANT: for Redirect URIs, use in http://127.0.0.1:9090 ⚠')
                # warn user about leaving the app for a web browser
                tk.messagebox.showwarning('Opening Spotify Developer Website',
                                          '⌛︎  Opening Spotify Developer Website now ...')
                # open website
                webbrowser.open('https://developer.spotify.com')
                # update default settings
                change_default_profile_input()


# this function lets the user input their new data from their developer profile to load their own playlists
def change_default_profile_input():
    global default_user_id
    clear_widgets()
    set_background(root, "Change Name-PW-SpID.jpg")
    # make clear where to put the secret and create variable to store the new one
    client_secret = tk.StringVar(value='Replace this text with your client secret')
    # back button
    b_back1 = tk.Button(root, text="🔙", command=settings, font=helv16, borderwidth=0, relief="flat",
                        highlightthickness=0)
    b_back1.grid(column=1, row=7, sticky="n", padx=10, pady=5)
    # explanatory label
    l_username_label = tk.Label(root, text=f"Please type Client ID and Client Secret below: ", font=helv16,
                                borderwidth=0, relief="flat", fg="black", bg="lightgreen", highlightthickness=0)
    l_username_label.grid(column=1, row=1, sticky='s', padx=10, pady=5)
    # create variable for new client id
    new_default_id = tk.StringVar()
    # input fields and enter button
    b_id_input = tk.Entry(root, textvariable=new_default_id, fg="black", bg="white", font=helv16, borderwidth=0,
                          relief="flat", highlightthickness=0)
    b_id_input.grid(column=1, row=2, sticky="new", padx=47, pady=5)
    b_id_input.focus_set()
    b_id_secret = tk.Entry(root, textvariable=client_secret, fg="red", bg="white", font=helv16, borderwidth=0,
                           relief="flat", highlightthickness=0)
    b_id_secret.grid(column=1, row=2, sticky="sew", padx=47, pady=5)
    b_enter_logon = tk.Button(root, text="         ✓   Enter   ➤️        ",
                              command=lambda: overwrite_default_profile(client_secret, app_id), font=helv16,
                              borderwidth=0, relief="flat", highlightthickness=0, fg='darkred')
    b_enter_logon.grid(column=1, row=3, padx=10, pady=0)


# this function overwrites the default profile in the auth.py python file
def overwrite_default_profile(client_secret, app_id):
    global spotify_id, default_user_id
    # choose file name here for simplicity and readability
    file_name = "auth.py"
    # write new file
    with open(file_name, 'w') as f:
        f.write(f'''\
client_id_spot = "{app_id.get()}"
secret_spot = "{client_secret.get()}"
redir_spot = "http://127.0.0.1:9090"       
''')
    # close file to avoid problems
    f.close
    # update default user variable
    default_user_id = spotify_id
    # notifiy user about the successful change
    tk.messagebox.showinfo('SUCCESS',
                           'Update successful! Your default Spotify Account has been changed. You should now be able to'
                           ' access your personal playlists from your Spotify account.')
    # re-laod spotify account with the new default
    load_account()
    # redirect to welcome page to let user enjoy the app with their own spotify account linked to it
    welcome()


# this function lets the user put in a new username
def change_username():
    global name, change_info, newinfo
    change_info = name
    clear_widgets()
    set_background(root, "Change Name-PW-SpID.jpg")
    # place elements
    # back button
    b_back1 = tk.Button(root, text="🔙", command=settings, font=helv16, borderwidth=0, relief="flat",
                        highlightthickness=0)
    b_back1.grid(column=1, row=7, sticky="n", padx=10, pady=5)
    # display current username and ask for new input
    b_username_display_label = tk.Label(root, text=f"Current username: {name.get()}", font=helv16, borderwidth=0,
                                        relief="flat", fg="black", bg="lightgreen", highlightthickness=0)
    b_username_display_label.grid(column=1, row=2, sticky="n", padx=10, pady=5)
    # display instructions
    b_username_label = tk.Label(root, text=f"Please type new username below: ", font=helv16, borderwidth=0,
                                relief="flat", fg="black", bg="lightgreen", highlightthickness=0)
    b_username_label.grid(column=1, row=2, padx=10, pady=5)
    # create new name variable
    newinfo = tk.StringVar()
    # create input field for new name
    b_username_input = tk.Entry(root, textvariable=newinfo, fg="black", bg="white", font=helv16, borderwidth=0,
                                relief="flat", highlightthickness=0)
    b_username_input.grid(column=1, row=2, sticky="sew", padx=47, pady=5)
    b_username_input.focus_set()
    # enter button
    b_enter_logon = tk.Button(root, text="         ✓   Enter   ➤️        ", command=lambda: update_info(), font=helv16,
                              borderwidth=0, relief="flat", highlightthickness=0, fg='green', bg='blue')
    b_enter_logon.grid(column=1, row=3, sticky="s", padx=10, pady=5)


# this function lets the user put in a new password
def change_password():
    global password, change_info, newinfo
    change_info = password
    clear_widgets()
    set_background(root, "Change Name-PW-SpID.jpg")
    # place elements
    # back button
    b_back1 = tk.Button(root, text="🔙", command=settings, font=helv16, borderwidth=0, relief="flat",
                        highlightthickness=0)
    b_back1.grid(column=1, row=7, sticky="n", padx=10, pady=5)
    # display current username and ask for new input
    b_username_display_label = tk.Label(root, text=f"Current password: {password.get()}", font=helv16, borderwidth=0,
                                        relief="flat", fg="black", bg="lightgreen", highlightthickness=0)
    b_username_display_label.grid(column=1, row=2, sticky="n", padx=10, pady=5)
    # instruct user on putting in a new password
    b_username_label = tk.Label(root, text=f"Please type new password below: ", font=helv16, borderwidth=0,
                                relief="flat", fg="black", bg="lightgreen", highlightthickness=0)
    b_username_label.grid(column=1, row=2, padx=10, pady=5)
    # create new name variable
    newinfo = tk.StringVar()
    # input field
    b_username_input = tk.Entry(root, textvariable=newinfo, fg="black", bg="white", font=helv16, borderwidth=0,
                                relief="flat", highlightthickness=0)
    b_username_input.grid(column=1, row=2, sticky="sew", padx=47, pady=5)
    b_username_input.focus_set()
    # enter button to confirm input
    b_enter_logon = tk.Button(root, text="         ✓   Enter   ➤️        ", command=lambda: update_info(), font=helv16,
                              borderwidth=0, relief="flat", highlightthickness=0, fg='green', bg='blue')
    b_enter_logon.grid(column=1, row=3, sticky="s", padx=10, pady=5)


# this function lets the user put in a new Spotify ID
def change_id():
    global spotify_id, change_info, newinfo
    change_info = spotify_id
    clear_widgets()
    set_background(root, "Change Name-PW-SpID.jpg")
    # place elements
    # back button
    b_back1 = tk.Button(root, text="🔙", command=settings, font=helv16, borderwidth=0, relief="flat",
                        highlightthickness=0)
    b_back1.grid(column=1, row=7, sticky="n", padx=10, pady=5)
    # use try / except because spotify_id will be a string when called from an existing user but
    # a PY_VAR when called by a newly created user
    try:
        change_info = spotify_id.get()
    except:
        change_info = spotify_id
    # display current (old) Spotify ID
    b_username_display_label = tk.Label(root, text=f"Current Spotify ID: {change_info}", font=helv16, borderwidth=0,
                                        relief="flat", fg="black", bg="lightgreen", highlightthickness=0)
    b_username_display_label.grid(column=1, row=2, sticky="n", padx=10, pady=5)
    # display instructions
    b_username_label = tk.Label(root, text=f"Please type new Spotify ID below: ", font=helv16, borderwidth=0,
                                relief="flat", fg="black", bg="lightgreen", highlightthickness=0)
    b_username_label.grid(column=1, row=2, padx=10, pady=5)
    # create new ID variable
    newinfo = tk.StringVar()
    # create input field for new Spotify ID
    b_username_input = tk.Entry(root, textvariable=newinfo, fg="black", bg="white", font=helv16, borderwidth=0,
                                relief="flat", highlightthickness=0)
    b_username_input.grid(column=1, row=2, sticky="sew", padx=47, pady=5)
    b_username_input.focus_set()
    # enter button to confirm input
    b_enter_logon = tk.Button(root, text="         ✓   Enter   ➤️        ", command=lambda: update_info(), font=helv16,
                              borderwidth=0, relief="flat", highlightthickness=0, fg='green', bg='blue')
    b_enter_logon.grid(column=1, row=3, sticky="s", padx=10, pady=5)


# this function takes updated information (via global variables to keep them beyond this function)
# and makes changes to the user data csv file as well as the in-app information
# the same function is used to change settings but also add/remove songs to the gallery
def update_info():
    global change_info, newinfo, name, user_gallery, spotify_id, password
    oldinfo = change_info
    '''Step 1: load old data'''
    # load user-info first by reading csv file and creating a dataframe with just the current user's information
    old_data_df = pd.read_csv(userdatafile)
    # create user_ids list
    user_ids = list(pd.read_csv(userdatafile).user_id)
    '''Step 2: replace outdated data'''
    # overwrite old data
    # depending on whether the user is changing the settings or adding a song, either use .get() for PY_VAR or a string
    try:
        # for changing the username
        # making sure the new name is also unique and not already taken by another user
        if oldinfo.get() == name.get():
            if newinfo.get() in user_ids:
                tk.messagebox.showerror('Error', '⚠︎ Username already taken. Please choose a unique name. ⚠︎')
                return
            elif len(newinfo.get()) >= 11:
                tk.messagebox.showerror('Error', 'Your username is too long. Please choose up to 10 characters. ')
                return
            else:
                new_data_df = old_data_df.replace(oldinfo.get(), newinfo.get())
        # for changing the password
        else:
            old_data_df.loc[old_data_df['user_id'] == name.get(), 'password'] = newinfo.get()
            new_data_df = old_data_df
    except:
        try:
            # for changing the spotify_id
            new_data_df = old_data_df.replace(oldinfo, newinfo.get())
        except:
            # for adding a song
            old_data_df.loc[old_data_df['user_id'] == name.get(), 'gallery'] = [newinfo]
            new_data_df = old_data_df
    # overwrite csv
    with open(userdatafile, 'w') as f:
        new_data_df.to_csv(f, header=True, index=False)
    # close the file to prevent errors
    f.close()
    '''Step 3: complete change and return to settings'''
    # display info message about successful update and redirect to the appropriate page
    if change_info == name:
        tk.messagebox.showinfo('✧★︎✵ Congratulations! ✵★︎✧', f'Profile updated. Have fun, {newinfo.get()}!  ✌︎☺︎')
        name = newinfo
        # return to settings
        settings()
    elif change_info == password or change_info == spotify_id:
        tk.messagebox.showinfo('✧★︎✵ Congratulations! ✵★︎✧', f'Profile updated. Have fun, {name.get()}!  ✌︎☺︎')
        # return to settings
        settings()
    else:
        user_gallery = newinfo
        # do not go to settings here but to the song page
        song(button)


def welcome():
    # try to load spotify account and display error message if unable to
    global spotify_id, default_user_id, loggedin
    # check if the Spotify/Spotipy connection works, otherwise inform user of the most likely problem
    try:
        load_account()
    except:
        tk.messagebox.showerror('ERROR', 'Please install Spotipy')
        return
    clear_widgets()
    # refer to global variable to set the user to be logged in
    loggedin = True
    set_background(root, "Home – 2.jpg")
    # place elements
    b_logon = tk.Button(root, text=f"👋 Hello, {name.get()}", cursor="heart", command=greetings, font=helv28,
                        borderwidth=0,
                        relief="flat", highlightthickness=0)
    b_logon.grid(column=1, row=2, padx=10, pady=0)
    b_gallery = tk.Button(root, text="♫ Gallery", command=gallery, font=helv28, borderwidth=0, relief="flat",
                          highlightthickness=0)
    b_gallery.grid(column=1, row=3, padx=10, pady=0)
    b_about = tk.Button(root, text="ℹ︎ About Spotichord", command=about, font=helv28, borderwidth=0, relief="flat",
                        highlightthickness=0)
    b_about.grid(column=1, row=4, padx=10, pady=0)
    b_logout = tk.Button(root, text="Logout ✌︎", command=login, font=helv16, borderwidth=0, relief="flat",
                         highlightthickness=0)
    b_logout.grid(column=1, row=6, sticky="n", padx=10, pady=0)
    b_settings = tk.Button(root, text="Profile settings ⚙︎", command=settings, font=helv16, borderwidth=0,
                           relief="flat",
                           highlightthickness=0)
    b_settings.grid(column=1, row=6, padx=10, pady=0)


# this function shows the info page "about Spotichord" coming from the homepage or the welcome page
def about():
    clear_widgets()
    set_background(root, "Login – 1.jpg")
    # place adaptive elements based on global variable depending on if a user is logged in or not
    if loggedin == True:
        b_back2 = tk.Button(root, text="Got it, thanks! ☑︎", command=welcome, font=helv16, borderwidth=0, relief="flat",
                            highlightthickness=0)
        b_back2.grid(column=1, row=6, sticky="s", padx=10, pady=0)
    elif loggedin == False:
        b_back2 = tk.Button(root, text="Got it, thanks! ☑︎", command=login, font=helv16, borderwidth=0, relief="flat",
                            highlightthickness=0)
        b_back2.grid(column=1, row=6, sticky="s", padx=10, pady=0)


# this function defines the log-on-page for returning users
def logon():
    clear_widgets()
    # refer to global username variable
    global name, password

    set_background(root, "Log on.jpg")
    # place elements
    b_back3 = tk.Button(root, text="🔙", command=login, font=helv16, borderwidth=0, relief="flat", highlightthickness=0)
    b_back3.grid(column=1, row=6, sticky="s", padx=10, pady=0)
    b_userid_label = tk.Label(root, text="Enter username and password below:", font=helv16, borderwidth=0,
                              relief="flat", fg="black", bg="lightgreen", highlightthickness=0)
    b_userid_label.grid(column=1, row=2, sticky="n", padx=10, pady=5)
    # note: the variable "name" will be called PY_VAR0 when first running the script
    # The .get() function must be used in order to retrieve the name, otherwise, the variable will show PY_VAR{number}
    name = tk.StringVar()
    # input field for username
    b_username_input = tk.Entry(root, textvariable=name, fg="black", bg="white", font=helv16, borderwidth=0,
                                relief="flat", highlightthickness=0)
    b_username_input.grid(column=1, row=2, sticky="sew", padx=47, pady=5)
    b_username_input.focus_set()
    # "password" will be called PY_VAR1 when first running the script
    password = tk.StringVar()
    # input field for user password
    b_password_input = tk.Entry(root, textvariable=password, fg="black", bg="white", font=helv16, borderwidth=0,
                                relief="flat", highlightthickness=0)
    b_password_input.grid(column=1, row=3, sticky="new", padx=47, pady=5)
    # enter button to confirm username and password
    b_enter_logon = tk.Button(root, text="         ✓   Enter   ➤️        ", command=lambda: check_user(), font=helv16,
                              borderwidth=0, relief="flat", highlightthickness=0, fg='green', bg='blue')
    b_enter_logon.grid(column=1, row=3, sticky="s", padx=10, pady=5)
    # redirect users who accidentally went to logon but do not have an account yet
    b_yourenew = tk.Button(root, text="You're new?     Sign up! ✍︎️", font=helv16, command=signup, borderwidth=0,
                           relief="flat", highlightthickness=0)
    b_yourenew.grid(column=1, row=4, sticky="n", padx=10, pady=5)


# this function is for the personalized gallery page with the user's saved songs
def gallery():
    global all_uri, all_names, user_gallery
    clear_widgets()
    set_background(root, "Gallery - Saved Playlist - Songs – 1.jpg")
    #  back button
    b_back4 = tk.Button(root, text=" 🔙", command=welcome, font=helv16, borderwidth=0, relief="flat",
                        highlightthickness=0)
    b_back4.grid(column=1, row=6, sticky="s", padx=10, pady=0)
    # create "add new songs" button
    b_addnew = tk.Button(root, text=" ✚ add a new song ♪♬", command=all_playlists, font=helv16, fg='green',
                         borderwidth=0, relief="flat", highlightthickness=0)
    b_addnew.grid(column=1, row=6, padx=0, pady=0)
    # GenAI (1/3): as most of the programmers in online-forums used OOP to neatly create scrollable buttons in TKInter,
    # which I am not supposed to use, I had to ask AI for some help with the following part of the code in this function
    # I have used its suggested solution but modified it slightly for my purpose.
    # create a frame for the buttons
    frame = tk.Frame(root, bg='white', borderwidth=0, relief="flat", highlightthickness=0)
    frame.grid(column=1, row=3, rowspan=2, sticky="ns", padx=5, pady=0)
    # create a canvas for scrolling
    canvas = tk.Canvas(frame, bg='white', borderwidth=0, relief="flat", highlightthickness=0)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='white')
    # configure the scrollable frame
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    # create the canvas window
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    # attach the scrollbar to the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    # pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    # create buttons in a grid layout
    if len(user_gallery) == 1:
        # e.g., this added was added to the suggestion to display a default string if the library is empty
        b_empty = tk.Button(scrollable_frame, text=user_gallery, command=all_playlists, font=helv16,
                            fg='darkblue', borderwidth=0, relief="flat", highlightthickness=0)
        b_empty.grid(row=3, column=0, padx=5, pady=5)
    else:
        for i, bname in enumerate(user_gallery[1:], start=1):
            max_length = 33  # Maximum number of characters
            display_text = (bname[:max_length] + '...') if len(bname) > max_length else bname
            b_song_button = tk.Button(scrollable_frame, text=display_text, command=lambda n=bname: song(n), font=helv16,
                                      fg='black', borderwidth=0, relief="flat", highlightthickness=0)
            b_song_button.grid(row=i, column=0, padx=5, pady=5)


# this function loads the selected playlist and opens the playlist function with the correctly adjusted variables
def choose_playlist(bname):
    global button, selected_playlist_df
    button = bname  # Store the button name in a variable
    selected_playlist_df = full_gallery_df.loc[full_gallery_df['name'] == button]
    playlist(selected_playlist_df)


def all_playlists():
    global all_uri, all_names, full_gallery, full_gallery_df, selected_playlist_df
    clear_widgets()
    set_background(root, "Gallery – 1.jpg")
    # create back button
    b_back4 = tk.Button(root, text=" 🔙", command=gallery, font=helv16, borderwidth=0, relief="flat",
                        highlightthickness=0)
    b_back4.grid(column=1, row=6, sticky="s", padx=10, pady=0)
    # GenAI (2/3): as most of the programmers in online-forums used OOP to neatly create scrollable buttons in TKInter,
    # which I am not supposed to use, I had to ask AI for some help with the following part of the code in this function
    # I have used its suggested solution but modified it slightly for my purpose.
    # Create a frame for the buttons
    frame = tk.Frame(root, bg='white', borderwidth=0, relief="flat", highlightthickness=0)
    frame.grid(column=1, row=3, rowspan=2, sticky="ns", padx=0, pady=0)
    # create a canvas for scrolling
    canvas = tk.Canvas(frame, bg='white', borderwidth=0, relief="flat", highlightthickness=0)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='white')
    # configure the scrollable frame
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    # create the canvas window
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    # attach the scrollbar to the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    # pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    # create buttons in a grid layout
    for i, bname in enumerate(all_names):
        max_length = 33  # Maximum number of characters
        display_text = (bname[:max_length] + '...') if len(bname) > max_length else bname
        button = tk.Button(scrollable_frame, text=display_text, command=lambda n=bname: choose_playlist(n), font=helv16,
                           borderwidth=0, relief="flat", highlightthickness=0)
        button.grid(row=i, column=0, padx=5, pady=5)


# this function is activated upon the selection of a song and calls the update_info() function to add it to the  gallery
def choose_song(bname):
    global button, user_gallery, selected_playlist_df, change_info, newinfo
    button = bname  # store the button name in a variable
    selected_playlist_df = full_gallery_df.loc[full_gallery_df['name'] == button]
    if button in user_gallery:
        # inform user of unnecessary double-selection of a song
        tk.messagebox.showwarning("Warning", "☕︎ This song is already in your Gallery! ☑︎")
    else:
        # create copy of the existing list of songs
        change_info = user_gallery.copy()
        # create copy of the copy to modify only append new song to that second copy
        newinfo = change_info.copy()
        # append new song
        newinfo.append(button)
        # overwrite csv with updated gallery
        # this uses the same function as the settings in order to make the code cleaner and more efficient
        update_info()
        # let the user know that his gallery has been updated
        tk.messagebox.showinfo("Success", "☕︎ Saved song to gallery! ☑︎")
    # open the song page
    song(bname)


# this function shows the selected, opened playlist for users to choose songs from
def playlist(selected_playlist):
    global all_uri, all_names, selected_playlist_df, tracks
    load_playlist(selected_playlist)
    clear_widgets()
    set_background(root, "Gallery - Saved Playlist - Songs – 1.jpg")
    # create back button
    b_back4 = tk.Button(root, text=" 🔙", command=all_playlists, font=helv16, borderwidth=0, relief="flat",
                        highlightthickness=0)
    b_back4.grid(column=1, row=6, sticky="s", padx=10, pady=0)
    # GenAI (1/3): as most of the programmers in online-forums used OOP to neatly create scrollable buttons in TKInter,
    # which I am not supposed to use, I had to ask AI for some help with the following part of the code in this function
    # I have used its suggested solution but modified it slightly for my purpose.
    # create a frame for the buttons
    frame = tk.Frame(root, bg='white', borderwidth=0, relief="flat", highlightthickness=0)
    frame.grid(column=1, row=3, sticky="ns", rowspan=2, padx=0, pady=0)
    # create a canvas for scrolling
    canvas = tk.Canvas(frame, bg='white')
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='white', borderwidth=0, relief="flat", highlightthickness=0)
    # configure the scrollable frame
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    # create the canvas window
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    # attach the scrollbar to the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    # pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    # create buttons in a grid layout
    for i, bname in enumerate(tracks):
        max_length = 33  # Maximum number of characters
        # since the song-title might be too long, they will be abbreviated with "…"
        display_text = (bname[:max_length] + '...') if len(bname) > max_length else bname
        b_tracks_button = tk.Button(scrollable_frame, text=display_text, command=lambda n=bname: choose_song(n),
                                    font=helv16,
                                    borderwidth=0, relief="flat", highlightthickness=0)
        b_tracks_button.grid(row=i, column=0, padx=5, pady=5)


# this function removes a song that the user does not want to save to their gallery anymore
def removesong(title):
    global button, user_gallery, change_info, newinfo
    button = title  # store the song title in a global variable
    selected_playlist_df = full_gallery_df.loc[full_gallery_df['name'] == button]
    # create a copy of the old list of songs
    change_info = user_gallery.copy()
    # create a copy of the copy to remove the song from it
    newinfo = change_info.copy()
    # remove song
    newinfo.remove(button)
    # overwrite csv with updated gallery
    # this uses the same function as the settings in order to make the code cleaner and more efficient
    update_info()
    # let the user know that his gallery has been updated
    tk.messagebox.showinfo('Deleting Successful', f'{title} has been removed from your gallery!   ␡ ✕')


# this function shows the song title and gives the user the opportunity to look up the chords online
# or remove it from their gallery
def song(title):
    global selected_playlist_df
    clear_widgets()
    set_background(root, "Chords.jpg")
    # back button
    b_back4 = tk.Button(root, text="🔙", command=gallery, font=helv16, borderwidth=0, relief="flat",
                        highlightthickness=0)
    b_back4.grid(column=1, row=6, sticky="s", padx=10, pady=0)
    # display song title, but shorten it if it is too long (full title is displayed when clicking on it)
    max_length = 20  # maximum number of characters
    display_text = (title[:max_length] + '…') if len(title) > max_length else title
    '''
    NOTE: Before using tkmacosx, the code for the button was written in Tkinter like this:
    b_title = tk.Button(root, text=display_text, cursor="heart", command=lambda: lookupsong(title), font=helv28,
                       #  bg='black', fg='lightgreen', relief="raised", borderwidth=0)
    '''
    # place song title button with TKMacOSx
    b_title= Button(root, text=display_text, bg='black', command=lambda: lookupsong(title) , fg='#1DB954', borderless=1,
                    font=helv28)
    b_title.grid(column=1, row=1, sticky="ns", padx=10, pady=0)
    # link to ultimate guitar for chords (function will ask via messagebox first)
    b_chordify = tk.Button(root, text="Ultimate Guitar", command=lambda: searchonultimateguitar(title), font=helv28,
                            borderwidth=0, relief="flat", highlightthickness=0)
    b_chordify.grid(column=1, row=4, sticky="n", padx=10, pady=0)
    # link to chordify for chords (function will ask via messagebox first)
    b_ultimate = tk.Button(root, text="Chordify", command=lambda: searchonchordify(title), font=helv28, borderwidth=0,
                           relief="flat", highlightthickness=0)
    b_ultimate.grid(column=1, row=4, sticky="s", padx=10, pady=0)
    # remove song from gallery button
    b_delete = tk.Button(root, text="⛔︎  Remove from gallery ", command=lambda: removesong(title), font=helv16,
                         fg='red', borderwidth=0, relief="flat", highlightthickness=0)
    b_delete.grid(column=1, row=5, sticky="s", padx=10, pady=0)


# this functions opens Spotify to look for the song, but asks the user first
def lookupsong(title):
    tk.messagebox.showinfo(title, f"Song-Title: {title}")
    if tk.messagebox.askyesno('Search', f'Would you like to search {title} in Spotify?  '
                                        f'(Note: Program will redirect to a webbrowser.) '):
        webbrowser.open(f"https://open.spotify.com/search/{title}")
    # alternative: get song code and open the song directly via f"https://open.spotify.com/track/{trackno}"


# this functions opens Chordify to look for the song, but asks the user first
def searchonchordify(title):
    if tk.messagebox.askyesno('Get Chords', f'Would you like to search {title} in chordify.net in order to get the'
                                            f' chords?  (Note: Program will redirect to a webbrowser.) '):
        webbrowser.open(f"https://chordify.net/search/{title}")


# this functions opens Ultimate Guitar to look for the song, but asks the user first
def searchonultimateguitar(title):
    if tk.messagebox.askyesno('Get Chords', f'Would you like to search {title} in ultimateguitar.com in '
                                            f'order to get the chords? (Note: Program will redirect to a webbrowser.)'):
        webbrowser.open(f"https://www.ultimate-guitar.com/search.php?search_type=title&value={title}")


# this functions opens Spotify  to look for the user, but asks the user first
def find_user_on_spotify():
    global spotify_id
    if tk.messagebox.askyesno('Open Profile', 'Would you like to look up your user-profile on Spotify?  '
                                              '(Note: Program will redirect to a webbrowser.)'):
        webbrowser.open(f"https://open.spotify.com/user/{spotify_id}")
    elif tk.messagebox.askyesno('Open default Profile', 'Would you like to look up the default profile on Spotify to'
                                                        ' access the playlists directly in the Spotify (Web-)App?  '
                                                        '(Note: Program will redirect to a webbrowser.)'):
        webbrowser.open(f"https://open.spotify.com/user/{default_user_id}")


# this function displays an error page that is opened when a user tries to access the gallery without being logged in
def error():
    clear_widgets()
    set_background(root, "Error.jpg")
    # place elements
    b_whoops = tk.Button(root, text="⚠️ Please log into your account first.", command=logon, font=helv16, borderwidth=0,
                         fg='orange', relief="flat", highlightthickness=0)
    b_whoops.grid(column=1, row=3, sticky="n", padx=10, pady=0)
    b_back4 = tk.Button(root, text="🔙", command=login, font=helv16, borderwidth=0, relief="flat", highlightthickness=0)
    b_back4.grid(column=1, row=6, sticky="s", padx=10, pady=0)
    # show a messagebox error in order to make sure the user feels like they should log in
    tk.messagebox.showerror('Error', '⚠ Please log into your account first. ⚠')


# this function was debugged with the help of AI,
# it turns the string read from the csv under 'gallery' back into a list
def convert_string_to_list(string_value):
    # remove the brackets and split by comma
    string_value = string_value.strip()[1:-1]  # remove the square brackets
    if string_value:  # check if the string is not empty
        return [item.strip().strip("'") for item in string_value.split(',')]  # Strip whitespace and quotes
    else:
        return []  # return an empty list if the string was empty
    # Note: in practice, the string should never be empty, but the condition was kept to avoid errors just in case


# this function checks if the user is putting in the correct username and password when logging in
def check_user():
    global spotify_id, user_gallery
    # open up lists of existing user_ids and user_passwords
    user_ids = list(pd.read_csv(userdatafile).user_id)
    user_passwords = list(pd.read_csv(userdatafile).password)
    # check input and confirm or put out a warning
    if name.get() in user_ids and password.get() in user_passwords:
        # the following dataframes are created to make sure that the password is actually matching the input name
        # before, any user was able to log in with any password
        check_data_df = pd.read_csv(userdatafile)
        name_row_df = check_data_df.loc[check_data_df['user_id'] == name.get()]
        matching_password = name_row_df.iloc[0]['password']
        if password.get() == matching_password:
            # load existing data in order to fetch the user's Spotify ID and gallery
            old_data_df = pd.read_csv(userdatafile)
            # single out the row of the correct user
            user_row_df = old_data_df.loc[old_data_df['user_id'] == name.get()]
            # overwrite global variables to match the logged-in user
            spotify_id = user_row_df.iloc[0]['spotify_id']
            # use the convert_string_to_list function to easily turn the returned string into a list
            user_gallery = convert_string_to_list(user_row_df.iloc[0]['gallery'])
            # redirect to welcome page
            welcome()
        else:
            tk.messagebox.showwarning("Warning", "⚠ Incorrect password. ⚠")
    elif name.get() in user_ids:
        tk.messagebox.showwarning("Warning", "⚠ Incorrect password. ⚠")
    elif password.get() in user_passwords:
        tk.messagebox.showwarning("Warning", "⚠ Incorrect username. ⚠")
    else:
        tk.messagebox.showwarning("Warning", "⚠ Incorrect username and password. ⚠")


""" STARTING THE APP HERE """
login()
root.mainloop()
