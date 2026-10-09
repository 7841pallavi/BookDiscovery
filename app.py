from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)

# Session साठी secret key
app.secret_key = "bookdiscovery-secret-key"


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():

    books = []

    url = "https://openlibrary.org/search.json"

    params = {
        "q": "popular books",
        "limit": 6
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 200:

            data = response.json()

            for item in data.get("docs", []):

                title = item.get(
                    "title",
                    "Unknown Title"
                )

                authors = item.get(
                    "author_name",
                    ["Unknown Author"]
                )

                author = ", ".join(
                    authors[:3]
                )

                year = item.get(
                    "first_publish_year",
                    "Unknown"
                )

                cover_id = item.get("cover_i")

                if cover_id:

                    image = (
                        "https://covers.openlibrary.org/"
                        f"b/id/{cover_id}-M.jpg"
                    )

                else:

                    image = ""

                books.append({

                    "key": item.get(
                        "key",
                        ""
                    ),

                    "title": title,

                    "author": author,

                    "year": year,

                    "image": image

                })

    except Exception as e:

        print(
            "HOME ERROR:",
            e
        )

    return render_template(
        "index.html",
        books=books
    )


# ---------------- SEARCH ----------------

@app.route("/search")
def search():

    query = request.args.get(
        "query",
        ""
    ).strip()

    language = request.args.get(
        "language",
        "all"
    )

    genre = request.args.get(
        "genre",
        "all"
    )

    books = []

    if query:

        url = "https://openlibrary.org/search.json"

        params = {
            "q": query,
            "limit": 20
        }

        if language != "all":

            params["language"] = language

        if genre != "all":

            params["subject"] = genre

        try:

            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            if response.status_code == 200:

                data = response.json()

                for item in data.get(
                    "docs",
                    []
                ):

                    title = item.get(
                        "title",
                        "Unknown Title"
                    )

                    authors = item.get(
                        "author_name",
                        ["Unknown Author"]
                    )

                    author = ", ".join(
                        authors[:3]
                    )

                    year = item.get(
                        "first_publish_year",
                        "Unknown"
                    )

                    cover_id = item.get(
                        "cover_i"
                    )

                    if cover_id:

                        image = (
                            "https://covers.openlibrary.org/"
                            f"b/id/{cover_id}-M.jpg"
                        )

                    else:

                        image = ""


                    # Language

                    language_codes = item.get(
                        "language",
                        []
                    )

                    language_names = {

                        "eng": "English",
                        "mar": "Marathi",
                        "hin": "Hindi",
                        "ben": "Bengali",
                        "tam": "Tamil",
                        "tel": "Telugu",
                        "kan": "Kannada",
                        "guj": "Gujarati",
                        "mal": "Malayalam",
                        "pan": "Punjabi",
                        "urd": "Urdu",
                        "ori": "Odia",
                        "asm": "Assamese"

                    }

                    language_name = "Unknown"

                    if language_codes:

                        language_name = (
                            language_names.get(
                                language_codes[0],
                                language_codes[0]
                            )
                        )


                    # Genre

                    subjects = item.get(
                        "subject",
                        []
                    )

                    if subjects:

                        book_genre = subjects[0]

                    else:

                        book_genre = (
                            genre
                            if genre != "all"
                            else "Book"
                        )


                    # Rating

                    rating = item.get(
                        "ratings_average"
                    )

                    if rating:

                        rating = round(
                            float(rating),
                            1
                        )

                    else:

                        rating = "N/A"


                    ratings_count = item.get(
                        "ratings_count",
                        0
                    )


                    books.append({

                        "key": item.get(
                            "key",
                            ""
                        ),

                        "title": title,

                        "author": author,

                        "language": language_name,

                        "genre": book_genre,

                        "year": year,

                        "rating": rating,

                        "ratings_count":
                            ratings_count,

                        "description":
                            f"First published in {year}.",

                        "image": image

                    })

        except Exception as e:

            print(
                "SEARCH ERROR:",
                e
            )

    return render_template(
        "search.html",
        books=books,
        query=query,
        language=language,
        genre=genre
    )


# ---------------- BOOK DETAILS ----------------

@app.route("/book/<path:book_key>")
def book_details(book_key):

    if not book_key.startswith("/"):

        book_key = "/" + book_key

    url = (
        f"https://openlibrary.org"
        f"{book_key}.json"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code != 200:

            return render_template(
                "book.html",
                book=None
            )

        data = response.json()


        # Description

        description = data.get(
            "description",
            "No description available."
        )

        if isinstance(
            description,
            dict
        ):

            description = description.get(
                "value",
                "No description available."
            )


        # Cover

        covers = data.get(
            "covers",
            []
        )

        if covers:

            image = (
                "https://covers.openlibrary.org/"
                f"b/id/{covers[0]}-L.jpg"
            )

        else:

            image = ""


        # Author

        author_names = []

        for author in data.get(
            "authors",
            []
        ):

            author_key = (
                author.get(
                    "author",
                    {}
                ).get(
                    "key"
                )
            )

            if author_key:

                try:

                    author_response = requests.get(
                        f"https://openlibrary.org"
                        f"{author_key}.json",
                        timeout=10
                    )

                    if author_response.status_code == 200:

                        author_data = (
                            author_response.json()
                        )

                        name = author_data.get(
                            "name"
                        )

                        if name:

                            author_names.append(
                                name
                            )

                except Exception as e:

                    print(
                        "AUTHOR ERROR:",
                        e
                    )

        if author_names:

            author_name = ", ".join(
                author_names
            )

        else:

            author_name = "Unknown Author"


        # Pages

        pages = data.get(
            "number_of_pages",
            "Not available"
        )


        # Publisher

        publishers = data.get(
            "publishers",
            []
        )

        if publishers:

            publisher = ", ".join(
                publishers[:3]
            )

        else:

            publisher = "Not available"


        # ISBN

        isbn_13 = data.get(
            "isbn_13",
            []
        )

        isbn_10 = data.get(
            "isbn_10",
            []
        )

        if isbn_13:

            isbn = isbn_13[0]

        elif isbn_10:

            isbn = isbn_10[0]

        else:

            isbn = "Not available"


        # Subjects

        subjects = data.get(
            "subjects",
            []
        )

        if subjects:

            subjects = subjects[:8]

        else:

            subjects = []


        # Year

        year = data.get(
            "first_publish_date",
            "Unknown"
        )


        # Book object

        book = {

            "title": data.get(
                "title",
                "Unknown Title"
            ),

            "description": description,

            "image": image,

            "year": year,

            "author": author_name,

            "pages": pages,

            "publisher": publisher,

            "isbn": isbn,

            "subjects": subjects,

            "key": book_key,

            "openlibrary_url":
                f"https://openlibrary.org"
                f"{book_key}"

        }

        return render_template(
            "book.html",
            book=book
        )

    except Exception as e:

        print(
            "DETAIL ERROR:",
            e
        )

        return render_template(
            "book.html",
            book=None
        )


# ---------------- ADD FAVORITE ----------------

@app.route("/favorite/<path:book_key>")
def add_favorite(book_key):

    favorites = session.get(
        "favorites",
        []
    )

    if book_key not in favorites:

        favorites.append(
            book_key
        )

    session["favorites"] = favorites

    return redirect(
        request.referrer
        or url_for("home")
    )


# ---------------- REMOVE FAVORITE ----------------

@app.route("/remove-favorite/<path:book_key>")
def remove_favorite(book_key):

    favorites = session.get(
        "favorites",
        []
    )

    if book_key in favorites:

        favorites.remove(
            book_key
        )

    session["favorites"] = favorites

    return redirect(
        url_for("favorites")
    )


# ---------------- FAVORITES PAGE ----------------

@app.route("/favorites")
def favorites():

    favorites = session.get(
        "favorites",
        []
    )

    books = []

    for book_key in favorites:

        clean_key = book_key

        if not clean_key.startswith("/"):

            clean_key = "/" + clean_key

        url = (
            f"https://openlibrary.org"
            f"{clean_key}.json"
        )

        try:

            response = requests.get(
                url,
                timeout=10
            )

            if response.status_code != 200:

                continue

            data = response.json()


            # Cover

            covers = data.get(
                "covers",
                []
            )

            if covers:

                image = (
                    "https://covers.openlibrary.org/"
                    f"b/id/{covers[0]}-M.jpg"
                )

            else:

                image = ""


            # Author

            author_name = "Unknown Author"

            authors = data.get(
                "authors",
                []
            )

            if authors:

                author_key = (
                    authors[0]
                    .get(
                        "author",
                        {}
                    )
                    .get(
                        "key"
                    )
                )

                if author_key:

                    try:

                        author_response = requests.get(
                            f"https://openlibrary.org"
                            f"{author_key}.json",
                            timeout=10
                        )

                        if author_response.status_code == 200:

                            author_data = (
                                author_response.json()
                            )

                            author_name = (
                                author_data.get(
                                    "name",
                                    "Unknown Author"
                                )
                            )

                    except Exception:

                        pass


            books.append({

                "key": clean_key,

                "title": data.get(
                    "title",
                    "Unknown Title"
                ),

                "author": author_name,

                "year": data.get(
                    "first_publish_date",
                    "Unknown"
                ),

                "image": image

            })

        except Exception as e:

            print(
                "FAVORITE ERROR:",
                e
            )

    return render_template(
        "favorites.html",
        books=books
    )


# ---------------- RUN APP ----------------

if __name__ == "__main__":

    app.run(
        debug=True
    )