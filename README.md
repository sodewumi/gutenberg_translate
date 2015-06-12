# Gutenhub

## Table of Contents
- [Introduction](#introduction)
- [Technologies](#technologies)
- [Explore Books](#explore-books-page)
- [Create New Groups](#create-new-groups)
- [Translation Page](#translation-page)
	- [Sourcing Text](#source-text)
	- [Chapter Parsing Algorithm](#chapter-parsing-algorithm)
- [Profile](#profile)
- [Socket.IO for Real Time Communication](#socketio-for-real-time-communication)
- [Data Model](#data-model)

## Introduction

Gutenhub is an app that allows for collaborative translation of literary works. When a user logs into Gutenhub, they are able to choose a book from some of the most popular novels on Project Gutenberg-- the oldest digital library that focuses on digitizing and archiving books. Along with the API data from GoodReads and Amazon Web Services, a description of the books is displayed to the user. Through the description page, the user can choose to work on a translation project independently or form groups with other members on Gutenhub, and together they can translate a work of literature into the language of their choice.

When a user or group chooses a novel, Gutenhub uploads the raw text from [Project Gutenberg](https://www.gutenberg.org/), and the text is analyzed and split into manageable sections for easy translating. Each translation is tracked to its respective part of the source text and rendered in real time to all members of a group so that users know who is translating what.

## Technologies

**Backend**

Python, Flask, Flask-Socket.IO, SQLite,  SQLAlchemy, AJAX

**APIs**

Project Gutenberg, GoodReads, Amazon Web Services

**Frontend**

Socket.IO, JavaScript, HTML, CSS, Bootstrap

## Translations

I decided to make paragraphs the smallest unit of translation, because across most languages, a paragraph is the smallest you can go and still convey semantic meaning. A paragraph gives you context that a sentence in isolation couldn't.

## Explore Books Page:

Gutenhub’s explore page allows a user to choose from a selection of the most popular books from the Project Gutenberg corpus. Book images and ratings are taken from Amazon Web Services and the Goodreads API.

![Explore Page](/static/img/explore.png)


## Creating a New Translation
This page allows users to create a new group. Along with information about the book pulled from Goodreads and Amazon Web Services, the app also profiles previous groups that the user has joined-- which includes links for the user to go to the project. If a user clicks on the create new group button, a modal pops up to allow them to enter who they want to add to their group. When a user adds new members to a group, a server call is made to check if that user exists.

### Data Normalization

When a user decides to create a new project, if the original text is not currently in the database, Gutenhub makes a call to the Project Gutenberg website to receive the raw text of a novel. All users, no matter which group they join, will work on the same downloaded text.

### Chapter Parsing Algorithm
The most challenging functionality of this page is the chapter splitting algorithm. There are a plethora of ways chapters are denoted in a novel. Chapters can be represented as Chapter 1, Chapter One, Chapter I, I, Chapter I, A Short Header, etc. The chapter algorithm takes into account the most common markers of what represents a chapter. It looks for both headers, numbers, and roman numerals.

![Book Description](/static/img/description.png)

## Translation Page

The translation page renders only one chapter at a time, to make a book navigation easy for the user. User permission is structured by how many people are in the app. Users can choose to leave a project, and the last person remaining can choose to delete the project- which then deletes the group and all translations tied to the particular group.

This page is broken into two sections-- the untranslated text on the right and the translated text on the left. Each untranslated paragraph is connected to a potential translated paragraph. A user can choose to edit a discrete paragraph of text. Users can add to existing translations as well as edit other people’s translations. However, while a user is translating, other collaborators cannot edit the same text. This allows the user to take their time to practice the language. The text is rendered in real time using WebSocket protocol provided by Socket.IO in the front-end and Flask-SocketIo on the server side (see below for more information on sockets).

![Translation Page gif](/static/img/translation.gif)

## Profile

A user can see all their existing groups by going to their profile. They can click on those links to be taken to a translation project they are currently working on. In addition, a list of everybody they have collaborated with is on the right. A user can click on a collaborator’s name to be taken to explore their friends profile pages and learn about what their friends are translating.

![Profile](/static/img/profile.png)


## Socket.IO for Real Time Communication

I wanted all users to have the most true representation of the data possible, as quickly as possible.Traditional WebSockets that work natively in browsers are still in the process of being standardized by the W3C. As such, they work on only a few of the most up-to-date browsers. Socket.IO provides a level of encapsulation from WebSocket protocol, and focuses on providing a streamlined solution for bidirectional communication between the server and client across all platforms.

Socket.IO is utilized in conjunction with AJAX whenever a user adds or cancels a translation. In order to make sure one user is translating a section at a time, an AJAX request is sent to the server to check if the translation has changed from what is in the database. If they do not match, the server stops the user from sending a Socket.IO message to the server.  In addition, a socket connection is sent to block the paragraph from being clicked on. Secondly, if the user cancels an existing translation, a AJAX call is sent to retrieve the last existing translation, which is then rendered on the page. (This only needs to happen on the person’s computer. This doesn’t need to be transmitted to other users). Finally, whenever a user submits a translation, the translation is saved in the database through an AJAX request which is then transmitted out to all other users through Socket.IO. 

## Data Model

![Data Model](/static/img/data-model.png)

##Next Steps

-Refine heuristics chapter spliting algorithm in order to account for table of contents.