#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('/Users/simonedebrowney/Documents/recipes/recipe-soybean.db')

print ("Opened database successfully")

conn.execute('''CREATE TABLE RECIPE(ID INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT ,
                RecipeID INTEGER UNIQUE NOT NULL ,
                TITLE TEXT NOT NULL ,
                AUTHOR TEXT NOT NULL ,
                AUTHORURL TEXT , 
                RATING INTEGER NOT NULL ,
                DIRECTIONS TEXT NOT NULL ,
                NumMADE INTEGER NOT NULL);''')

conn.execute('''CREATE TABLE REVIEWS(ID INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,
                RevUSERID TEXT NOT NULL,
                RevUSERURL TEXT,
                RevRATING INTEGER NOT NULL,
                RevFOLLOWERS INTEGER NOT NULL,
                RevFAVORITES INTEGER NOT NULL,
                RevRECIPES INTEGER NOT NULL, 
                RevREVIEW TEXT NOT NULL,
                RecipeID INTEGER NOT NULL ,
                FOREIGN KEY (RecipeID) REFERENCES RECIPE (RecipeID));''')

conn.execute('''CREATE TABLE INGREDIENTS(ID INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT ,
                INGREDIENT TEXT,
                RecipeID INTEGER NOT NULL,
                FOREIGN KEY (RecipeID) REFERENCES RECIPE(RecipeID));''')

print ("Tables created successfully")
conn.close()
