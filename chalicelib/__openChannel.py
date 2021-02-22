# -*- coding: utf-8 -*-
"""
Created on Tue May  5 16:26:25 2015

@author: mweier
"""

import numpy as np
from numba import jit

@jit
def channelBuilder(wsDepth, rightSS, leftSS, widthBottom):
    """
    Builds trapziodal channel station/elevation array given depth, 
    right side slope, left side slope, and bottom width
    """
    leftToe = wsDepth*1.25*leftSS
    rightToe = wsDepth*1.25*rightSS  
    staElev = np.array([(0.0, wsDepth*1.25), (leftToe, 0.0), (leftToe+widthBottom, 0.0), (leftToe+widthBottom+rightToe, wsDepth*1.25)])
    return staElev


def lineIntersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])
    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        x = y = np.nan
#        print 'lines do not intersect'
        return x, y

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

@jit
def polygonArea(corners):
    area = 0.0
    for i in range(len(corners)):
        j = (i + 1) % len(corners)
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    area = abs(area) / 2.0
    return area  

@jit
def channelPerimeter(corners):
    P = 0.0
    for i in range(len(corners)-1):
        P += np.sqrt((np.power((corners[i+1][0]-corners[i][0]),2) + np.power((corners[i+1][1]-corners[i][1]),2)))
    return P
    

def flowEst(wsElev, n, slope, staElev, units):
    """
    Estimates uniform flow using the Manning equation for
    a user defined trapziodal channel or a manually defined channel using
    a station/elevation file 
    """

    if units == "m":
        const = 1.0
    else:
        const = 1.49
    
    intersectList = []
    for i in range(0, len(staElev)):
        x, y = lineIntersection((staElev[i-1], staElev[i]), ([staElev[0][0],wsElev], [staElev[-1][0],wsElev]))  
        if x >= staElev[i-1][0] and x <= staElev[i][0] and abs(y - wsElev)<0.01:
            #print x,y
            intersectList.append((x,y))
        else:
            #print 'line segments do not intersect'
            pass



    intersectArray = np.array(intersectList)
    intersectArray = intersectArray[intersectArray[:, 0].argsort()]
    # print 'more than two points intersect'
    staMinElev = staElev[np.where(staElev[:,1]==min(staElev[:,1]))][0][0]
    startPoint = intersectArray[np.where(intersectArray[:,0]<staMinElev)][-1]
    endPoint = intersectArray[np.where(intersectArray[:,0]>staMinElev)][0]
    intersectArray = np.vstack([startPoint, endPoint])

        
    staMin = np.min(intersectArray[:,0])
    staMax = np.max(intersectArray[:,0])
    
    thalweig = staElev[np.where(staElev[:,1] == np.min(staElev[:,1]))] 

    minElev = thalweig[:,1][0]
    maxDepth = wsElev-minElev

    staElevTrim = np.vstack([intersectArray[0], staElev, intersectArray[1]])
    #staElevTrim = staElevTrim[staElevTrim[:,0].argsort()]
    staElevTrim = staElevTrim[np.where((staElevTrim[:,0]>=staMin) & (staElevTrim[:,0]<=staMax))]
  
    area = polygonArea(staElevTrim)
    R = area/channelPerimeter(staElevTrim)
    v = (const/n)*np.power(R,(2./3.0))*np.sqrt(slope)
    Q = v*area
    topWidth = staMax-staMin 
    xGround = staElev[:,0]
    yGround = staElev[:,1]
    yGround0 = np.ones(len(xGround))*np.min(yGround)     
    xWater = staElevTrim[:,0]
    yWater = np.ones(len(xWater))*wsElev
    yWater0 = staElevTrim[:,1]  
    args = R, area, topWidth, Q, v, maxDepth, xGround, yGround, yGround0, xWater, yWater, yWater0
    return args
