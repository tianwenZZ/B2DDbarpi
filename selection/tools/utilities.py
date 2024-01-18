def get_val(tree,item):
    '''
    return the value of expression for given treen and entry
    '''
    pieces = item.split()
    if len(pieces)==1:
        return getattr(tree,pieces[0])
    else:
        pieces = pieces[2:]
        for ii,p in enumerate(pieces):
            # reply on upper case to find the variable
            if any(c.isupper() for c in p):
                    p = getattr(tree,p)
            pieces[ii] = str(p)
        expr = ' '.join(pieces)
        code_obj = compile(expr,'','eval')
        return eval(code_obj)
