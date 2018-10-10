from flask import Flask
from flask import request,render_template, flash, redirect, url_for
from yfin_mkt import *

app = Flask(__name__)

if __name__ == '__main__':
	app.run(host='0.0.0.0')