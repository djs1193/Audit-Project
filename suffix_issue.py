from bs4 import BeautifulSoup
from string_compare import *
import pandas as pd
import glob, os

####SUPPRESSING THE CHAINED COPYING WARNING IN PANDAS
pd.options.mode.chained_assignment = None


#####IMPROVING THE DISPLAY ON THE TERMINAL (FOR SELF ON THE MAC)
pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


####IMPORTING THE GOLD STANDARD EXCEL
gold_standard_df = pd.read_excel('new_gs_essential.xlsx',index = False)

####LISTING OUT ALL THE MOC (CURRENTLY) FOR WHICH COMPARISION CAN BE DONE
##### NO MOC WITH "=" INCLUDED TILL NOW
curr_moc_list  = pd.read_excel('curr_moc.xlsx',index = False)
moc_list_gs = curr_moc_list['GS MOC'].tolist()


######CHANGING THE DIRECTORY TO SEE TO CHILDREN OF THE FOLDER TO EXTRACT ALL THE XML FILES
os.chdir("dumps")


######STORING THE XML FILES AS A LIST
all_files = []
for f in glob.glob("*.xml"):
    all_files.append(f)


######INTRODUCING  THE TAGS SO THAT PARSING DOESNT STOP ONLY AFTER READING FIRST XML
###CONCATENATE ALL XML BETWEEN THE FILE TAGS
line1 = '<file_tag>'
line2 = '</file_tag>'
with open('concatenated_dump', 'w') as f:
    f.write(line1.rstrip('\r\n') + '\n')
    for fname in all_files:
        with open(fname) as infile:
            for line in infile:
                f.write(line)
    f.write(line2.rstrip('\r\n') + '\n')


######READING THE CONCATENATED XML USING BS4
infile = open("concatenated_dump","r")
contents = infile.read()
xml = BeautifulSoup(contents,'xml')


######GET ALL THE ATTRIBUTE TAGS AND DATA WITHIN THESE TAGS
######THIS IS WHERE ALL THE MOC AND THE PARAMETERS THEY HAVE ARE STORED INDIVIDUALLY
attribute = []
for item in xml.findAll('xn:attributes'):
    attribute.append(item)


###### WITHIN EACH ATTRIBUTE GET ALL THE TAGS (PARAMETERS) AND STORE THEM IN A LIST
moc_list = []
for all_moc in attribute:
    k = all_moc.findAll()
    moc_list.append(k)


######MAIN

column_1 = []                                                                   ####THIS WILL STORE THE PARAMETER
column_2 = []                                                                   #####THIS WILL STORE THE VALUE OF PARAMETER
index = []                                                                      #####THIS WILL STORE THE NAME OF THE MOC FOR WHICH THE PARAMETER AND VALUES BELONG
paths = []                                                                      #####THIS WILL STORE THE PATH TO WHICH THE MOC BELONGS TO (PARENT)
Unique_Index = []                                                                #####THIS WILL STORE ALL THE MOCS BELONGING IN THE DUMP


for all_moc in moc_list:                                                        ###FOR ALL THE GROUP OF TAGS IN 1 ATTRIBUTE
    for moc in all_moc:                                                         ###FOR ALL TAGS WITHIN THIS GROUP
            head = []                                                           #### THIS WILL KEEP ON STORING THE PARENTS OF A TAG
            if all_moc.index(moc) == 0:                                         ### WE ONLY TAKE PARENT OF 1ST TAG IN THE GROUP TO INCREASE EFFECIENCY
                i = moc.text                                                    ### THE 1ST TAG IS ALWAYS THE MOC NAME, EXTRACT THE NAME OF MOC
                Unique_Index.append(i)                                          ### PUT IT IN THE UNIQUE MOC LIST
                for parent in moc.parents:                                      ###NOW FOR ALL THE PARENTS THAT HAVE BEEN ATTAINED
                    if parent.has_attr('id') and parent.name != "VsDataContainer":
                        head.append("%s-%s"%(parent.name,parent.get('id')))     ####GET THE ID AND INCLUDE IT IN THE PARENT PATH
                    if parent.has_attr('id') and parent.name == "VsDataContainer":### IF PARENT NAME IS VsDataContainer WE WANT ID OF THE CONTAINER IN PATH
                        head.append("%s-%s"%(parent.find('xn:vsDataType').text,parent.get('id')))### GET THE ID OF THE PATH
                path = ("-".join(reversed(head)))                               ###STRING FORMATTING OF OF THE PARENTS TO PRINT THE HEAD
            val_name = moc.name                                                  ####THE PARAMETER WITHIN THE ATTRIBUTE IS EXTRACTED
            val_txt = moc.text.split()                                          ##### BS4 PARSES ALL THE TEXT VALUES SO WE SPLIT THEM IN A LIST
            if len(val_txt) == 1:                                                #### IF LENGTH IS 1 THEN ONLY CONSIDER THIS AS THE PARAMTER AND ITS VALUE
                column_1.append(val_name)
                column_2.append(val_txt[0])                                     #### THE FIRST VALUE FROM THE TEXT IS THE TRUE VALUE
                index.append(i)                                                 ###PUT THE MOC TO WHICH THIS VALUE AND PARAMETER BELONGS TO
                paths.append(path)                                              ###PUT THE PATH TO WHICH THIS MOC BELONGS TO
            if len(val_txt) == 0:
                column_1.append(val_name)                                       #### IF THE PARAMETER HAS NO VALUE JUST PUT A SPACE
                column_2.append(" ")
                index.append(i)
                paths.append(path)
            val_txt = []


