from bs4 import BeautifulSoup
import pandas as pd
import glob



import glob, os
os.chdir("Kyle")

all_files = []
for f in glob.glob("*.xml"):
    all_files.append(f)

line1 = '<file_tag>'
line2 = '</file_tag>'
with open('concatenated_dump', 'w') as f:
    f.write(line1.rstrip('\r\n') + '\n')
    for fname in all_files:
        with open(fname) as infile:
            for line in infile:
                f.write(line)
    f.write(line2.rstrip('\r\n') + '\n')


infile = open("concatenated_dump","r")
contents = infile.read()
xml = BeautifulSoup(contents,'xml')

attribute = []
for item in xml.findAll('xn:attributes'):
    attribute.append(item)

moc_list = []
for all_moc in attribute:
    k = all_moc.findAll()
    moc_list.append(k)

column_1 = []
column_2 = []
index = []
paths = []
Unique_Index = []
for all_moc in moc_list:
    for moc in all_moc:
            head = []
            if all_moc.index(moc) == 0:
                i = moc.text
                Unique_Index.append(i)
                for parent in moc.parents:
                    if parent.has_attr('id') and parent.name != "VsDataContainer":
                        head.append("%s-%s"%(parent.name,parent.get('id')))
                    if parent.has_attr('id') and parent.name == "VsDataContainer":
                        head.append("%s-%s"%(parent.find('xn:vsDataType').text,parent.get('id')))
                path = ("-".join(reversed(head)))
            val_name = moc.name
            val_txt = moc.text.split()
            if len(val_txt) == 1:
#                print('%s : %s'%(val_name,val_txt[0]))
                column_1.append(str(val_name))
                column_2.append(str(val_txt[0]))
                index.append(i)
                paths.append(path)
            if len(val_txt) == 0:
#                print('%s : '%(val_name))
                column_1.append(str(val_name))
                column_2.append(" ")
                index.append(i)
                paths.append(path)
            val_txt = []

def worksheet_name(moc):
    if moc[0] == 'v':
        return(moc[6:36])
    else:
        return(moc)




Moc_List = list(sorted(set(Unique_Index)))
df = pd.DataFrame({'INDEX':index, 'PATHS': paths, 'MOC':column_1, 'VALUES': column_2 })



os.chdir("..")

writer = pd.ExcelWriter('Kyle.xlsx',options={'strings_to_urls': False})

for moc in Moc_List:
    f = df.loc[df['INDEX'] == moc]
    f.set_index('INDEX', inplace=True)
    pivot_table = f.pivot_table(index=['PATHS'],
                         columns=["MOC"],
                         values=["VALUES"],
                         aggfunc=lambda x: ' '.join(str(v) for v in x))
    w_name = worksheet_name(moc)
    pivot_table.to_excel(writer, sheet_name = w_name)
writer.close()
