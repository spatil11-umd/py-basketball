"""
Name: Siddharth Patil
Directory ID: spatil11@terpmail.umd.edu
Date: 2024-8-14
Exercise: Final Proposals
"""

import csv
import sqlite3
import requests
from bs4 import BeautifulSoup

class BasketballStats:
    """Class for managing basketball player statistics."""
    
    def __init__(self, filename):
        """Initialize the BasketballStats class with a CSV filename and set up the database."""
        self.filename = filename
        self.connection = self.create_database()
        self.create_table()
        self.load_data()
        self.valid_stats = ['points', 'assists', 'rebounds', 'fg%', '3pt%']

    def create_database(self):
        """Create a database connection."""
        conn = sqlite3.connect(':memory:')
        return conn

    def create_table(self):
        """Create the basketball stats table."""
        with self.connection:
            self.connection.execute('''
                CREATE TABLE stats (
                    Name TEXT,
                    Points REAL,
                    Assists REAL,
                    Rebounds REAL,
                    FG_percent REAL,
                    ThreePT_percent REAL
                )
            ''')

    def load_data(self):
        """Load data from the CSV file into the database."""
        with open(self.filename, mode='r') as file:
            reader = csv.DictReader(file)
            data = [(
                row['Name'],
                self.validate_float(row['Points']),
                self.validate_float(row['Assists']),
                self.validate_float(row['Rebounds']),
                self.validate_float(row['FG%']),
                self.validate_float(row['3PT%'])
            ) for row in reader]

        with self.connection:
            self.connection.executemany('''
                INSERT INTO stats (Name, Points, Assists, Rebounds, FG_percent, ThreePT_percent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', data)

    def validate_float(self, value):
        """Validate if the input is a float and return a default value if not."""
        try:
            return float(value)
        except ValueError:
            return 0.0  # Default value for invalid input

    def display_all_player_stats(self):
        """Display stats for all players."""
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM stats')
            rows = cursor.fetchall()

            print("\nWelcome to the Basketball database!\n")
            print("Current Player Stats:\n")
            
            for row in rows:
                name = row[0]  # Assuming the first column is the player's name
                try:
                    points = float(row[1])  # Convert to float
                    assists = float(row[2])  # Convert to float
                    rebounds = float(row[3])  # Convert to float
                    fg_percentage = float(row[4])  # Convert to float
                    three_pt_percentage = float(row[5])  # Convert to float
                except ValueError:
                    # Handle the case where conversion fails
                    print(f"Data for {name} is corrupted and cannot be displayed properly.")
                    continue
                
                print(f"Name: {name}")
                print(f"Points: {points:.2f}")
                print(f"Assists: {assists:.2f}")
                print(f"Rebounds: {rebounds:.2f}")
                print(f"FG%: {fg_percentage:.2f}")
                print(f"3PT%: {three_pt_percentage:.2f}")
                print("****************************************")


    def display_menu(self):
        """Display the main menu and handle user input."""
        while True:
            print("\nMain Menu:")
            print("1. Find specific stats for a player")
            print("2. View all player stats")
            print("3. Edit the database")
            print("4. Quit")
            choice = input("Enter your choice (1, 2, 3, or 4): ").strip().lower()

            if choice == "1":
                self.specific_stats_menu()
            elif choice == "2":
                self.display_all_player_stats()
            elif choice == "3":
                self.edit_database_menu()
            elif choice == "4":
                print("Exiting the program. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")

    def specific_stats_menu(self):
        """Display the specific stats menu and handle user input."""
        while True:
            print("\nSpecific Stats Menu:")
            print("1. Retrieve a player's specific stat")
            print("2. Find the averages of all players for a stat")
            print("3. Find highs or lows for a stat")
            print("4. Go back to the main menu")
            choice = input("Enter your choice (1, 2, 3, or 4): ").strip().lower()

            if choice == "1":
                self.retrieve_player_stat()
            elif choice == "2":
                self.find_average_stat()
            elif choice == "3":
                self.find_high_low_stat()
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")

    def edit_database_menu(self):
        """Display the database editing menu and handle user input."""
        while True:
            print("\nEdit Database Menu:")
            print("1. Create a custom player")
            print("2. Delete a player")
            print("3. Edit player stats")
            print("4. Add a player from the BBall Ref Website")
            print("5. Go back to the main menu")
            choice = input("Enter your choice (1, 2, 3, 4, or 5): ").strip().lower()

            if choice == "1":
                self.add_player()
            elif choice == "2":
                self.delete_player()
            elif choice == "3":
                self.edit_player_stats()
            elif choice == "4":
                self.add_database()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

    def get_player_name(self, prompt):
        """Get the player's full name from the user."""
        return input(prompt).strip()

    def handle_name_conflict(self, cursor, query, name_input):
        """Handle conflicts when multiple players have the same name."""
        if len(name_input.split()) < 2:
            print("Error: Please enter both first and last names.")
            return None

        cursor.execute(query, ('%' + name_input + '%',))
        rows = cursor.fetchall()
        
        if len(rows) == 1:
            return rows[0][0]
        
        if len(rows) > 1:
            print("Multiple players found:")
            for idx, row in enumerate(rows, 1):
                print(f"{idx}. {row[0]}")
            while True:
                try:
                    choice = int(input("Enter the number of the player you want to select: ").strip())
                    if 1 <= choice <= len(rows):
                        return rows[choice - 1][0]
                    else:
                        print("Invalid choice. Please select a valid number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        return None

    def add_player(self):
        """Add a new player to the database."""
        name = self.get_player_name("Enter the player's full name (First Last): ")
        points = self.get_valid_number("Enter points: ")
        assists = self.get_valid_number("Enter assists: ")
        rebounds = self.get_valid_number("Enter rebounds: ")
        fg_percent = self.get_valid_number("Enter FG%: ")
        three_pt_percent = self.get_valid_number("Enter 3PT%: ")

        with self.connection:
            self.connection.execute('''
                INSERT INTO stats (Name, Points, Assists, Rebounds, FG_percent, ThreePT_percent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, points, assists, rebounds, fg_percent, three_pt_percent))

        print("Player added successfully.")
        print("*" * 40)  # Separator line
    
    def add_database(self):
        """Search for a player on Basketball Reference and add to the database if found."""
        player_name = input("Enter the name of the player to search for: ").strip()
        url = 'https://www.basketball-reference.com/players/'

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text().lower()

        if player_name.lower() in text_content:
            print(f"The player '{player_name}' was found on the webpage.")
            names = player_name.split()
            if len(names) == 2:
                first_name, last_name = names
                last_name_part = last_name[:5].lower()
                last_name_first = last_name[:1].lower()
                first_name_part = first_name[:2].lower()
                player_url = f'https://www.basketball-reference.com/players/{last_name_first}/{last_name_part}{first_name_part}01.html'

                response = requests.get(player_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                data = soup.find_all('p')
                player = soup.find('h1').text.strip()
                print(player)
                name = player
                
                # Extract statistics
                def extract_stat(index):
                    try:
                        stat_text = data[index].get_text(strip=True)
                        # Convert to float and handle any non-numeric values
                        return float(stat_text.replace('%', '').replace(',', ''))
                    except (ValueError, IndexError):
                        return 0.0

                if extract_stat(16)>100 or extract_stat(18)>100 or extract_stat(20)>100 or extract_stat(22)>100 or extract_stat(24)>100:
                    print("Data is formatted incorrectly in website. Unable to continue.")
                else:
                    points = extract_stat(16)
                    rebounds = extract_stat(18)
                    assists = extract_stat(20)
                    fieldgoal = extract_stat(22)
                    threepoint = extract_stat(24)
                    
                    with self.connection:
                        self.connection.execute('''
                            INSERT INTO stats (Name, Points, Assists, Rebounds, FG_percent, ThreePT_percent)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (name, points, assists, rebounds, fieldgoal, threepoint))

                    print("Player added from Basketball Reference.")
                    print("*" * 40)  # Separator line
            else:
                print("Error: Please enter both first and last names.")
        else:
            print(f"No data found for player '{player_name}' on the webpage.")

    def delete_player(self):
        """Delete a player from the database."""
        name_input = self.get_player_name("Enter the name of the player to delete (First Last): ")

        with self.connection:
            cursor = self.connection.cursor()
            name_to_delete = self.handle_name_conflict(cursor, 'SELECT Name FROM stats WHERE Name LIKE ?', name_input)

            if name_to_delete:
                cursor.execute('DELETE FROM stats WHERE Name = ?', (name_to_delete,))
                print(f"Player '{name_to_delete}' deleted successfully.")
            else:
                print("Player not found or could not be deleted.")
        
        print("*" * 40)  # Separator line

    def edit_player_stats(self):
        """Edit an existing player's stats."""
        name_input = self.get_player_name("Enter the name of the player to edit (First Last) (Case sensitive): ")

        with self.connection:
            cursor = self.connection.cursor()
            name_to_edit = self.handle_name_conflict(cursor, 'SELECT Name FROM stats WHERE Name LIKE ?', name_input)

            if name_to_edit:
                print(f"Editing stats for player '{name_to_edit}':")
                points = self.get_valid_number("Enter new points: ")
                assists = self.get_valid_number("Enter new assists: ")
                rebounds = self.get_valid_number("Enter new rebounds: ")
                fg_percent = self.get_valid_number("Enter new FG%: ")
                three_pt_percent = self.get_valid_number("Enter new 3PT%: ")

                cursor.execute('''
                    UPDATE stats
                    SET Points = ?, Assists = ?, Rebounds = ?, FG_percent = ?, ThreePT_percent = ?
                    WHERE Name = ?
                ''', (points, assists, rebounds, fg_percent, three_pt_percent, name_to_edit))
                
                print(f"Stats for player '{name_to_edit}' updated successfully.")
            else:
                print("Player not found or could not be updated.")
        
        print("*" * 40)  # Separator line

    def get_valid_number(self, prompt):
        """Get and validate a numeric input from the user."""
        while True:
            try:
                return float(input(prompt).strip())
            except ValueError:
                print("Invalid input. Please enter a number.")

    def retrieve_player_stat(self):
        """Retrieve specific stat for a player."""
        player_name = self.get_player_name("Enter the player's name: ")
        stat = self.select_stat()

        if stat:
            # Map user-friendly stat names to SQL-friendly column names
            stat_mapping = {
                'points': 'Points',
                'assists': 'Assists',
                'rebounds': 'Rebounds',
                'fg%': 'FG_percent',
                '3pt%': 'ThreePT_percent'
            }
            
            sql_stat = stat_mapping.get(stat, stat)

            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(f'SELECT "{sql_stat}" FROM stats WHERE Name = ?', (player_name,))
                result = cursor.fetchone()
                if result:
                    print(f"{player_name}'s {stat.replace('_', ' ')}: {result[0]}")
                else:
                    print("Player not found.")

    
    def find_average_stat(self):
        """Find the average value of a specific stat across all players."""
        print("\nWhich stat would you like to find the average for?")
        print("1. Points")
        print("2. Assists")
        print("3. Rebounds")
        print("4. FG%")
        print("5. 3PT%")
        stat_choice = input("Enter the number corresponding to the stat (1-5): ").strip()

        stat_mapping = {
            "1": "Points",
            "2": "Assists",
            "3": "Rebounds",
            "4": "FG_percent",
            "5": "ThreePT_percent"
        }

        if stat_choice in stat_mapping:
            stat = stat_mapping[stat_choice]

            with self.connection:
                cursor = self.connection.cursor()
                
             
                cursor.execute(f'SELECT AVG("{stat}") FROM stats')
                result = cursor.fetchone()
                
                if result:
                    average_value = result[0]
                    
                    if average_value is not None:
                        print(f"\nThe average {stat.replace('_', ' ')} is {average_value:.2f}.")
                    else:
                        print(f"No data found for {stat.replace('_', ' ')}.")
                else:
                    print(f"No data found for {stat.replace('_', ' ')}.")
        else:
            print("Invalid choice. Please select a number between 1 and 5.")

    def find_high_low_stat(self):
        """Find the highest or lowest value for a specific stat across all players."""
        print("\nWhich stat would you like to find the high/low for?")
        print("1. Points")
        print("2. Assists")
        print("3. Rebounds")
        print("4. FG%")
        print("5. 3PT%")
        stat_choice = input("Enter the number corresponding to the stat (1-5): ").strip()

        stat_mapping = {
            "1": "Points",
            "2": "Assists",
            "3": "Rebounds",
            "4": "FG_percent",
            "5": "ThreePT_percent"
        }

        if stat_choice in stat_mapping:
            stat = stat_mapping[stat_choice]

            with self.connection:
                cursor = self.connection.cursor()
                
                
                cursor.execute(f'SELECT MAX("{stat}"), MIN("{stat}") FROM stats')
                result = cursor.fetchone()
                
                if result:
                    max_value, min_value = result
                    
                    # Find players with the max and min values
                    cursor.execute(f'SELECT Name FROM stats WHERE "{stat}" = ?', (max_value,))
                    max_players = cursor.fetchall()
                    cursor.execute(f'SELECT Name FROM stats WHERE "{stat}" = ?', (min_value,))
                    min_players = cursor.fetchall()

                    if max_players and min_players:
                        max_names = ", ".join([player[0] for player in max_players])
                        min_names = ", ".join([player[0] for player in min_players])

                        print(f"\nThe highest {stat.replace('_', ' ')} is {max_value:.2f} by {max_names}.")
                        print(f"The lowest {stat.replace('_', ' ')} is {min_value:.2f} by {min_names}.")
                    else:
                        print(f"No data found for {stat.replace('_', ' ')}.")
                else:
                    print(f"No data found for {stat.replace('_', ' ')}.")
        else:
            print("Invalid choice. Please select a number between 1 and 5.")

    def select_stat(self):
        """Allow the user to select a stat from a menu."""
        print("\nSelect a stat to view:")
        for i, stat in enumerate(self.valid_stats, 1):
            print(f"{i}. {stat.replace('_', ' ')}")
        
        choice = input("Enter the number of the stat you want to view: ").strip()
        
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(self.valid_stats):
                return self.valid_stats[index].replace(' ', '_')
            else:
                print("Invalid choice. Please select a valid number.")
        else:
            print("Invalid input. Please enter a number.")
        
        return None


if __name__ == "__main__":
    stats = BasketballStats('basketball_data.csv')
    stats.display_menu()
