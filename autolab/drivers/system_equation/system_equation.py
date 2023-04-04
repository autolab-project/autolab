#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np  # can be used in equation
import pandas as pd


class GeneralEquation():  # very nice to have as many variables as wanted but for the GUI can only handle single variable
    """
    driver = Driver()
    driver.set_variables("x,y")
    driver.set_equation("4*x+y")
    print(driver.equation((2, 5)))

    driver = GeneralEquation()
    driver.set_variables_name("x,y")
    driver.set_variables(2, 5)
    driver.set_equation("4*x+y")
    print(driver.do_equation())

    """
    def __init__(self):
        self._variables_name = ""
        self._variables = "0"
        self._equation_str = "0"
        self.set_equation(self._equation_str)

    def get_variables(self):
        return str(self._variables)[1:-1]

    def set_variables(self, value):
        value = str(value).split(",")
        value = [float(val) for val in value]
        self._variables = list(value)

    def set_variables_str(self, value):
        value = str(value).split(",")
        self._variables = list(value)

    def get_variables_name(self):
        return self._variables_name

    def set_variables_name(self, value):
        self._variables_name = str(value)

    def get_equation(self):
        return self._equation_str

    def set_equation(self, equation):
        self._equation_str = str(equation)
        exec(str(f"def fcn({self._variables_name}):\n return ({equation})"))
        self._equation = locals()['fcn']

    def do_equation(self):
        return self._equation(*self._variables)

    def do_equation_str(self):
        return str(self._equation(*self._variables))

    def get_driver_model(self):

        model = []
        model.append({'element':'variable','name':'variables_name','type':str,'read':self.get_variables_name, 'write':self.set_variables_name,'help':'variables_name names seperated with comma. Ex: x+y'})
        model.append({'element':'variable','name':'variables','type':str,'read':self.get_variables, 'write':self.set_variables,'help':'Variables values seperated with comma. Ex: 4,8'})
        model.append({'element':'variable','name':'variables_str','type':str,'read':self.get_variables, 'write':self.set_variables_str,'help':'Variables string values seperated with comma. Ex: text1,text2'})
        model.append({'element':'variable','name':'equation','type':str,'read':self.get_equation,'write':self.set_equation,'help':'Equation can use device variables and np for numpy'})
        model.append({'element':'variable','name':'result','type':float,'read':self.do_equation,'help':'Returns equation result'})
        model.append({'element':'variable','name':'result_str','type':str,'read':self.do_equation_str,'help':'Returns equation result in string format'})

        return model


class GeneralEquation2():  # very nice to have as many variables as wanted but for the GUI can only handle single variable
    """

    """
    def __init__(self):
        pass

    def res_expression(self):
        value = self._raw_expression
        import autolab
        allowed_dict ={"np":np, "pd":pd}
        allowed_dict.update(autolab.DEVICES)

        value = eval(str(value), {}, allowed_dict)
        self._res_expression = value
        return self._res_expression

    def get_expression(self):
        return self._raw_expression

    def set_expression(self, value):
        self._raw_expression = value

    def get_driver_model(self):

        model = []
        model.append({'element':'variable','name':'set_expression','type':str,'read':self.get_expression, 'write':self.set_expression,'help':'Write full expression. Ex: dummy.phase()+1'})
        model.append({'element':'variable','name':'expression','type':float,'read':self.res_expression,'help':'Returns full expression result'})

        return model



class Driver():

    def __init__(self):
        self._x = 0
        self._y = 0
        self._z = 0
        self._a = 0
        self._b = 0
        self._c = 0
        self._dataframe = pd.DataFrame()
        self._variables = "x,y,z,a,b,c, dataframe"
        self._equation_str = "a*x+b"
        self.set_equation(self._equation_str)


        self.generalEquation = GeneralEquation()
        self.generalEquation2 = GeneralEquation2()
        pass


    def get_x(self):
        return self._x

    def set_x(self, value):
        self._x = value


    def get_y(self):
        return self._y

    def set_y(self, value):
        self._y = value


    def get_z(self):
        return self._z

    def set_z(self, value):
        self._z = value


    def get_a(self):
        return self._a

    def set_a(self, value):
        self._a = value


    def get_b(self):
        return self._b

    def set_b(self, value):
        self._b = value


    def get_c(self):
        return self._c

    def set_c(self, value):
        self._c = value


    def get_dataframe(self):
        return self._dataframe

    def set_dataframe(self, value):
        self._dataframe = pd.DataFrame(value)


    def get_equation(self):
        return self._equation_str

    def set_equation(self, equation):
        self._equation_str = str(equation)
        exec(str(f"def fcn({self._variables}):\n return ({self._equation_str})"))
        self._equation = locals()['fcn']

    def set_equation2(self, equation):
        self._equation_str = str(equation)
        exec(str(f"def fcn({self._variables}):\n return ({self._equation_str})"))
        self._equation = locals()['fcn']

    def equation(self):
        return float(self._equation(self._x, self._y, self._z, self._a, self._b, self._c, self._dataframe))

    def get_driver_model(self):

        model = []
        model.append({'element':'variable','name':'x','type':float,'read':self.get_x, 'write':self.set_x,'help':'Buffer float x'})
        model.append({'element':'variable','name':'y','type':float,'read':self.get_y, 'write':self.set_y,'help':'Buffer float y'})
        model.append({'element':'variable','name':'z','type':float,'read':self.get_z, 'write':self.set_z,'help':'Buffer float z'})
        model.append({'element':'variable','name':'a','type':float,'read':self.get_a, 'write':self.set_a,'help':'Buffer float a'})
        model.append({'element':'variable','name':'b','type':float,'read':self.get_b, 'write':self.set_b,'help':'Buffer float b'})
        model.append({'element':'variable','name':'c','type':float,'read':self.get_c, 'write':self.set_c,'help':'Buffer float c'})
        model.append({'element':'variable','name':'dataframe','type':pd.DataFrame, 'read':self.get_dataframe, 'write':self.set_dataframe,'help':'Buffer dataframe. Be careful with it, equation need to be a float at the end'})
        model.append({'element':'variable','name':'equation','type':str,'read':self.get_equation,'write':self.set_equation,'help':'Equation can use x,y,a,b,c and np for numpy'})
        model.append({'element':'variable','name':'result','type':float,'read':self.equation,'help':'Returns equation result'})
        model.append({'element':'module','name':'general_eq','object':getattr(self,'generalEquation')})
        model.append({'element':'module','name':'general_eq2','object':getattr(self,'generalEquation2')})

        return model


#################################################################################
############################## Connections classes ##############################
class Driver_DEFAULT(Driver):
    def __init__(self):

        Driver.__init__(self)


############################## Connections classes ##############################
#################################################################################
