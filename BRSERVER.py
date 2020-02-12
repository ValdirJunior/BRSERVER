from flask import Flask, jsonify, abort, make_response
from flask import request
from flaskext.mysql import MySQL

from flasgger import APISpec, Schema, Swagger, fields

from configparser import ConfigParser

version = 0.1

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'BRSERVER',
    'uiversion': 3,
    'version':version
}
swagger = Swagger(app)
mysql = MySQL()

def read_db_config(filename='config.ini', section='mysql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db

db = read_db_config()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = db['user']
app.config['MYSQL_DATABASE_PASSWORD'] = db['password']
app.config['MYSQL_DATABASE_DB'] = db['database']
app.config['MYSQL_DATABASE_HOST'] = db['host']

mysql.init_app(app)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/api/'+str(version)+'/estados', methods=['GET'])
def get_estados():
    """
    Só para pegar estados.
    Traz todos estados brasileiros
    ---
    tags:
      - estados
    description: Só para pegar estados
    consumes:
      - application/json
    produces:
      - application/json
    responses:
        200:
            description: Deve retornar uma lista de estados
            schema:
                $ref: '#/definitions/Estado'
        404:
            description: Não retornou a lista de estados
            schema:
                $ref: '#/definitions/Estado'
    """
    cur = mysql.connect().cursor()
    cur.execute('''select * from state''')
    ests = cur.fetchall()
    estados = []
    for est in ests:
        estado = {'id': est[0], 'sigla': est[1], 'nome': est[2]}
        estados.append(estado)

    return jsonify({'estados': estados})

@app.route('/api/'+str(version)+'/estados/<int:estado_id>', methods=['GET'])
def get_estado(estado_id):
    """
    Só para pegar o estado você quer.
    Traz o estado perfeito para você
    ---
    tags:
      - estados
    parameters:
      - name: estado_id
        in: path
        type: string
        enum: [1, 2, 3]
        required: true
        default: all
        description: Que estado você quer?
    description: Só para pegar o estado que você quer
    consumes:
      - application/json
    produces:
      - application/json
    responses:
        200:
            description: OK
            schema:
                $ref: '#/definitions/Estado'
        404:
            description: Not found
    """
    cur = mysql.connect().cursor()
    cur.execute("select * from state where id = %s", (estado_id))
    ests = cur.fetchall()
    estados = []

    for est in ests:
        estado = {'id': est[0], 'sigla': est[1], 'nome': est[2]}
        estados.append(estado)

    if len(estados) == 0:
        abort(404)
    return jsonify({'estado': estados[0]})

@app.route('/api/'+str(version)+'/cidades/<int:cidade_id>', methods=['GET'])
def get_cidade(cidade_id):
    """
    Só para pegar o estado você quer.
    Traz o estado perfeito para você
    ---
    tags:
      - cidades
    parameters:
      - name: estado_id
        in: path
        type: string
        enum: [1, 2, 3]
        required: true
        default: all
        description: Que estado você quer?
    description: Só para pegar o estado que você quer
    consumes:
      - application/json
    produces:
      - application/json
    responses:
        200:
            description: OK
            schema:
                $ref: '#/definitions/Cidade'
        404:
            description: Not found
    """
    cur = mysql.connect().cursor()
    cur.execute("select * from city where id = %s", (cidade_id))
    cids = cur.fetchall()
    cidades = []

    for cid in cids:
        cidade = {'id': cid[0], 'id_estado': cid[1], 'nome': cid[2]}
        cidades.append(cidade)

    if len(cidades) == 0:
        abort(404)
    return jsonify({'cidade': cidades[0]})

@app.route('/api/'+str(version)+'/info/<string:estado_uf>/<string:cidade>', methods=['GET'])
def get_info(estado_uf, cidade):
    """
    Só para pegar o estado você quer.
    Traz o estado perfeito para você
    ---
    tags:
      - cidades
    parameters:
      - name: estado_uf
        in: path
        type: string
        enum: [1, 2, 3]
        required: true
        default: all
        description: Que estado você quer?
      - name: cidade
        in: path
        type: string
        enum: [1, 2, 3]
        required: true
        default: all
        description: Que cidade você quer?
    description: Só para pegar o estado que você quer
    consumes:
      - application/json
    produces:
      - application/json
    responses:
        200:
            description: OK
            schema:
                $ref: '#/definitions/Estado'
        404:
            description: Not found
    """
    cur = mysql.connect().cursor()
    cur.execute("select * from city where name = %s and idState in (select id from state where initialsState = %s);", (cidade,estado_uf))
    ins = cur.fetchall()
    infos = []

    for i in ins:
        info = {'id': i[0], 'id_estado': i[1], 'cidade': i[2]}
        infos.append(info)

    if len(infos) == 0:
        abort(404)
    return jsonify({'info': infos[0]})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error':'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error':'Bad request'}), 400)

if __name__ == '__main__':
    app.run(debug=True)
