import io
import pymysql
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

def get_db_connection():
    try:
        conn = pymysql.connect(host='krzDev506.mysql.pythonanywhere-services.com',
                               user='krzDev506',
                               password='ADMsitios@',
                               database='krzDev506$default',
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        return conn
    except pymysql.OperationalError as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


@app.route('/')
def index():
    conn = get_db_connection()
    if conn is None:
        return "Error al conectar a la base de datos", 500

    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, descripcion FROM candidatos')
    candidatos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('inicio.html', candidatos=candidatos)

@app.route('/reportes')
def reportes():
    return render_template('reportes.html')

@app.route('/imagen/<int:idP>')
def mostrar_imagen(idP):
    conn = get_db_connection()
    if conn is None:
        return "Error al conectar a la base de datos", 500

    cursor = conn.cursor()
    try:
        cursor.execute('SELECT imagen FROM candidatos WHERE id = %s', (idP,))
        imagen = cursor.fetchone()
        cursor.close()
        conn.close()

        if imagen and imagen['imagen']:
            print(f"Imagen recuperada para idP={idP}")
            return send_file(io.BytesIO(imagen['imagen']), mimetype='image/jpeg')
        else:
            print(f"Imagen no encontrada para idP={idP}")
            return 'Imagen no encontrada', 404
    except Exception as e:
        print(f"Error al recuperar la imagen: {e}")
        return 'Error al recuperar la imagen', 500

@app.route('/votar', methods=['POST'])
def votar():
    candidato_id = int(request.form['idCandidato'])
    conn = get_db_connection()
    if conn is None:
        return jsonify({'mensaje': 'Error al conectar a la base de datos.'}), 500

    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO votos (idCandidato) VALUES (%s)', (candidato_id,))
        conn.commit()
        return jsonify({'mensaje': 'Gracias por su voto!'})
    except Exception as e:
        print(f"Error al registrar el voto: {e}")
        return jsonify({'mensaje': 'Error al registrar el voto.'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/get_votos')
def get_votos():
    filter_type = request.args.get('filter')
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Error al conectar a la base de datos.'}), 500

    cursor = conn.cursor()
    try:
        if filter_type == 'partido':
            query = '''
                SELECT partidos.nombrePartido AS nombre, COUNT(votos.idVoto) AS cantidad_votos
                FROM votos
                JOIN candidatos ON votos.idCandidato = candidatos.id
                JOIN partidos ON candidatos.idPartido = partidos.idPartido
                GROUP BY partidos.nombrePartido;
            '''
        else:
            query = '''
                SELECT candidatos.nombre AS nombre, COUNT(votos.idVoto) AS cantidad_votos
                FROM votos
                JOIN candidatos ON votos.idCandidato = candidatos.id
                GROUP BY candidatos.nombre;
            '''
        cursor.execute(query)
        votos = cursor.fetchall()
        return jsonify([row for row in votos])
    except Exception as e:
        print(f"Error al obtener los votos: {e}")
        return jsonify({'error': 'Error al obtener los votos.'}), 500
    finally:
        cursor.close()
        conn.close()

