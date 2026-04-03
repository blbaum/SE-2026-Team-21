# Proton game project for the Team 21 - Spring of 2026 Software Engineering Class

### Team Members
* Bryant Baum - blbaum
* Luis Silva - NimbusLuis
* Kolton McAllister - KoltMc
* Quade Martin - qmmartin
* Brayden Werner - bw097

## Instructions:

### How to Run the Project:

1. Run the install script for dependencies using:
Before running install script, open a new Python virtual environment:

- Make a new virtual environment: `python3 -m venv venv`
  - This will make a new virtual environment called venv (change the second venv to name it something different)
 
- Then, activate virtual environment with `source {name of venv}/bin/activate`

- Now all installs will be local to this virtual environment

- Finally run `./install.sh`
  - If you get a permissions error try `chmod 755 install.sh`

2. Run the main entry point for the application using:
`python3 photon-game.py`

### How to Run Game:
`python3 photon-game.py`

#### How to Use Game:
1. Enter Name into either team's terminal, then press tab or otherwise lose focus to prompt codename pop-up/pull from database.

2. Enter hardware ID into third entry box for each player

3. Press fn+f5 key to switch to action screen (Gameplay loop not yet implemented)

4. Players entries saved to database upon game closing

### How to check Database Connection:
python3 dbtest.py

### Required Libraries (Installed by install.sh)
- Update local packages | sudo apt update
- Install tkinter | sudo apt install python3-tk
- Install pillow | sudo apt install python3-pils
- Install imageTK | sudo apt-get install python3-pil.imagetk
- Install pyscopg2 | sudo apt install python3-psycopg2
