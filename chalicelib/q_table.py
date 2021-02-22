import numpy as np
import geopandas as gpd

from chalicelib.__openChannel import flowEst

def q_table(project_path, cross_sections, mannings=.1, max_height=35):
    """Creates a synthetic rating curve for every cross section, "Q_table.csv".

        Parameters
        ----------
        project_path : str
            Directory containing the relevant vector and raster files.
        cross_sections : str
            File name of stream vector with calculated attributes.
        max_height : str
            Maximum height in meters computed in each syntehtic rating curve (default value is 25)

    """

    # Read the cross sections vector
    cross_df = gpd.read_file(project_path + cross_sections).sort_values('id')
    cross_df['elevation'] = cross_df['elevation'].interpolate()
    cross_df = cross_df[cross_df['elevation'] >= 0]
    cross_df = cross_df.dropna()
    reference_vals = [.0012, mannings]


    # Get a two arrays of distance and elevation
    profile_vals = np.vstack([np.arange(1, cross_df.shape[0]+1),
                             cross_df['elevation'].values]).T


    max_elevation = np.max(profile_vals[:, 1])
    min_elevation = np.min(profile_vals[:, 1])
    max_station = 50
    dist_max = np.max(profile_vals[:, 0])
    cell_size = profile_vals[-1, 0] - profile_vals[-2, 0]


    # Append false ending point to the cross section at a height of 50

    start_point = np.array([0, max_elevation + max_station])
    profile_vals = np.vstack([start_point, profile_vals])
    end_point = np.array([dist_max + cell_size, max_elevation + max_station])
    profile_vals = np.vstack([profile_vals, end_point])

    # Create a loop for the max height in meters
    current_height = 1
    # MaxHeightMeter from GUI
    q_list = []

    # Create a depth to stage relationship up to the max stage
    q_val = 0
    max_height_meter = max_height
    while max_height_meter > 0:
        # Create the max elev, loop over the pool.
        ws_elev = min_elevation + current_height
        units = "f"

        try:
            # Pass variables into Open Channel Function
            args = flowEst(ws_elev,
                           reference_vals[1],
                           reference_vals[0],
                           profile_vals,
                           units)

            q_val = args[3] if q_val != args[3] else args[3] + 1

        except:
            q_val + 1


        q_list.append(q_val)

        # Create a paired list of Q and Stage
        current_height = current_height + 1
        max_height_meter = max_height_meter - 1

    q_list = np.array(q_list)
    if not np.all(q_list[2:] == np.zeros(25)):
        non_zero_idx = np.where(q_list[2:] != 0)[0]
        q_list[2:] = np.interp(np.arange(len(q_list[2:])),
                               non_zero_idx,
                               q_list[2:][non_zero_idx])

    return q_list
