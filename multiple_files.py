from bs4 import BeautifulSoup                                                   #FOR PARSING THE DATA
import pandas as pd                                                             #FOR MAKING DATAFRAMES
import glob                                                                     #TO READ THE CHILDREN OF MAIN DIRECTORY (READ ALL XML FILES)
import os                                                                       #SHIFTING THE DIRECTORIES(MOVING UP AND DOWN)

                                                                                #SEE ALL THE CHILDREN OF THE DIRECTORY (SEE ALL THE XML FILES)
os.chdir("Kyle")

all_files = []                                                                  #WILL CONTAIN ALL THE XML FILES AS A LIST
for f in glob.glob("*.xml"):                                                    #GET ONLY FILES WITH XML EXTENSION IN THE
    all_files.append(f)                                                         #PUT THEM INTO THE LIST

line1 = '<file_tag>'                                                            #TAG PREFIXED TO THE 'CONCATED DUMP'(INTRODUCED LATER)
line2 = '</file_tag>'                                                           #TAG SUFFIXED TO THE 'CONCATED DUMP'(INTRODUCED LATER)
with open('concatenated_dump', 'w') as f:                                       #CREATE A NEW FILE CALLED CONACATED DUMPS
    f.write(line1.rstrip('\r\n') + '\n')                                        #WRITE THE PREFIXED TAG (THIS IS DONE SO THAT BS4 DOESNT STOP PARSING---
    for fname in all_files:                                                     #---- ONLY AFTER READING THE FIRST XML OUT OF POSSIBLY MANY
        with open(fname) as infile:                                             #FOR ALL XML DUMPS IN ALL_FILES
            for line in infile:                                                 #OPEN THE XML FILE AND WRITE EACH OF ITS LINE
                f.write(line)
    f.write(line2.rstrip('\r\n') + '\n')                                        #PUT THE END TAG.THIS IS WHERE THE PARSING SHOULD STOP


infile = open("concatenated_dump","r")                                          #READ THE CONCATENATED DUMP INTO CONTENTS
contents = infile.read()
xml = BeautifulSoup(contents,'xml')                                             #PARSE IT USING BUILT IN LIBRARY FOR XML

attribute = []                                                                  #THIS WILL CONTAIN ALL THE TAG STARTING FROM ATTRIBUTE (<ATTRIBUTE>)...<ALLTAGS>,(</ATTRIBUTE>)
for item in xml.findAll('xn:attributes'):                                       #THIS IS HOW THE ATTRIBUTE TAG IS NAMED IN THE RAW DATA
    attribute.append(item)                                                      #LIST OF ALL ATTRIBUTES IS STORED

moc_list = []                                                                   #THIS WILL CONTAIN ALL TAGS WITHIN A SINGLE ATTRIBUTE
for all_moc in attribute:                                                       #FOR AN ATTRIBUTE FIND ALL THE TAGS WITHIN THAT ONE ATTRIBUTE( DO FOR ALL ATTRIBUTES)
    k = all_moc.findAll()
    moc_list.append(k)                                                          #PUT ALL THE TAGS FOR 1 ATTRIBUTE AS AN ITEM OF THE LIST

