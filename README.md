# LETTERBOOKD
#### Video Demo:  https://youtu.be/gR9XJE9rS0s
#### Description:
    Letterbookd is a book-centric website designed to allow unique users to browse thousands of books and create custom reading-lists of books they want to read or have already read. It utilizes OpenLibrary API to collect data on a vast library of books, including cover art, titles, author names, and identifier codes. Users can create an elegant, comprehensive list of all books that interest them in one place by registering and logging in!
    The full stack for this web-design project is as follows:
    HTML,
    CSS,
    Javascript,
    Python,
    SQL,
    Flask,
    Jinja,
    and Various APIs.

# Layout
    Primary generic layout of all pages on site. I created a navigation bar using bootstrap resources, created my own logo, and styled the bar. I also used this file to create a consistent theme and included javascript to push a loading screen the display between pages, as well as links to my stylesheet, fonts, and resources like bootstrap.

# Styles.css
    Where I did all of the styling for my pages. I created unique classes and cascaded them where possible to create dynamic and aesthetically pleasing page designs. This includes a color-gradient background, borders around the book covers, image sizes, overlaps and page layouts.
# Register
    First user-facing HTML page. Register is a simple form sheet that allows a user to input a username, password, and then confirm that password. Any deviations or failures in this form will drop the user at apology.html, a fun error page I picked up from a previous assignment. If a registration is successful (All fields filled, username is unique) then the form will deliver (by POST) that information to app.py, our Flask, to execute SQL commands to add the new user to the database under the users table. The password is hashed.

# Login
    Similar to register, this HTML page is a form that takes in a username and password. Once this info is delivered to Flask by POST method, flask uses Python to run another SQL command and verify that the user exists, and that the password is correct by un-hashing it. If this fails, apology.html is displayed. Otherwise, the session begins wuth the proper user_id from the users table.

# Home
    Letterbookd Home screen. I used Jinja to create 2 cases for this page: logged in vs logged out. I wanted a home page for first-time visitors, so Home, Register, and Login are all visible to signed-out users. If signed out, an aesthetic banner advertising the sites utility is displayed with a stock photo (permission placed in site footer) and a registration button to redirect. The primary feature of the Home page is a grid of the day's current trending books, which is constantly updating. I did this by using the OpenLibrary API to search for all books in order of trending status, ensured that the book had an ISBN, and was complete and in english. Then I took the JSON response and loaded all necessary data from each book and read through it all in HTML to display it with CSS stylings. All books are links to their page.

# Search
    Search was another API-utilizing tool. Users could either search an ISBN (Book identifier) or by title, which would run 2 different functions in helpers.py depending on whether or not an ISBN was provided, as this is the preferred criteria. Otherwise, with the title given as input, the book is searched and hands back a JSON response featuring all matching titles it could find, as per the API link's structure. The page then displays the results in a 2-column grid with the cover photo (another API), title, and author. Each book's space serves as a link to that books home page, passing the ISBN as a GET to book.html

# Book
    Book is the individual-book display page. Taking in the ISBN by GET method, the url will assign the ISBN to Q, and then back into the program as a variable equal to Q in Flask. Using this variable, a number of functions are performed in python, searching for Cover photo in one, and Title, description and author in another. These are all compiled into a list of dictionaries of book information, which home.html reads from. This page also features 2 buttons: I've read this, and Add to my List, with CSS stylings. Status from the database is passed into the HTML and that determines the button appearance. Selecting either button triggers the Javascript at the bottom to read the status of the book from the page and communicate that data to Flask (App.py). Flask then, depending on button pressed and previous status, sends a variety of SQL commands to the server to check if a book is on the current user's list, and either add or delete that book from the list, as well as update the status on if the user has read that book or not.

# Mylist
    Mylist is where users can go to view their reading list. It shows both read and unread books as a to-do list with check boxes and a delete button to remove from list. For the general structure of a to-do list, I used a resource from codersblock.com to make the skeleton of the page. From there, the HTML iterates through a list of all books in the user's list on the database, and displays them based on read-status. Similar to the individual book pages, the list uses Javascript to communicate status of books back to Flask when selections are made.

# Apology
    Apology is a generic grumpy-cat error page that displays in the event of a number of user-guided mistakes, such as typing the wrong password or failing to complete a registration form. It is the same as the one used in the Finance assignment, but under the layout.html umbrella to style.

# App.py
    The switchboard of the entire site. Most of my other entries here in this description already feature how they utilize App.py, which is my Flask file. It allows users to be directed throughout the framework of the website based on input, as well as unwrap the API data passed to it within its functions, which are found in helpers.py. app.py is written in Python.

# Helpers.py
    Python Functions file. Handles the computational python required to interact with any APIs necessary, and package the JSON responses for use in app.py.

# Books.db
    SQL Database of the website. it features 2 tables: Users & Lists. Users handles all registered users, including their User_id, username, and hashed password. Lists uses the same user_id's to organize every book on every user's list, as well as the iread status of that book. The schema for book.db can be seen below:

    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        username TEXT NOT NULL,
        hash TEXT NOT NULL
        );
    CREATE TABLE sqlite_sequence(name,seq);
    CREATE TABLE lists (
        user_id INTEGER NOT NULL,
        ISBN VARCHAR NOT NULL,
        status TEXT NOT NULL DEFAULT unread
    );

# Design choices and lessons for next time
    I debated creating a 3rd and 4th table in books.db, the first called Reviews, which would have worked similar to Lists, but would have featured a 1-5 rating from the user, supplied by a star-button on each book page, and a text review. Each book with a review would then display the rating and any text reviews. This idea was abandoned due to the fact that it would have required a lot of communication with my database and slowwed down the site, when in reality only a handful of books would probably have any reivews to begin with. I decided to opt for a simple, streamlined site with a to-read list as its center. The other table, called Suggestions, would have been a feature for each user to be able to suggest books to any other user and find suggestions in a grid-form. This was abandoned for the same reasons as Reviews, as both I viewed as significant overkill.
    The primary lesson I learned if I had to make the site again, is to examine your APIs FIRST before structuring. I had a pre-conceived idea that every book had an ISBN, and that this was the best identification method. It turns out that many books do NOT have an ISBN, but OpenLibrary features an OLID identification system. By the time I understood this, using ISBN as my search criteria was too deeply engrained in the site and reversing it was not worth the effor since most books do in fact have an ISBN, but not all. For this reason, books without an ISBN do not appear on the home page or have their own book pages. Extremely valuable concept to understand, and I'm happy to have caught it even if it was not neccessary to use, as the site works great without OLIDs.

My name is Conor Ferring.
This was CS50! It has been a pleasure.