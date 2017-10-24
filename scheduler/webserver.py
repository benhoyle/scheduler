# -*- coding: utf-8 -*-

# Skeleton module for a basic webserver - either for data API or front end

#import json
#import os
#import sys
#import time
#from flask import Flask, Response, request

## Replace this line with own classes
#from skeleton.core import TestClass

##[=========================== Server Setup ================================]

##

##[=========================== Server Setup END =============================]

#app = Flask(__name__, static_url_path='', static_folder='public')
#app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

#@app.route('/api/test/<data>', methods=['GET'])
#def example_route(data):
    #""" Example API route. """

    #return json.dumps(data)


## Need to change and configure this
#@app.route('/api/test_form', methods=['GET', 'POST'])
#def example_form():
    #""" Example API route for form submission. """

    #if request.method == 'POST':
        #pass

    #return Response(
        #json.dumps("example"),
        #mimetype='application/json',
        #headers={
            #'Cache-Control': 'no-cache',
            #'Access-Control-Allow-Origin': '*'
        #}
    #)

#def main():
    #app.run(port=int(os.environ.get("PORT", 3000)), debug=True)

#if __name__ == '__main__':
    #main()
