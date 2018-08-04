from bs4 import BeautifulSoup
import pandas as pd


infile = open("HXL_00831.xml","r")
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
for all_moc in moc_list:
    for moc in all_moc:
            head = []
            if all_moc.index(moc) == 0:
                for parent in moc.parents:
                    if parent.has_attr('id') and parent.name != "VsDataContainer":
                        head.append("%s-%s"%(parent.name,parent.get('id')))
                    if parent.has_attr('id') and parent.name == "VsDataContainer":
                        head.append("%s-%s"%(parent.find('xn:vsDataType').text,parent.get('id')))
                path = ("-".join(reversed(head)))
                column_1.append("PATH")
                column_2.append(path)
            val_name = moc.name
            val_txt = moc.text.split()
            if len(val_txt) == 1:
                print('%s : %s'%(val_name,val_txt[0]))
                column_1.append(val_name)
                column_2.append(val_txt[0])
            if len(val_txt) == 0:
                print('%s : '%(val_name))
                column_1.append(val_name)
                column_2.append(" ")
            val_txt = []
    column_1.append(" ")
    column_2.append(" ")
    print("-"*40)

df = pd.DataFrame({'MOC':column_1, 'VALUES': column_2})
df.set_index('MOC', inplace=True)

df.to_csv('moc_list.csv')