column_1 = []                                                                   #THESE LISTS WILL CONTAIN INDEX:index,  PATHS: paths,
column_2 = []                                                                   #MOC:column_1,VALUES:column_2
index = []
paths = []
Unique_Index = []
for all_moc in moc_list:                                                        #FOR ALL TAGS WITHIN ALL ATTRIBUTES
    for moc in all_moc:                                                         #FOR A SINGLE TAG IN ONE ATTRIBUTE
            head = []                                                           #THIS IS MUTABLE LIST FOR EVERY ITERATION USED FOR STORING PATH
            if all_moc.index(moc) == 0:                                         #DONE TO IMPROVE EFFECIENCY (ONLY DONE FOR 1ST TAG IN THE LIST)
                i = moc.text                                                    #THE FIRST TAG IS ALWAYS MOC NAME. GET ITS NAME AS TEXT
                Unique_Index.append(i)                                          #PUT IT IN UNIQUE AS THIS WILL AVOID DUPLICATION
                for parent in moc.parents:                                      #GETTING PATH OF THE FIRST TAG(THIS WILL BE PATH FOR ALL TAGS WITHIN THE SAME ATTRIBUTE)
                    if parent.has_attr('id') and parent.name != "VsDataContainer":
                        head.append("%s-%s"%(parent.name,parent.get('id')))
                    if parent.has_attr('id') and parent.name == "VsDataContainer":   #IF ITS DATA CONTAINER WE WANT WHATS INSIDE THE ID FOR THE PATH NAME
                        head.append("%s-%s"%(parent.find('xn:vsDataType').text,parent.get('id')))
                path = ("-".join(reversed(head)))                               #THE ORDER IS REVERSE SO THAT WE GO FROM (HIGH TO LOW)
            val_name = moc.name                                                 #IF INDEX IS NOT 0 .GET THE TAG NAME
            val_txt = moc.text.split()                                          #GET WHATS INSIDE THE TAG. THIS MIGHT GIVE TEXT VALUES FOR THE CHILD TAG ALSO. SO WE MAKE LIST OF ALL TAG VALUES---
            if len(val_txt) == 1:                                               #IF LIST HAS ONE VALUE,THIS IS IDEAL(AS TAG HAS NO CHILD) GET THIS VALUE
#                print('%s : %s'%(val_name,val_txt[0]))
                column_1.append(str(val_name))                                  #PUT THE PARAMETER NAME
                column_2.append(str(val_txt[0]))                                #PUT THE VALUE OF THAT PARAMETER
                index.append(i)                                                 #PUT THE MOC NAME FOR THAT INDIVIDUAL PARAMETER
                paths.append(path)                                              #PUT THE PATH FOR THAT INDIVIDUAL PARAMETER
            if len(val_txt) == 0:                                               #IF THERE WAS NO VALUE PRESENT FOR THE PARAMETER
#                print('%s : '%(val_name))
                column_1.append(str(val_name))                                  #PUT THE PARAMETER NAME
                column_2.append(" ")                                            #EMPTY STRING FOR PARAMETER VALUE
                index.append(i)
                paths.append(path)
            val_txt = []                                                        #MAKE SURE VAL TEXT IS EMPTY FOR THE NEXT PARAMETER

def worksheet_name(moc):
    "THIS FUNCTION IS USED FOR NAMING THE WORKSHEET NAME."
    if moc[0] == 'v':                                                           #IF THE MOC NAME STARTS FROM I.E OF TYPE VSDATA
        return(moc[6:36])                                                       #GET RID OF VSDATA AND MAKE SURE LENGTH IS LESS THAN 31
    else:
        return(moc)                                                             #ELSE FOR E.G TYPE HXL.. LET IT BE THE SAME NAME




Moc_List = list(sorted(set(Unique_Index)))                                      #TAKE ONLY UNIQUE VALUES AS ATTRIBUTES MIGHT HAVE THE SAME MOC NAME.
df = pd.DataFrame({'INDEX':index, 'PATHS': paths, 'MOC':column_1, 'VALUES': column_2 })#MAKE THE DATAFRAME



os.chdir("..")                                                                  #WE WANT EXCEL TO BE GENERATED IN ROOT DIRECTORY

writer = pd.ExcelWriter('Kyle.xlsx',options={'strings_to_urls': False})         #SUPRESS ANY HYPERLINK ISSUES IN EXCEL

for moc in Moc_List:                                                            # FOR A MOC IN ALL MOC
    f = df.loc[df['INDEX'] == moc]                                              # GET ALL ROWS FOR THIS MOC
    f.set_index('INDEX', inplace=True)                                          # GET RID OF THE PANDAS INDEX
    pivot_table = f.pivot_table(index=['PATHS'],                                #PIVOT THE TABLE FOR NEPA FORMAT LIKE STRUCTURE
                         columns=["MOC"],
                         values=["VALUES"],
                         aggfunc=lambda x: ' '.join(str(v) for v in x))
    w_name = worksheet_name(moc)
    pivot_table.to_excel(writer, sheet_name = w_name)
writer.close()
