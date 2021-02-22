'''
Created on Jan 18, 2020

@author: Greg Petrochenkov
'''


from flask import Flask, render_template, request, jsonify, send_file
# from werkzeug.utils import secure_filename
import os

try:
    from vrflood.get_info import get_images
    from vrflood.q_table import q_table
    from vrflood.staging import stage
    from vrflood.floods import floods
except ImportError:
    from get_info import get_images
    from q_table import q_table
    from staging import stage
    from floods import floods


app = Flask(__name__)
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'csv'])
#
# app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS


if 'VR_FLOOD_UPLOADS_PATH' in os.environ:
    UPLOAD_FOLDER = os.environ['VR_FLOOD_UPLOADS_PATH'] + '/'
else:
    UPLOAD_FOLDER = './uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def render_layout():
    """
    Main layout for application
    """

    return 'Hello from VR Flood!'


@app.route('/get_images', methods=['POST'])
def calculate_geometry():
    """
    Calculates Cross-sectional Geometry and Reads or Computes
    Hydraulic Properties Table
    """
    request.get_data()

    bath_file = str(request.form["bath_file"])
    xrat = float(request.form["xratio"])
    yrat = float(request.form["yratio"])
    angle = float(request.form["angle"])
    distance = int(request.form["dist"])

    if bath_file == 'Morris3.tif':
        epsg = 'EPSG:5070'
        max_stage = 100
        units = 'Meters'

    else:
        epsg = 'EPSG:2260'
        max_stage = 20
        units = 'Feet'

    info = get_images(upload_path=app.config['UPLOAD_FOLDER'],
                      bathfile=bath_file,
                      xrat=xrat,
                      yrat=yrat,
                      angle=angle,
                      distance=distance,
                      crs=epsg,
                      units=units,
                      max_stage=max_stage)

    return jsonify(**info)

@app.route('/flood_height', methods=['POST'])
def get_flood_height():
    """
    Gets a flood height given the synthetic rating curve of a a cross section
    """

    request.get_data()
    print("Form:", request.form, "Data:", request.data)
    # cross section geometry file
    discharge = float(request.form["discharge"])
    mannings = float(request.form["mannings"])

    rating_curve = q_table(app.config['UPLOAD_FOLDER'], 'cross.shp', mannings)
    stage_height = stage(discharge, rating_curve)
    flood_height = floods(app.config['UPLOAD_FOLDER'], stage_height, '/mohawk_bath.tif')

    print(flood_height, type(flood_height))
    return jsonify({'flood_height': flood_height})


@app.route('/image')
def serve_img():
    """
    Serves an image to the client
    """
    
    name = request.args.get('name')
    file_name = ''.join([app.config['UPLOAD_FOLDER'], name, '.png'])
    return send_file(file_name, mimetype='image/png')


app.secret_key = os.urandom(24)

if __name__ == '__main__':
    app.run(debug=True)
