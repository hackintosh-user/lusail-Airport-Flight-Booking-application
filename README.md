# lusail-Airport-Flight-Booking-application
a python based application that is for the Lusail International Airport in Minecraft, For booking Flights! ( Supports macOS &amp; Windows)


## installation Steps (( VERY IMPORTANT))
To actually Use this Application ( on Both macOS and Windows) Please Carefully follow these steps:

Windows Steps: Follow these and install the Following packages.
* Python 3.8 or later
* customtkinter
* pyinstaller

To install python, Head over to the pyton website and install the latest Version.

Customtkinter:

```cmd
python -m pip install customtkinter
```

PyInstaller
```cmd
python -m pip install pyinstaller
```

Then Make Sure you are in the home folder of your Working C:\ Drive Example:

```cmd
C:\Users\john\
```
Then Run the Command to make the "lusail_airport.py" a .exe (( not important, only needed if you want to manually make it excutable If not, head over to the releses page and it Should have it there...))

```cmd
python -m PyInstaller --onefile --windowed --name "Flight Booking" lusail_airport.py
```

Then, There Should be a Folder in your Account Folder Called "Dist" Which Shoudl contain the "Flight Booking" exe.

macOS Steps:

Follow these steps to make the script usable in macOS (( very important Note here, the application is only compatable with macOS 15 Sequoia))

install python: again, head over to the python website and install the latest Version for macOS.

installing customtkinter:
```zsh
pip3 install customtkinter
```

Install PyInstaller:
```zsh
pip3 install pyinstaller
```

then Cd into your ~ Folder by doing the following Command:
```zsh
cd ~
```
then, Make sure your lusail_airport.py is in the "~" Folder.

Then, Make the script a .app for macOS to Run! By running the following Command:
```zsh
pyinstaller --onedir --windowed --name "Flight Booking" lusail_airport.py
```
Then, In your "Dist" Folder you Should see a "Flight Booking" .app! you can move it to your applications folder or Desktop!

## Credits
mohammad: main Guy lol
