from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify, Response
import psycopg2
import csv
import json
from fpdf import FPDF
import pandas as pd
import io
from werkzeug.security import generate_password_hash, check_password_hash
import xml.etree.ElementTree as ET
from openpyxl import Workbook
from db import get_db_connection

app = Flask(__name__)
app.secret_key = '1234567890'  # Necesario para manejar sesiones

# Ruta para login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and user[2] == password:  
            session['user'] = user[1]
            return redirect(url_for('listar_tareas'))
        else:
            flash('Usuario o contraseña incorrectos')

    return render_template('login.html', body_class="login-page")

# Ruta para dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

# Cerrar sesión
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('login'))

# Ruta para listar tareas
@app.route('/tareas')
def listar_tareas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tareas')
    tareas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('tareas.html', tareas=tareas, body_class="tareas-page")

# Ruta para agregar tarea
@app.route('/tareas/agregar', methods=['GET', 'POST'])
def agregar_tarea():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha_hora = request.form['fecha_hora']
        estado = request.form['estado']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tareas (titulo, descripcion, fecha_hora, estado) VALUES (%s, %s, %s, %s)",
            (titulo, descripcion, fecha_hora, estado)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('listar_tareas'))

    return render_template('agregar_tarea.html', body_class="agregar-tarea-page")

# Ruta para editar tarea
@app.route('/tareas/editar/<int:id>', methods=['GET', 'POST'])
def editar_tarea(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha_hora = request.form['fecha_hora']
        estado = request.form['estado']
        cur.execute(
            "UPDATE tareas SET titulo = %s, descripcion = %s, fecha_hora = %s, estado = %s WHERE id = %s",
            (titulo, descripcion, fecha_hora, estado, id)
        )
        conn.commit()
        return redirect(url_for('listar_tareas')) 
    
    cur.execute('SELECT * FROM tareas WHERE id = %s', (id,))
    tarea = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('editar_tarea.html', tarea=tarea, body_class="editar-tareas-page")

# Ruta para eliminar tarea
@app.route('/tareas/eliminar/<int:id>')
def eliminar_tarea(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM tareas WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('listar_tareas'))

# Rutas de Exportación
@app.route('/exportar/<formato>')
def exportar_datos(formato):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tareas")
    tareas = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]

    if formato == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for tarea in tareas:
            pdf.cell(200, 10, txt=f"{tarea}", ln=True)
        pdf_file = 'tareas.pdf'
        pdf.output(pdf_file)
        return send_file(pdf_file, as_attachment=True)

    elif formato == 'xlsx':
        df = pd.DataFrame(tareas, columns=column_names)
        excel_file = 'tareas.xlsx'
        df.to_excel(excel_file, index=False)
        return send_file(excel_file, as_attachment=True)

    elif formato == 'csv':
        df = pd.DataFrame(tareas, columns=column_names)
        csv_file = 'tareas.csv'
        df.to_csv(csv_file, index=False)
        return send_file(csv_file, as_attachment=True)

    elif formato == 'xml':
        root = ET.Element("Tareas")
        for tarea in tareas:
            tarea_element = ET.SubElement(root, "Tarea")
            for i, col in enumerate(column_names):
                ET.SubElement(tarea_element, col).text = str(tarea[i])
        tree = ET.ElementTree(root)
        xml_file = 'tareas.xml'
        tree.write(xml_file)
        return send_file(xml_file, as_attachment=True)

    elif formato == 'json':
        data = []
        for tarea in tareas:
            tarea_dict = {
                "ID": tarea[0],
                "Título": tarea[1],
                "Descripción": tarea[2],
                "Fecha y Hora": tarea[3].strftime('%Y-%m-%d %H:%M:%S'),
                "Estado": tarea[4]
            }
            data.append(tarea_dict)

        json_output = json.dumps(data, indent=4)
        return send_file(io.BytesIO(json_output.encode()), as_attachment=True, download_name='tareas.json', mimetype='application/json')

    return redirect(url_for('listar_tareas'))

# Ruta para buscar tareas
@app.route('/buscar_tareas')
def buscar_tareas():
    term = request.args.get('term')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tareas WHERE titulo ILIKE %s OR descripcion ILIKE %s", (f'%{term}%', f'%{term}%'))
    tareas = cursor.fetchall()

    result = []
    for tarea in tareas:
        result.append({
            'id': tarea[0],
            'titulo': tarea[1],
            'descripcion': tarea[2],
            'fecha_hora': tarea[3].isoformat(),
            'estado': tarea[4]
        })

    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
