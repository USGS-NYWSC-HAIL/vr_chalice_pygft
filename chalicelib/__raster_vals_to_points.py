import rasterio
import numpy as np


def get_rast_values(upload_path, raster_path, lon_vals, lat_vals):
    """Gets raster values for each point provided.

        Parameters
        ----------
        upload_path : str
            Directory containing the upload path.
        raster_path : str
            Directory containing the relevant vector and raster files.
        lon_vals : array_like
            Longitude points of vector.
        lat_vals : array_like
            Latitude points of vector.

        Returns
        -------
        array_like
            Float array of raster values at each given point.


    """

    # Open raster and get its latitude and longitude bounds
    rast = rasterio.open(upload_path + raster_path)
    lon_min, lat_min, lon_max, lat_max = rast.bounds

    # Get the raster transform and units
    rst_transform = rast.transform
    lon_units = np.abs(rst_transform[0])
    lat_units = np.abs(rst_transform[4])

    # Adjust by the minimum values if x_min is less than zero
    if lon_min < 0:
        lon_max = lon_max + np.abs(lon_min)
        lon_vals = lon_vals + np.abs(lon_min)
        lon_min = lon_min + np.abs(lon_min)

    # Round all values and convert to integer array
    lon_vals = np.round(lon_vals).astype(np.int)

    # Create sparse array of x values
    sparse_lons = np.empty(int(lon_max))
    index = 0
    for idx in range(int(lon_min), int(lon_max)):
        sparse_lons[idx] = index
        index += 1

    # Adjust by the minimum values if y_min is less than zero
    if lat_min < 0:
        lat_max = lat_max + np.abs(lat_min)
        lat_vals = lat_vals + np.abs(lat_min)
        lat_min = lat_min + np.abs(lat_min)

    # Round all values and convert to integer array
    lat_vals = np.round(lat_vals).astype(np.int)

    # Create sparse array of y values
    sparse_lats = np.empty(int(lat_max))
    index = lat_max - lat_min
    for idx in range(int(lat_min), int(lat_max)):
        sparse_lats[idx] = index
        index -= 1

    #Get raster values from dataset
    val_array = rast.read(1)

    #Get the values for each point in zip(x_vals, y_vals)
    return get_value(lon_vals,
                     lat_vals,
                     sparse_lons,
                     lon_units,
                     sparse_lats,
                     lat_units,
                     val_array)


def get_value(lon_vals, lat_vals, sparse_lons, lon_units,
              sparse_lats, lat_units, val_array):
    """Gets raster values from index.

            Parameters
            ----------
            lon_vals : array_like
                Longitude points of vector.
            lat_vals : array_like
                Latitude points of vector.
            sparse_lons : array_like
                Sparse array of x longitude values in raster
            lon_units : int
                Units of x dimension
            sparse_lats : array_like
                Sparse array of y latitude values in raster
            lat_units : int
                Units of y dimension
            val_array : array_like
                Values of raster array


            Returns
            -------
            array_like
                Float array of raster values at each given point.


        """

    values = np.empty(len(lon_vals))

    for idx, _ in enumerate(lon_vals):

        try:
            x_idx = int(np.round(sparse_lons[lon_vals[idx]] / lon_units))
            y_idx = int(np.round(sparse_lats[lat_vals[idx]] / lat_units))

            values[idx] = float("%.2f" % round(val_array[y_idx, x_idx], 2))
        except IndexError:
            values[idx] = np.nan

    return values

