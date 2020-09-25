"""
Example of interactive plot without storing data.

Acquire a trace "a" and a trigger "b" and plot "a" regarding some condition on "b".

Usage:
    import histeresys as h
    h.histeresys()
"""

import sys
import time
from matplotlib.pylab import *
sys.path.append('/home/bruno/Postdoc/job/Stuarts_lab/TDS5104B/')
import TDS5104B as TDS
reload(TDS)

def histeresys(IND=5,chan=['CH2','CH3']):
    I = TDS.TDS5104B(channel=chan)
    
    fig=figure(53,figsize=(14,6))
    show(False)
    try:
        while True:
            I.stop()
            a = convert(I.get_data(RET=True,chan=chan[0]))
            b = convert(I.get_data(RET=True,chan=chan[1]))
            idx = np.argmax(b)
            clf()
            plot(b[0:idx],a[0:idx],'b')
            plot(b[idx:],a[idx:],'g')
            I.run()
            fig.canvas.draw()
            time.sleep(0.2)
    except KeyboardInterrupt:
            print('Stopping scope ...')
            I.close()
            return
    
def convert(s):
    u=np.array([ord(c) for c in s[6:]],dtype='uint8')
    return u.view(dtype='int8')
