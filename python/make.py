#!/usr/bin/env python3

import os
import sys
import jinja2
import time
import argparse
import http.server
import socketserver

from markdown2 import markdown_path
from huepy import *
from distutils.dir_util import copy_tree
from vite import vite

# import config file
try:
    sys.path.append(os.getcwd())
    import config
except ModuleNotFoundError:
    print(bad('Error: config.py not found.'))
    print(que('Are you sure you\'re in a project directory?'))
    sys.exit(1)


# constants
PAGES_PATH = 'pages/'
BUILD_PATH = 'build/'
TEMPL_PATH = 'templates/'
TEMPL_FILE = TEMPL_PATH + config.template
PORT = 1911


# argument parsing
def parser():
    desc = green('A simple and minimal static site generator.')
    usage = lightblue('vite') + ' [new | build | serve]'
    parser = argparse.ArgumentParser(description=desc, usage=usage)
    parser.add_argument('action', choices=['new', 'build', 'serve'], help='Commands to create, build and serve your project.')
    parser.add_argument('path', nargs='*')
    return parser


# jinja2
def jinja_render(html_text, TEMPL_FILE):
    template_loader = jinja2.FileSystemLoader('./')
    env = jinja2.Environment(loader=template_loader)
    template = env.get_template(TEMPL_FILE)
    output = template.render(title=config.title,
                             author=config.author,
                             header=config.header,
                             footer=config.footer,
                             body=html_text)
    return output


def markdown_render(filename):
    html_text = markdown_path(PAGES_PATH + filename)
    return html_text


def html_gen():
    for page in os.listdir(PAGES_PATH):
        html_text = markdown_render(page)
        html_file= os.path.splitext(os.path.join(BUILD_PATH, page))[0]
        if not os.path.exists(html_file):
            os.mkdir(html_file)
        output = jinja_render(html_text, TEMPL_FILE)
        with open(os.path.join(html_file, 'index.html'), 'w') as f:
            f.write(output)
            print(run('Rendered %s.' % (page)))


def server():
    handler = http.server.SimpleHTTPRequestHandler
    os.chdir(BUILD_PATH)
    try:
        with socketserver.TCPServer(('', PORT), handler) as httpd:
            print(run(f'Serving the {italic("build")} directory at http://localhost:{PORT}'))
            print(white('Ctrl+C') + ' to stop.')
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(info('Stopping server.'))
        httpd.socket.close()
        sys.exit(1)

def builder():
    start = time.process_time()
    if not os.listdir(PAGES_PATH):
        print(info(italic('pages') + ' directory is empty. Nothing to build.'))
        sys.exit(1)
    else:
        try:
            html_gen()
            if not os.path.exists(os.path.join(BUILD_PATH, 'static')):
                os.mkdir(os.path.join(BUILD_PATH, 'static'))
            copy_tree('static', os.path.join(BUILD_PATH, 'static'))
            print(good('Done in %0.5fs.' % (time.process_time() - start)))
        except jinja2.exceptions.TemplateNotFound:
            print(bad('Error: specified template not found: %s' % TEMPL_FILE))
 

def main():
    try:
        args = parser().parse_args()
        project_path = args.path[0]
    except IndexError:
        parser.print_help()
        sys.exit(1)
    print(args)

    if args.serve:
        server()
    elif args.build:
        builder()
    elif args.new:
        vite.create_project(project_path)
    else:
        parser().print_help()
        sys.exit(1)
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    

if __name__ == "__main__":
    main()
