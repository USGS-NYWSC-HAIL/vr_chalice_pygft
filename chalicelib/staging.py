import numpy as np


def stage(discharge, rating_curve):
    """Creates a stage assigned watershed grid, "watershed_stage.tif" or stage assigned point vector if interp is True "stage_points.shp"

        Parameters
        ----------
        discharge : flt
            Value of discharge.
        rating_curve : list
            list of synthetic rating curve

    """

    q_val = discharge

    # Query synthetic rating curve table for COMID
    # temp_q_df = q_df[q_df[0] == comid]
    # cross_ids = temp_q_df[1].unique()
    # cross_ids = [0]

    # for cross_id in cross_ids:

    q_vals = rating_curve

    # Get synthetic rating curve Qs and see how many are below the stream Q
    my_array = np.squeeze(q_vals)
    test_min = my_array[np.where(my_array < q_val)]

    # if not TestMin:
    if test_min.size == 0:

        min_q = 0
        min_stage = 0

        # Index is at 1
        max_q = np.amin(my_array)

    else:
        min_q = np.amax(my_array[my_array < q_val])
        min_stage = np.where(my_array == min_q)

        # get int from array and index 1
        min_stage = min_stage[0] + 1

        try:
            max_q = np.amin(my_array[my_array > q_val])
        except ValueError:
            return len(rating_curve)

    max_stage = np.where(my_array == max_q)

    # get int from array and index 1
    max_stage = max_stage[0] + 1

    # Start Interpolation
    # Goal create a stage value based on the min and max lookup.
    ht_1 = min_stage
    ht_3 = max_stage

    f_11 = min_q
    f_12 = q_val
    f_13 = max_q

    fl_int_1 = f_12 - f_11
    fl_int_2 = f_13 - f_12
    fl_int_3 = fl_int_1 + fl_int_2
    fl_int_4 = fl_int_1 * ht_3
    fl_int_5 = ht_1 * fl_int_2
    fl_int_6 = fl_int_4 + fl_int_5

    final_ht = fl_int_6 / fl_int_3

    return final_ht
