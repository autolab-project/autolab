# -*- coding: utf-8 -*-

def print_tab(tab_content) :
    
    MIN_SPACE_LEFT = 1
    MIN_SPACE_RIGHT = 4
    SEP_SIGN = '='
    
    # Nb col
    for content in tab_content : 
        if content is not None :
            nb_col = len(content)
            break
        
    # Col width
    col_width = []
    for i in range(nb_col) :
        col_width.append(MIN_SPACE_LEFT+MIN_SPACE_RIGHT+max([len(c[i]) for c in tab_content if c is not None]))
        
    # Str to print
    str_to_print = ''
    for i in range(len(tab_content)):
        if tab_content[i] is None : 
            str_to_print += ' '+SEP_SIGN*(sum(col_width)+nb_col-1)
        else :
            str_to_print += '|'
            for col in range(nb_col) :
                str_to_print += ' '*MIN_SPACE_LEFT + tab_content[i][col] + ' '*(col_width[col]-len(tab_content[i][col])-MIN_SPACE_LEFT) + '|'
        if i != len(tab_content)-1 :
            str_to_print += '\n'
    
    print(str_to_print)
    
    
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
