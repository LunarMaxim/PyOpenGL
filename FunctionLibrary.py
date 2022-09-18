import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *

def getMagnitude(vector:np.ndarray):
    return math.sqrt(vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[2])

def normalize(vector:np.ndarray):
    magnitude = getMagnitude(vector)
    return np.array(vector) / magnitude

# 绘制文字
def drawText(x,y,text):
    blending = False
    if glIsEnabled(GL_BLEND):
        blending = True
    glWindowPos2f(x,y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ctypes.c_int(ord(ch)))
    if not blending:
        glDisable(GL_BLEND)
