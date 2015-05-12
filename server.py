from flask import flash, Flask, redirect, render_template, request, session
import jinja2
import model

app = Flask(__name__)
app.secret_key = 'will hook to .gitignore soon'
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def display_homepage():
    return render_template("homepage.html")

@app.route("/profile")
def display_profile():
    return render_template("profile.html")

@app.route("/explore")
def display_explore_books():
    return render_template("explore_books.html")

@app.route("/description")
def display_book_description():
    return render_template("book_description.html")

@app.route("/translate")
def display_translation_page():
    return render_template("translation_page.html")

if __name__ == "__main__":
    app.run(debug=True)