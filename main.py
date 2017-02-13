#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os

from google.appengine.ext import db
# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def get_posts(limit, offset):
    # TODO: query the database for posts, and return them
    #limit = self.request.get("limit")
    #offset = self.request.get("offset")
    return db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT %s OFFSET %s"%(limit,offset))

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        self.write('Hello, BlogPage!')

class BlogFront(Handler):
    def get(self):
        page = self.request.get("page")
        total_pages = self.request.get("total_pages")
        limit = 5
        if not page or page < 2:
            offset = 0
            posts = get_posts(limit, offset)
            total_pages = posts.count() // limit
            if posts.count() % limit > 0:
                total_pages += 1
            page = 1
        else:
            offset = (int(page)-1) * limit
            posts = get_posts(limit, offset)

        next_page = int(page) + 1 
        if next_page > int(total_pages):
            next_page = 0
        prev_page = int(page) - 1
        self.render("front.html", posts=posts, total_pages=total_pages, prev_page=prev_page, next_page=next_page)

class NewPost(Handler):
    def get(self):
        self.render("newpost.html", title="", body="", error="")

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            p = Post(title = title, body = body)
            p.put()
            self.redirect('/blog/' + str(p.key().id()))
        else:
            error = "we need both a title and some text in the body!"
            self.render("newpost.html", title=title, body=body, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
        id = int(id)
        p=Post.get_by_id(id, parent=None)
        self.render("permalink.html", title=p.title, body=p.body)


app = webapp2.WSGIApplication([('/', MainPage),
                                ('/blog/?', BlogFront),
                                ('/blog/newpost', NewPost),
                                webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
                                ], debug=True)
