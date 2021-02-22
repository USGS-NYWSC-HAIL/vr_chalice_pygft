import numpy as np
import rasterio


def floods(project_path, stage_height, dem):
    """Returns a float (to be 2d array fo flood depths.

        Parameters
        ----------
        project_path : str
            Directory containing the relevant vector and raster files.
        stage_height : float
            Height of stage in area
        dem : str
            File name of DEM.

    """

    # Load stage and relative height rasters
    dem_path = project_path + dem
    dem_rst = rasterio.open(dem_path)

    stage = stage_height
    print(stage_height)
    dem_data = dem_rst.read(1)

    w_depth = (np.min(np.min(dem_data)) + stage_height) - dem_data
    return np.float64(np.max(np.max(np.max(w_depth)), 0))