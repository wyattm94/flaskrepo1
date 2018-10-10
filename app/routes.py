from app import app

@app.route('/')
@app.route('/home')
def home():
	return "The app is working"