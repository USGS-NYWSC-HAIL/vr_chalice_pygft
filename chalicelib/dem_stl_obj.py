# #Dem to 3d params
# return {"layer": path_layer[0],
#         "roi_x_max": self.roi_x_max, "roi_x_min": self.roi_x_min, "roi_y_max": self.roi_y_max,
#         "roi_y_min": self.roi_y_min, "roi_rect_Param": self.rect_Params,
#         "spacing_mm": spacing_mm, "height": self.height, "width": self.width,
#         "z_scale": self.z_scale, "scale": self.scale, "scale_h": self.scale_h, "scale_w": self.scale_w,
#         "z_inv": z_inv, "z_base": z_base,
#         "projected": projected, "crs_layer": self.layer.crs(), "crs_map": self.map_crs, "divideRow": rows,
#         "divideCols": cols}
#
# layer = dir path
# self.roi_x_max = pointMax.x()
# self.roi_y_min = pointMin.y()
# self.roi_x_min = pointMin.x()
# self.roi_y_max = pointMax.y()
#
# self.rect_Params = {'center': [rec.center().x(), rec.center().y()], 'width': rec.width(), 'height': rec.height(),
#                     'rotation': 0}
#
# self.spacing_mm =  .3  e.g
# "height": self.height,
# "width": self.width,
#
# "z_scale": self.z_scale,
# "scale": self.scale,
# "scale_h": self.scale_h,
# "scale_w": self.scale_w,
#
# "z_inv": False or 0
# "z_base": 'lowest point in dem'
# "projected": False or 0
# "crs_layer": self.layer.crs(), 'Proj4'
# "crs_map": self.map_crs, 'Proj4'  #Hopefully the same works
# "divideRow": 1,
# "divideCols": 1}