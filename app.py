from flask import Flask
from flask import request,render_template, flash, redirect, url_for
from yfin_mkt import *

app = Flask(__name__)

@app.route('/')
def home():
	sp = yget_stock('^GSPC',start='2018-1-1')
	dj  = yget_stock('^DJI',start='2018-1-1')
	nd = yget_stock('^IXIC',start='2018-1-1')
	
	sp_p = yf_plot(sp)
	img1 = io.BytesIO(); plt.savefig(img1,format='png'); img1.seek(0)
	res_sp = base64.b64encode(img1.getvalue()).decode()
	
	dj_p  = yf_plot(dj)
	img2 = io.BytesIO(); plt.savefig(img2,format='png'); img2.seek(0)
	res_dj = base64.b64encode(img2.getvalue()).decode()
	
	nd_p = yf_plot(nd)
	img3 = io.BytesIO(); plt.savefig(img3,format='png'); img3.seek(0)
	res_nd = base64.b64encode(img3.getvalue()).decode()
	
	return render_template('home.html',fsp=res_sp,fdj=res_dj,fnd=res_nd)
	#return render_template("home.html") #, title='Home Page') #posts=posts

@app.route('/page2')
def page2():
	return render_template("page2.html")

@app.route('/page3')
def page3():
	return render_template("page3.html")

if __name__ == '__main__':
	app.run(host='0.0.0.0')