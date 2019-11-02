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
