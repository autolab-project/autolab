# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 23:09:51 2019

@author: qchat
"""

def emphasize(txt,sign='-'):

    ''' Returns:    ---
                    txt
                    ---
    '''

    return sign*len(txt) + '\n' + txt + '\n' + sign*len(txt)


def underline(txt,sign='-'):

    ''' Returns:
                    txt
                    ---
    '''

    return txt + '\n' + sign*len(txt)


def clean_string(txt):

    """ Returns txt without special characters """

    for character in r'*."/\[]:;|, ' :
        txt = txt.replace(character,'')

    return txt



def two_columns(txt_list) :

    ''' Returns a string of the form:
        txt[0]                         txt[1]
        with a minimal spacing between the first character of txt1 and txt2 '''

    spacing = max([len(txt[0]) for txt in txt_list]) + 5

    return '\n'.join([ txt[0] + ' '*(spacing-len(txt[0])) + txt[1]
            for txt in txt_list])


def boolean(value):
    """ Convert value from "True" or "False" or float, int, bool to bool """

    if value == "True":
        value = True
    elif value == "False":
        value = False
    else:
        value = bool(int(float(value)))
    return value


def openFile(filename):
    import platform
    import os
    system = platform.system()
    if system == 'Windows':
        os.startfile(filename)
    elif system == 'Linux':
        os.system(f'gedit "{filename}"')
    elif system == 'Darwin':
        os.system(f'open "{filename}"')


def formatData(data):
    """ Format data to DataFrame """
    import pandas as pd
    try:
        data = pd.DataFrame(data)
    except ValueError:
        data = pd.DataFrame([data])
    data.columns = data.columns.astype(str)
    data_type = data.values.dtype

    try:
        data[data.columns] = data[data.columns].apply(pd.to_numeric, errors="coerce")
    except ValueError:
        pass  # OPTIMIZE: This happens when their is identical column name
    if len(data) != 0:
        assert not data.isnull().values.all(), f"Datatype '{data_type}' not supported"
        if data.iloc[-1].isnull().values.all():  # if last line is full of nan, remove it
            data = data[:-1]
    if data.shape[1] == 1:
        data.rename(columns = {'0':'1'}, inplace=True)
        data.insert(0, "0", range(data.shape[0]))
    return data


def pyqtgraph_fig_ax():
    """ Return a formated fig and ax pyqtgraph for a basic plot """

    import pyqtgraph as pg
    from pyqtgraph import QtGui

    # Configure and initialize the figure in the GUI
    fig = pg.PlotWidget()
    ax = fig.getPlotItem()

    ax.setLabel("bottom", '', **{'color':0.4, 'font-size': '12pt'})
    ax.setLabel("left", '', **{'color':0.4, 'font-size': '12pt'})

    # Set your custom font for both axes
    my_font = QtGui.QFont('Arial', 12)
    my_font_tick = QtGui.QFont('Arial', 10)
    ax.getAxis("bottom").label.setFont(my_font)
    ax.getAxis("left").label.setFont(my_font)
    ax.getAxis("bottom").setTickFont(my_font_tick)
    ax.getAxis("left").setTickFont(my_font_tick)
    ax.showGrid(x=True, y=True)

    vb = ax.getViewBox()
    vb.enableAutoRange(enable=True)
    vb.setBorder(pg.mkPen(color=0.4))

    ## Text label for the data coordinates of the mouse pointer
    dataLabel = pg.LabelItem(color='k', parent=ax.getAxis('bottom'))
    dataLabel.anchor(itemPos=(1,1), parentPos=(1,1), offset=(0,0))

    def mouseMoved(point):
        """ This function marks the position of the cursor in data coordinates"""

        vb = ax.getViewBox()
        mousePoint = vb.mapSceneToView(point)
        l = f'x = {mousePoint.x():g},  y = {mousePoint.y():g}'
        dataLabel.setText(l)

    # data reader signal connection
    ax.scene().sigMouseMoved.connect(mouseMoved)

    return fig, ax


CHECK_ONCE = True

def qt_object_exists(QtObject):
    """ Return True if object exists (not deleted).
    Check if use pyqt5, pyqt6, pyside2 or pyside6 to use correct implementation
    """

    global CHECK_ONCE
    import os
    QT_API = os.environ.get("QT_API")

    try:
        if QT_API in ("pyqt5", "pyqt6"):
            import sip
            return not sip.isdeleted(QtObject)
        elif QT_API == "pyside2":
            import shiboken2
            return shiboken2.isValid(QtObject)
        elif QT_API =="pyside6":
            import shiboken6
            return shiboken6.isValid(QtObject)
        else:
            raise ModuleNotFoundError(f"QT_API '{QT_API}' unknown")

    except ModuleNotFoundError as e:
        if CHECK_ONCE:
            print(f"Warning: {e}. Skip check if Qt Object not deleted.")
            CHECK_ONCE = False
        return True
