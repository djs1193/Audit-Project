ones_list = ['TRUE','True','true','T','ACTIVATED','activated']
zeros_list = ['False','FALSE','false','F','DEACTIVATED','deactivated','DISABLED','disabled','AUTOMATIC','NOT_APPLICABLE','OFF','NONE']
def compare_values(comp1,comp2):

    if comp2 == "Nan":               ### IF GOLD STANDARD WAS NAN MEANS NOTHING TO COMPARE
        val = "Nan"
        return(val)

    if comp1 in ones_list:
        comp1 = '1'
    elif comp1 in zeros_list:
        comp1 = '0'
    if comp2 in ones_list:
        comp2 = '1'
    elif comp2 in zeros_list:
        comp2 = '0'


    if "(" in comp2:
        for i in comp2:
            if i == "(":
                open_index = comp2.index(i)
            if i == ")":
                close_index = comp2.index(i)
        comp2 = comp2[open_index+1:close_index]

    if ':' in comp2:
        val_list = comp2.split(':')
        for i in range(len(val_list)):
            if val_list[i] in ones_list:
                val_list[i] = '1'
            elif val_list[i] in zeros_list:
                val_list[i] = '0'
        if comp1 in val_list:
            val = "T"
            return(val)

    if ',' in comp2:
        val_list = comp2.split(',')
        for i in range(len(val_list)):
            if val_list[i] in ones_list:
                val_list[i] = '1'
            elif val_list[i] in zeros_list:
                val_list[i] = '0'        
        if comp1 in val_list:
            val = "T"
            return(val)

    if comp1 == str(comp2):   ### IF THE STRINGS MATCH PUT THEM AS EQUAL
        val = "T"
    else:
        val = "F"        ###UNEQUAL STRINGS
    return(val)
