from flask import Flask,render_template,redirect,url_for,request
import langcodes
import language_data
from googletrans import Translator
from pymongo import MongoClient

# Replace with your MongoDB connection string
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client['database']

app=Flask(__name__)
app.config["SECRET_KEY"] = "SECRETKEY"

# Temporary data storage
users = []
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Insert user into MongoDB
        db.users.insert_one({'username': username, 'password': password})
        
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user exists in MongoDB
        user = db.users.find_one({'username': username, 'password': password})
        
        if user:
            return redirect('/select')
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/select')
def select():
    return render_template('select.html')
@app.route('/about_detect')
def about_detect():
    return render_template('about_detect.html')
@app.route('/detect', methods=['POST'])
def detector():
    translator = Translator()
    text = request.form['content']
    detected = translator.detect(text)
    lang_code = detected.lang
    lang_name = langcodes.LanguageData(language=lang_code).language_name()
    
    # Insert detection details into MongoDB
    db.detection.insert_one({'content': text, 'detected_language': lang_name})
    
    return render_template('detect.html', detected=lang_name)
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/translate', methods=['POST'])
def translate():
    translator = Translator()
    text = request.form['content']
    source_lang = request.form['languages']
    target_lang = request.form['language']
    translated_text = translator.translate(text, src=source_lang, dest=target_lang).text
    
    # Insert translation details into MongoDB
    db.translation.insert_one({'original_text': text, 'translated_text': translated_text})
    
    return render_template('res.html', text=text, translated_text=translated_text)
if __name__=='__main__':
    app.run(debug=True)