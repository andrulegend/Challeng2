
#The first 3 lines of my code, are all the tools I'm using, the most important are Flask, 
#Werkzeug we use to generate hash and check the hash and SQL alchemy we use to work with SQL in the Code
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#This Secret Key is super weak, the secret key is used to firm cookies, this way the website know is the cookie is real or made 
#for another Person, I decide To keep it like this because is not a real app, but in generally I should change it.
app.secret_key = "1234"

# SQLalchemy work with flask
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Here we create a class called User and is gonna save the data username and password in the data base called User inside user.db
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password) 

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#This is our main route, is gonna send us to index.html if you are not log in.
@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


#login so this the logic of the login is a method POST so we request information from the username like username and password

@app.route("/login", methods = ["POST"])
def login():
    # Logic, basic request form from the HTML username and password check if exist in the database, if exist send you to the Dashboard if not stay in Index and tell you the error
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username = username).first()
    if user and user.check_password(password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        if not user:
            return render_template("index.html", error="User Not Found")
        return render_template("index.html", error="Wrong Password")

    #Register
    
@app.route("/register", methods=["POST"])
def register():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username = username).first()
    if user:
        return render_template("index.html", error = "user already here")
    else:
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect(url_for("dashboard"))
    
@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username = session['username'])
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    session.pop('username',None)
    return redirect(url_for('home'))

# This route let me check all users the users I have in my database and the password hash, is super insecure I just have it to make test and check thing but it should be like this.
@app.route("/test-users")
def test_users():
    users = User.query.all()

    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "password_hash": user.password_hash
            }
            for user in users
        ]
    }
        
if __name__ in "__main__":
    
    with app.app_context():
        db.create_all()
    app.run(debug = True, host = "0.0.0.0", port = 5555)