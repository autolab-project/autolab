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
    
    for character in '*."/\[]:;|, ' :
        txt = txt.replace(character,'')
        
    return txt   



def two_columns(txt_list) :
    
    ''' Returns a string of the form:
        txt[0]                         txt[1] 
        with a minimal spacing between the first character of txt1 and txt2 '''
    
    spacing = max([len(txt[0]) for txt in txt_list]) + 5
    
    return '\n'.join([ txt[0] + ' '*(spacing-len(txt[0])) + txt[1] 
            for txt in txt_list])

