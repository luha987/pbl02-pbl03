from peewee import *
from flask import Flask, render_template, request, url_for, redirect
import openpyxl
import csv
import pandas as pd
import os 
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'svg', 'csv', 'xlsx'}

global appType
appType = 'Monolith'

database = SqliteDatabase('carsweb.db')


class BaseModel(Model):
    class Meta:
        database = database


class TBCars(BaseModel):
    carname = TextField()
    carbrand = TextField()
    carmodel = TextField()
    carprice = TextField()


def create_tables():
    with database:
        database.create_tables([TBCars])


@app.route('/')
def indeks():
    return render_template('index.html', appType=appType)


@app.route('/createcar')
def createcar():
    return render_template('createcar.html', appType=appType)


@app.route('/createcarsave', methods=['GET', 'POST'])
def createcarsave():
    fName = request.form['carName']
    fBrand = request.form['carBrand']
    fModel = request.form['carModel']
    fPrice = request.form['carPrice']

    viewData = {
        "name": fName,
        "brand": fBrand,
        "model": fModel,
        "price": fPrice
    }

    # Save to DB
    TBCars.create(
        carname=fName,
        carbrand=fBrand,
        carmodel=fModel,
        carprice=fPrice
    )
    return redirect(url_for('readcar'))


@app.route('/readcar')
def readcar():
    rows = TBCars.select()
    return render_template('readcar.html', rows=rows, appType=appType)


# Route untuk updatecar
@app.route('/updatecar')
def updatecar():
    return render_template('updatecar.html', appType=appType)


# Fungsi untuk mencari data yang ingin di update berdasarkan id
@app.route('/updatecarsearch', methods=['POST'])
def updatecarsearch():
    car_id = request.form['carId']

    # Mencari berdasarkan Id
    car = TBCars.get_or_none(TBCars.id == car_id)
    if not car:
        return render_template('updatecar.html', appType=appType, error="Mobil ber ID tersebut tidak ada")
    
    # Jika id ada maka akan masuk ke form tambahan baru untuk mengedit
    return render_template('updatecarform.html', car=car, appType=appType)


# Menyimpan data car
@app.route('/updatecarsave', methods=['POST'])
def updatecarsave():
    car_id = request.form['id']

    # Validasi jika id mobil ada
    car = TBCars.get_or_none(TBCars.id == car_id)
    if not car:
        return render_template('updatecar.html', appType=appType, error="Mobil ber ID tersebut tidak ada")

    # Mengupdate value car
    fName = request.form['carName']
    fBrand = request.form['carBrand']
    fModel = request.form['carModel']
    fPrice = request.form['carPrice']

    # Update detail car
    TBCars.update(
        carname=fName,
        carbrand=fBrand,
        carmodel=fModel,
        carprice=fPrice
    ).where(TBCars.id == car_id).execute()
    
    return redirect(url_for('readcar'))


@app.route('/deletecar')
def deletecar():
    return render_template('deletecar.html', appType=appType)


@app.route('/deletecarsave', methods=['GET', 'POST'])
def deletecarsave():
    fName = request.form['carName']
    TBCars.delete().where(TBCars.carname == fName).execute()
    return redirect(url_for('readcar'))


@app.route('/searchcar', methods=['GET', 'POST'])
def searchcar():
    results = []  # Inisiasi dari list kosong
    if request.method == 'POST':
        search_query = request.form['searchQuery']  # Mengambil data dari form 
        results = TBCars.select().where(TBCars.carname.contains(search_query))  # Menyamakan data berdasarkan nama
    return render_template('searchcar.html', appType=appType, results=results)  # Menampilkan data yang memiliki nama yang sama dengan pencarian 


# Route untuk upload file
@app.route('/uploadfile', methods=['GET', 'POST'])
def uploadfile():
    # Create the uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Memproses file berdasarkan extensi - nya
            if filename.endswith('.csv'):
                process_csv(file_path)
            elif filename.endswith('.xlsx'):
                process_excel(file_path)
            elif filename.endswith('.svg'):
                process_svg(file_path)

            return redirect(url_for('readcar'))

    return render_template('uploadfile.html', appType=appType)


# Memberikan fungsi hanya file apasaja yang boleh diizinkan
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def process_csv(file_path):
    df = pd.read_csv(file_path)
    for index, row in df.iterrows():
        TBCars.create(
            carname=row.get('name', 'null'),
            carbrand=row.get('brand', 'null'),
            carmodel=row.get('model', 'null'),
            carprice=row.get('price', 'null')
        )


def process_excel(file_path):
    df = pd.read_excel(file_path)
    for index, row in df.iterrows():
        TBCars.create(
            carname=row.get('name', 'null'),
            carbrand=row.get('brand', 'null'),
            carmodel=row.get('model', 'null'),
            carprice=row.get('price', 'null')
        )


def process_svg(file_path):
    with open(file_path, 'r') as svg_file:
        svg_data = svg_file.read()
        TBCars.create(
            carname="SVG Data",
            carbrand="N/A",
            carmodel="N/A",
            carprice="N/A"
        )


@app.route('/help')
def help():
    return "ini halaman Helps"


if __name__ == '__main__':
    create_tables()
    app.run(
        port=5010,
        host='0.0.0.0',
        debug=True
    )
