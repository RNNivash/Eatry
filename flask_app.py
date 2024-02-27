from flask import Flask,redirect,render_template,request,url_for,session
import pickle

import smtplib
from email.mime.text import MIMEText
from flask import session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "sujith"


def send_email(name,reciveremail):
    smtp_ssl_host = 'smtp.gmail.com'  # smtp.mail.yahoo.com
    smtp_ssl_port = 465
    username = 'server.mailbridge@gmail.com'
    password = 'fwsujrovkmlxmfqm'
    sender = 'server.mailbridge@gmail.com'
    targets = reciveremail
    targets=targets.casefold()
    msg = MIMEText('Hello  {} !,Thankyou for booking, your food will be ready by your time'.format(name))
    msg['Subject'] = 'Table Booking -Reg'
    msg['From'] = sender
    msg['To'] = targets

    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    server.login(username, password)
    server.sendmail(sender, targets, msg.as_string())
    server.quit()


@app.route('/')
def index():
    return render_template('index.html',sty='style=display:none;')

@app.route('/Menu')
def Menu():
    return render_template('dishes.html')


@app.route('/food/<name>',methods=['GET','POST'])
def Book(name):
    if request.method == 'POST':
        order = []
        session['name'] = request.form['name']
        session['phone'] = request.form['phone']
        session['email'] = request.form['email']
        session['dish'] = request.form['dish']
        session['seat'] = request.form['seat']
        session['datetime'] = request.form['datetime']
        session['message'] = request.form['message']
        dt=session['datetime'].split('T')
        date,time = dt[0],dt[1]

        with open('Tables','rb') as fp:
            Tables=pickle.load(fp)
        Tables[session['seat']] = True
        with open('Tables','wb') as fp:
            pickle.dump(Tables,fp)
        order.append(session['name'])
        order.append(session['phone'])
        order.append(session['email'])
        order.append(session['dish'])
        order.append(session['seat'])
        order.append(date)
        order.append(time)
        order.append(session['message'])
        with open('Orders','rb') as fp:
            Orders=pickle.load(fp)
        Orders.append(order)
        with open('Orders','wb') as fp1:
            pickle.dump(Orders,fp1)
        send_email(session['name'],session['email'])
        return render_template('index.html',mss='booking compleate')

    else:
        with open('Tables','rb') as fp:
            Tables=pickle.load(fp)
        lst=[]
        for table in Tables:
            if Tables[table] == False:
                lst.append(table)
        return render_template('seats.html',ls=lst,dish=name)

@app.route('/admin',methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        session['pass'] = request.form['pass']
        if session['pass'] == "12345678":
            with open('Orders','rb') as fp:
                Orders=pickle.load(fp)
            return render_template("pannel.html",order=Orders)
        else:
            return render_template("admin.html")
    else:
        return render_template("admin.html")

@app.route('/compleate/<table>')
def compleate(table):
    with open('Orders','rb') as fp:
        Orders=pickle.load(fp)
    ls=[]
    for o in Orders:
        if o[4] !=  table:
            ls.append(o)
    with open('Orders','wb') as fp1:
        pickle.dump(ls,fp1)
    with open('Tables','rb') as fp:
        Tables=pickle.load(fp)
    Tables[table] = False
    with open('Tables','wb') as fp:
        pickle.dump(Tables,fp)
    return redirect(url_for('admin'))




if __name__ == '__main__':
    app.run()