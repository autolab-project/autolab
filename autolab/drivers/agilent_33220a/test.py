class Device() :
    def __init__(self, ... ):

    def setWavelength():


class Device_TCPIP() :
    def __init__(self, **kwargs):
        Device.__init__(self, **kwargs)
        self.controller = ...

    def query(self,command):
        return self.controller.query(command)

    def read(self):
        return self.controller.read()

    def write(self,command):
        self.controller.write(commande,length=self.length)


class Device_VX11() :
    def __init__(self, **kwargs):
        Device.__init__(self, **kwargs)
        self.controller = ...

    def query(self,command):
        return self.controller.query(command)

    def read(self):
        return self.controller.read()

    def write(self,command):
        self.controller.write(commande,length=self.length)



 
if __name__=="__main__":
    #conn='TCPIP'

    assert 'Device_'+conn in __main__.__attr__ , "Not in " + str([a for a in __main__.__attr__ if a.startwith('Device_'))

    myClass = getattr(__main__,'Device_'+conn)

    instance = myClass()
    
    
    from usit.core import _config as usitconfig
    
    usitconfig.checkConfig()
    usitconfig.DEVICES_INDEX_PATH






import agilent_33220a as a
import inspect

Driver_CONN = 'Driver_VISA'

# First check for Driver_CONN functions 
NAME ='getDriverConfig'
#NAME = 'internal_function'
#NAME ='amplitude'
#print(sys.modules[__name__],classes)  # import agilent33220a as a; inspect.getmembers(a,inspect.isclass)
classes = [(name,obj) for name,obj in inspect.getmembers(a, inspect.isclass) if name == Driver_CONN] #Driver_CONN
functions = [(name,obj,classes[k][0]) for k in range(len(classes)) for name,obj in inspect.getmembers(classes[k][1],inspect.isfunction) if name!= '__init__']
func = [function for function in functions if NAME==function[0]]
if func:
    print(f'found in {"".join([func[f][2] for f in range(len(func))])}')
# Then all the Other classes but Driver*
Driver_classes = [name for name,obj in inspect.getmembers(a, inspect.isclass) if 'Driver' in name]
classes2 = [(name,obj) for name,obj in inspect.getmembers(a, inspect.isclass) if name not in Driver_classes] #Driver_CONN
functions2 = [(name,obj,classes2[k][0]) for k in range(len(classes2)) for name,obj in inspect.getmembers(classes2[k][1],inspect.isfunction) if name!= '__init__']
func2 = [function for function in functions2 if NAME==functions2[0]]
if func2:
    print(f'found in {"".join([func2[f][2] for f in range(len(func2))])}')


# Start instantiating
Driver_CONN_class = getattr(a,Driver_CONN)
I = Driver_CONN_class()

#vars(I)    =>   channel
#inspect.getmembers getattr(I,'channel'),inspect.ismethod
#inspect.getmembers vars(I)['channel'],inspect.ismethod
#inspect.getmembers vars(I)['test'],inspect.ismethod    =>   []
l = []
class_meth = [f'I.{name}' for name,obj in inspect.getmembers(I,inspect.ismethod) if name != '__init__']
#print([getattr(I,class_meth[k][0]) for k in range(len(class_meth)) if class_meth[k][0] != '__init__'])

class_vars = [f'I.{key}.{name}' for key in vars(I).keys() for name,obj in inspect.getmembers(vars(I)[key],inspect.ismethod) if inspect.getmembers(vars(I)[key],inspect.ismethod) != '__init__' and inspect.getmembers(vars(I)[key],inspect.ismethod) and name!='__init__']

l.extend(class_meth);l.extend(class_vars)

print(l)
for i in range(len(l)):
    print(getattr(I,l[i].split('.')[1]))
    if len(l[i].split('.'))==2: getattr(I,l[i].split('.')[1])
    else: getattr(getattr(I,l[i].split('.')[1]),l[i].split('.')[-1])
    
import os
print(os.path.join(os.path.dirname(__file__),'core'))
    

