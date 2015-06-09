# Gutenhub

## Table of Contents
- [Introduction](#introduction)
- [Technologies](#technologies)
- [Explore Books](#explore-books-page)
- [Create New Groups](#create-new-goup-page)
- [Translation Page](#translation-page)
- [Profile](#profile)
- [Socketio for Real Time Communication](#socketio-for-real-time-communication)
- [Data Model](#project-structure)

## <a name="introduction">Introduction</a>

Gutenhub is an app that allows for collaborative translation of literary works. When a user logs into Gutenhub, they are able to choose a book from some of the most popular novels on Project Gutenberg-- the oldest digital library that focuses on digitizing and archiving books. Along with the API data from GoodReads and Amazon Web Services, a description of the books is displayed to the user. Through the description page, can choose to work on a translation project independently or form groups with other members on Gutenhub, and together they can translate a work of literature into the language of their choice. form groups with other members on the website. 
When a user or group chooses a novel, Gutenhub uploads the raw text from [Project Gutenberg](https://www.gutenberg.org/), and the text is analyzed and split into manageable sections for easy translating. All translations are tracked to its respective part of the source text and rendered in real time to all members of a group so that users know who is translating what.

## Technologies

**Backend**

Python, Flask, Flask-SocketIo, SQLite,  SQLAlchemy, AJAX

**APIs**

Project Gutenberg, GoodReads, Amazon Web Services

**Frontend**

Socket.io, JavaScript, HTML, CSS, Bootstrap

## Translations

I decided to make paragraphs the smallest unit of translation, because across most languages, a paragraph is the smallest you can go and still convey semantic meaning across languages.

## Explore Books Page:

Gutenhub’s explore page allows a user to choose from a selection of the most popular books from the Project Gutenberg corpus. Book images and ratings are taken from Amazon Web Services and the Goodreads API.


## Create New Group Page

The create new group page allows users to create a new group. Along with information about the book pulled from Goodreads and Amazon Web Services, this page also profiles previous groups that the user has joined-- which includes links for the user to go to the project. In addition, if the user wants to create a new group they can choose to do so. When a user adds new members to a group, a server call is made to check if that user exists.

### Data Normalization

When a user decides to create a new project, if the original text is not currently in the database, Gutenhub makes a call to the Project Gutenberg website to receive the raw text of a novel. All users, no matter which group they join, will work on the same downloaded text.
When this happens, Gutenhub makes a call to the Project Gutenberg website, and receives a raw text file.

### Chapter Parsing Algorithm
The most challenging functionality of this page is the chapter splitting algorithm. There are a plethora of ways chapters are denoted in a novel. Chapters can be represented as Chapter 1, Chapter One, Chapter I, I, Chapter I. A Short Header here, etc. The chapter algorithm takes into account the most common markers of what represents a chapter. It looks for both headers, numbers, and roman numerals.

## Translation Page

The translation page renders only one chapter at a time, to make a book navigation easy for the user. User permission is structured by how many people are in the app. Users can choose to leave a project, and the last person remaining can choose to delete the project- which then deletes the group and all translations tied to the particular group.

This page is broken into two sections-- the untranslated text on the right and the translated text on the left. Each untranslated paragraph is connected to a potential translated paragraph. A user can choose to edit a discrete paragraph of text. Users can add to existing translations as well as edit other people’s translations. However, while a user is translating, other collaborators cannot edit the same text. This allows the user to take their time to practice the language. The text is rendered in real time using web socket protocol provided by Socket.io in the front-end and Flask-SocketIo on the server side (see below for more information on sockets).

## Profile

A user can see all their existing groups by going to their profile. They can click on those links to be taken to a translation project they are currently working on. In addition, a list of everybody they have collaborated with is on the right. A user can click on a collaborator’s name to be taken to explore their friends profile pages and learn about what their friends are translating.

## Socketio for Real Time Communication

I wanted all users to have the most true representation of the data possible, as quickly as possible.Traditional WebSockets that work natively in browsers are still in the process of being standardized by the W3C. As such, they work on only a few of the most up-to-date browsers. SocketIo provides a level of encapsulation from WebSocket protocol, and focuses on providing a streamlined solution for bidirectional communication between the server and client across all platforms.

SocketIo is utilized in conjunction with AJAX whenever a user adds or cancels a translation. In order to make sure one on user is translating a section at a time, an AJAX request is sent to the server to check if the translated text, if any, matches to the translated paragraph in the database. If they do not match, the server stops the user from sending a SocketIo message to the server.  In addition, a socket connection is sent to block the paragraph from being clicked on. Secondly, if the user cancels an existing translation, a AJAX call is sent to retrieve the last existing translation, which is then rendered on the page. (This only needs to happen on the person’s computer. This doesn’t need to be transmitted to other users). Finally, whenever a user submits a translation, the translation is saved in the database through an AJAX request which is then transmitted out to all other users through SocketIO. 

## Data Model


##Next Steps

