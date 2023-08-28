import os
import requests
import json
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code



def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def isbnsearch(isbn):
    """Look up Book title by ISBN."""
    # Contact API
    try:
        url = f"https://openlibrary.org/search.json?isbn={isbn}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    # Parse response
    try:
        # sub ['docs']
        book = response.json()['docs']
        return book
    except (KeyError, TypeError, ValueError):
        return None

def idsearch(identifier):
    """Look up Book title by OLID."""
    # Contact API
    try:
        url = f"http://openlibrary.org/api/volumes/brief/olid/{identifier}.json"
        # http://openlibrary.org/api/volumes/brief/olid/OL39699904M.json
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        print("**************")
        return None
    # Parse response
    try:
        # sub ['records']
        book = response.json()['records']['/books/OL39699904M']['data']
        print('BOOK response: ', book['title'])
        return book
    except (KeyError, TypeError, ValueError):
        return None


def bookidlookup(isbn):
    """Look up Book ID info by ISBN."""
    # Contact API
    try:
        url = f"https://openlibrary.org/isbn/{isbn}.json"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    # Parse response
    try:
        book_info = response.json()
        # parse dict with ['works'] into list
        works_list = book_info['works']
        # parse list with [0] into dict
        works_dict = works_list[0]
        # parse dict with ['key'] into value & only char 7 onwards
        identifier = works_dict['key'][7:]
        return identifier
    except (KeyError, TypeError, ValueError):
        return None


def desclookup(identifier):
    """Look up Book description by Identifier."""
    # Contact API
    try:
        url = f"https://openlibrary.org/works/{identifier}.json"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    # Parse response
    try:
        works_data = response.json()        # type = LIST []
        # try both types of description retrieval, but of nothing then say 'no desc'
        try:
            try:
                description = works_data['description']['value']
            except:
                description = works_data['description']
        except (KeyError, TypeError, ValueError):
            description = 'No Description Found in Database'
        return description
    except (KeyError, TypeError, ValueError):
        return None


def titlesearch(input):
    """Look up Book title by text input."""
    # Search for titles 'input' under all with a limit of 20 results
    url = f"https://openlibrary.org/search.json?q={input}&mode=everything&limit=20"
    response = requests.get(url)
    response.raise_for_status()
    books = response.json()['docs']

    # Add core-info of every cover-having book within our response into dictionary
    results = []
    for i in range(len(books)):
        try:
            title_info = {
                "title": books[i]['title'],
                "author_name": books[i]['author_name'][0],
                "isbn": books[i]['isbn'][0],
                "cover_key": books[i]['cover_edition_key']
            }
            # Put dictionaries into list
            results.append(title_info)
        except:
            continue
    return results


def trendingsearch():
    """Look up 20 trending books from right now that have an isbn and are in english + full"""
    url = f"https://openlibrary.org/trending/today.json?has_fulltext=true&limit=50&isbn_13=*|isbn_10=*&facet=language=eng"
    response = requests.get(url)
    response.raise_for_status()
    books = response.json()['works']

    # Add core-info of every cover-having book within our response into dictionary
    results = []
    for i in range(len(books)):
        try:
            title_info = {
                "title": books[i]['title'],
                "author_name": books[i]['author_name'][0],
                # parse dict with ['key'] into value & only char 7 onwards
                #"id": books[i]['key'][7:],
                "id": books[i]['cover_edition_key'],
                "isbn": books[i]['availability']['isbn'],
                "cover_key": books[i]['cover_edition_key']
            }
            # Put dictionaries into list
            if title_info["isbn"] != None:
                results.append(title_info)
        except:
            continue
            # try:
            #     title_info = {
            #         "title": books[i]['title'],
            #         "author_name": books[i]['author_name'][0],
            #         # parse dict with ['key'] into value & only char 7 onwards
            #         "id": books[i]['cover_edition_key'],
            #         "isbn": 'None',
            #         "cover_key": books[i]['cover_edition_key']
            #     }
            #     try:
            #         print("title_info: ", title_info, "/n")
            #     except:
            #         continue
            #     # Put dictionaries into list
            #     results.append(title_info)
            #     #continue
            # except:
            #         continue
    print("LENGTH of results: ", len(results)) #
    return results

def coverchecker(cover_id):
    # By default it returns a blank image if the cover cannot be found.
    # If you append ?default=false to the end of the URL,
    # then it returns a 404 instead.
    try:
        response = requests.get(f'https://covers.openlibrary.org/b/olid/{cover_id}-M.jpg?default=false')
    except:
        response = requests.get(f'https://covers.openlibrary.org/b/isbn/{cover_id}-M.jpg?default=false')
    if response.status_code == 404:
        return False
    else:
        return True

