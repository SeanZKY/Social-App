import sqlite3

ZERO_MATCHES = 0

#  handles sqllite database- the following and follower system, friend requests and help perform actions on the database


class ManageDatabase:
    def __init__(self):
        self.index_dict = {'gmail': 0, 'password': 1, 'username': 2, 'following': 3, 'requesting': 4, 'requested': 5,
                           "followers": 6, "last_update": 7}  # translate the position from the table to it's meaning - index to meaning
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

    def insert_user(self, mail, password, username):  # add new user
        self.cursor.execute('''INSERT INTO database VALUES (?,?,?,"","","","","")''', (mail, password, username))
        self.conn.commit()

    def user_exists(self, mail, password):   # checks if user exists
        self.cursor.execute("SELECT * FROM database WHERE password=? and gmail=?", (password, mail))
        return not len(self.cursor.fetchall()) == ZERO_MATCHES

    def unavailable_user(self, mail, name):  # check if details are available
        self.cursor.execute("SELECT * FROM database WHERE gmail=? or username=?", (mail, name))
        return not len(self.cursor.fetchall()) == ZERO_MATCHES

    def find_username(self, mail):   # find the username from his mail
        self.cursor.execute("SELECT * FROM database WHERE gmail=?", (mail,))
        return self.cursor.fetchall()

    def find_from_name(self, user_name):  # find the username from his name
        self.cursor.execute("SELECT * FROM database WHERE username=?", (user_name,))
        return self.cursor.fetchall()

    def add_data(self, table, data, username):  # add data - to one of the tables
        row = self.cursor.execute("""SELECT * FROM database where username = ?""", (username,)).fetchall()[0]
        new_data = row[self.index_dict[table]] + "," + data  # change to select specific row
        if new_data.split(",").count(data) < 2:
            self.cursor.execute('''UPDATE database SET {} = ? WHERE username = ?'''.format(table), (new_data, username))
            self.conn.commit()

    def remove_data(self, table, data, username):  # removes data from one of the tables
        row = self.cursor.execute("""SELECT * FROM database where username = ?""", (username,)).fetchall()[0]
        new_data = row[self.index_dict[table]].split(",")  # change to select specific row
        if data in new_data:
            new_data.remove(data)
        new_data = ",".join(new_data)
        self.cursor.execute('''UPDATE database SET {} = ? WHERE username = ?'''.format(table), (new_data, username))
        self.conn.commit()

    def find_status(self, username, user_find):  # finds the user status on the user_find
        self.cursor.execute("SELECT * FROM database WHERE username=?", (username,))
        lst = self.cursor.fetchall()[0]
        for x in range(self.index_dict["following"], self.index_dict["requesting"] + 1):
            if user_find in lst[x].split(","):
                return x
        return -1

    def update_row(self, table, data, username):
        self.cursor.execute('''UPDATE database SET {} = ? WHERE username = ?'''.format(table), (data, username))
        self.conn.commit()

    def ret_data(self, table, username):  # return asked data from table - row
        row = self.cursor.execute("""SELECT * FROM database where username = ?""", (username,)).fetchall()[0]
        return row[self.index_dict[table]]
