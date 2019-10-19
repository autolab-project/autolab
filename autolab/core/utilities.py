# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 23:09:51 2019

@author: qchat
"""

def emphasize(txt):
    
    ''' Returns:    ---
                    txt
                    ---
    '''
    
    return '-'*len(txt) + '\n' + txt + '\n' + '-'*len(txt)



def clean_string(txt):
    
        """ Returns txt without special characters """
        
        for character in '*."/\[]:;|, ' :
            txt = txt.replace(character,'')
            
        return txt   
