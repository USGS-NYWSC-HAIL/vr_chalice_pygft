'''
Created on Jan 18, 2020
Modified for Chalice Feb 22, 2021 Martyn SMith

@author: Greg Petrochenkov
'''

from chalice import Chalice
# from werkzeug.utils import secure_filename
import os

from chalicelib.get_info import get_images
from chalicelib.q_table import q_table
from chalicelib.staging import stage
from chalicelib.floods import floods


app = Chalice(__name__)
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'csv'])
#
# app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'chalicelib','uploads')
os.environ['VR_FLOOD_UPLOADS_PATH'] = UPLOAD_FOLDER

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
    current_request.get_data()

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

    info = get_images(upload_path=UPLOAD_FOLDER,
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

    current_request.get_data()
    print("Form:", request.form, "Data:", request.data)
    # cross section geometry file
    discharge = float(request.form["discharge"])
    mannings = float(request.form["mannings"])

    rating_curve = q_table(UPLOAD_FOLDER, 'cross.shp', mannings)
    stage_height = stage(discharge, rating_curve)
    flood_height = floods(UPLOAD_FOLDER, stage_height, '/mohawk_bath.tif')

    print(flood_height, type(flood_height))
    return jsonify({'flood_height': flood_height})


@app.route('/image')
def serve_img():
    """
    Serves an image to the client
    """
    
    name = current_request.args.get('name')
    file_name = ''.join([UPLOAD_FOLDER, name, '.png'])
    return send_file(file_name, mimetype='image/png')


app.secret_key = os.urandom(24)

if __name__ == '__main__':
    app.run(debug=True)