#####GET ALL THE ATTRIBUTES(vsCONTAINERS)
Moc_List = list(sorted(set(Unique_Index)))                                      ### REMOVE REPETITION IN THE MOC NAMES AS ATTRIBUTES CAN/WILL HAVE SAME MOC NAME.

#####READ THE DATA INTO A DATA FRAME
raw_data_df = pd.DataFrame({'MOC':index, 'PATHS': paths, 'PARAMETER':column_1, 'VALUES': column_2 })

writer = pd.ExcelWriter('comparison_with_suffix.xlsx')


for moc in moc_list_gs:                                                         ### FOR ALL THE MOCS IN THE GOLD STANDARD
    raw_moc = "vsData"+moc                                                      #### APPEND THEM BY THIS STRING (FOR RAW DATA)
    if raw_moc in Moc_List:                                                     #### CHECK IF THE RAW MOC IS IN THE MOCS FOR THIS PARTICULAR DUMP
        df1 = (raw_data_df.loc[raw_data_df["MOC"] == raw_moc])                  #### GET THE ENTIRE ROW FROM DATA FRAME FOR THIS MOC AND MAKE A DATAFRAME
        df2 = gold_standard_df.loc[pd.notnull(gold_standard_df['Software Default Value'])]    ####LOAD ALL ROWS OF GOLD STANDARD WHERE VALUES IS NOT NULL
        df2 = df2.loc[(df2['MOC'] == moc)     &  (df2['HW/SW load'] == 'L18Q2G1G2')]       ####GET ALL ROWS FROM GOLD STANDARD FOR THIS PARTICULAR MOC AND LOAD

        my_list1 = df1["PARAMETER"].tolist()                                     ### PUT ALL THE PARAEMTERS IN LIST FOR ITERATION
        ############################
        my_list2 = set(df2["Parameter"].tolist())                                ### GET ALL THE PARAMETERS FROM GS (SET IS USED TO OVERCOME THE SUFFIX PROBLEM)

        gs = []
        para = []
        suffix = []
        for para1 in my_list1  :                                                ### FOR ALL PARAMETERS IN RAW MOC
                if para1 not in my_list2:                                       ### IF THE PARAMETER IS NOT IN GS PUT NAN
                    gs.append('Nan')
                    para.append("Nan")
                    suffix.append("  ")
                else:
                    for para2 in my_list2:                                      ### FOR ALL PARAMETERS IN THE GOLD STANDARD
                        if para1 == para2:
                            local_vals = []
                            local_sufs = []
                            df3 = df2.loc[df2['Parameter'] == para1]
                            para.append(df3.iloc[0]['Parameter'])
                            tot = len(df3.columns)
                            for i in range(tot):
                                try:
                                    local_vals.append(str(df3.iloc[i]['Software Default Value']))
                                except IndexError:
                                    local_vals.append('Nan')
                                try:
                                    local_sufs.append(str(df3.iloc[i]['Suffix']))
                                except IndexError:
                                    local_sufs.append('Nan')
                            while "Nan" in local_vals:
                                local_vals.remove("Nan")
                            while "Nan" in local_sufs:
                                local_sufs.remove("Nan")
                            if len(local_vals) > 0:
                                gs.append(",".join(local_vals))
                            else:
                                gs.append("  ")
                            if len(local_sufs) > 0:
                                suffix.append(",".join(local_sufs))
                            else:
                                suffix.append("  ")




        df1['G_S_PARA'] = para                                                  ##ADD THESE COLUMNS TO ORIGINAL DATAFRAME
        df1['SUFFIX'] = suffix
        df1['GOLD_STANDARD'] = gs


        comp1 = df1["VALUES"].tolist()                                          ### PUTTING IN THE LIST FOR COMPARISION
        comp2 = df1["GOLD_STANDARD"].tolist()

        Comparision = []
        for i in range (len(comp1)):                                            ### HEAD TO HEAD COMPARISION
            val  = compare_values(comp1[i],str(comp2[i]))
            Comparision.append(val)

        df1['COMPARISION'] = Comparision                                        #### MAKE THE COMPARISION COLUMN


        df1 = df1.loc[(df1['COMPARISION'] == 'F')]                              ### IF NEEDED ONLY GET THOSE ROWS WHERE WE GOT FALSE VALUE.
        df1.to_excel(writer, sheet_name = moc)

writer.close()
