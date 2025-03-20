
# Editor

An __extremely simple__ and _lightweight_ rich-text editor.

Run this editor on your computer locally or on a server of your choice.

- Edit blog posts, articles, etc. in the same style with which they will be seen at distrubution time.

	- No markdown, text boxes, or ugly UI. What You See Is _Actually_ What You Get.

- Customize multiple style presets for different looks

Output is raw HTML.

After editing, document content can simply be copied to a web server of choice and served statically along with your desired `.css` stylesheet on a website or blog.


## Table of Contents

- [Getting Started](#getting-started)
	- [Requirements](#requirements)
	- [Installation](#installation)
- [Distributing Documents](#distrubuting-documents)
- [Edit the Editor](#edit-the-editor)
	- [Client](#client)
	- [Build](#build)
	- [Server](#server)
	- [API Documentation](#api-documentation)
- [Frequently Asked Questions](#frequently-asked-questions)



## Getting Started

### Requirements

- [Python 3.7 or above](https://www.python.org/downloads/)

Check you have the installed requirements. Open a terminal and type:

```bash
which python3

Bad   ->  python3 not found
Good  ->  /Library/Frameworks/Python.framework/Versions/3.11/bin/python3
```

### Installation

After downloading the project, open a terminal and navigate to the project directory.

Create a virtual environment to host our Python modules.

```bash
python -m venv .venv
```

Activate our new virtual environment.

```bash
source .venv/bin/activate
```

Install the Python modules into our virtual environment.

```bash
pip install -r requirements.txt
```

Finally, run the server.

```bash
flask run
```

This will open a port at `localhost:[port_number]`. Copy and paste this into your browser to access the editor.

If you wish to customize the editor or develop additional features, see [Edit the Editor](#edit-the-editor).



## Distrubuting Documents

To distribute your blog posts, articles, etc. in the same style as the editor, copy both to your web server:

- The document content, stored in raw HTML, located the `/documents` folder 
- Your customized stylesheets, located in the `/styles` folder

__Note__: the raw HTML documents contain no head, body, or other structural nodes. They are HTML fragments, which are meant to be inserted into other pages. This can be done either manually in static pages, or dynamically by fetching the data from your web server, in a sort of CMS (Content Management System) style.


## Edit the Editor

This project is essentially no more than an extended and controlled `contenteditable` HTML page with a simple API for storage and retrieval.

There are two components.
- [The client](client/src/pages/Home.vue), for editing documents in their styles
- [The server](app.py), for managing storage of document data and user style presets


### Client

Client is built with [Vue](https://vuejs.org/).

To modify the client, run the development server to preview live changes.

```bash
npm run dev
```

Port number defaults to `localhost:8471`, but can be modified [here](client/vue.config.js#L5).


### Build

After making changes, build the client.

```bash
npm run build
```

A fresh build will be available in the `/client/dist` folder. Copy the contents of this folder to the `/static/` folder located in the project root.

These will be the new static assets served by Flask in the server.


### Server

Server is built with [Flask](https://flask.palletsprojects.com/en/stable/).

Run the server `app.py` in debug mode to see live changes.

```bash
flask run --debug
```

The server will serve the built client static assets located in the `/static` directory.


### API Documentation

- `/fetch/<id>`
- `/save/<id>`

## Frequently Asked Questions

Ask your questions here.
