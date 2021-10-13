from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

# cau hinh mySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'shop_wise'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Form dang nhap
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor() 

        result = cur.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['email'] = email

                flash('You are new logged in', 'success')   
                return redirect(url_for('home'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

#Register Form class
class RegisterForm(Form):
    firstname = StringField('Firstname', [validators.Length(min=1, max=25)])
    lastname = StringField('Lastname', [validators.Length(min=1, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Password do not match")
    ])
    confirm = PasswordField('Confirm Password')

#Form dang ky
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users( email, firstname, lastname, password) VALUES (%s, %s, %s, %s)", (email, firstname, lastname, password))

        mysql.connection.commit()

        cur.close()

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# thoat
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#Giao dien chinh
@app.route('/index')
def home():

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM product")

    product = cur.fetchall()

    if result > 0:
        return render_template('index.html', product=product)
    else:
        msg = "No products Found"
        return render_template('index.html', msg=msg)

    cur.close() 

#Product form class
class ProductForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=200)])
    description = TextAreaField('Description ', [validators.Length(min=1)])

# them san pham 
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = ProductForm(request.form) 
    if request.method == 'POST' and form.validate():
        name = form.name.data
        description = form.description.data

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO product(name, description) VALUES (%s, %s)", (name, description))

        mysql.connection.commit()
        
        cur.close()

        flash('Product Created', 'success')

        return redirect(url_for('home'))
    
    return render_template('add_product.html', form=form)


# Sua san pham
@app.route('/edit_product/<string:id>', methods=['GET', 'POST'])
def edit_product(id):

    cur = mysql.connection.cursor()

    #Lay san pham theo id
    result = cur.execute("SELECT * FROM product WHERE id=%s", [id])

    product = cur.fetchone()

    form = ProductForm(request.form)
    
    form.name.data = product['name']
    form.description.data = product['description']

    if request.method == 'POST' and form.validate():
        name = request.form['name']
        description = request.form['description']

        cur = mysql.connection.cursor()

        cur.execute("UPDATE product SET name=%s, description=%s WHERE id = %s", (name, description, id))

        mysql.connection.commit()
        
        cur.close()

        return redirect(url_for('home'))
    
    return render_template('edit_product.html', form=form)

# Xoa san pam
@app.route('/delete_product/<string:id>', methods=['POST'])
def delete_product(id):
    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM product WHERE id = %s", [id])

    mysql.connection.commit()
    
    cur.close()

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.secret_key = 'sercet123'
    app.run(debug=True)
