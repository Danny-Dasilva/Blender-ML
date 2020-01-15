import xml.etree.ElementTree as ET
import xml.dom.minidom
# create the file structure
data = ET.Element('data')
items = ET.SubElement(data, 'items')
item1 = ET.SubElement(items, 'item')
item2 = ET.SubElement(items, 'item')
item1.set('name','item1')
item2.set('name','item2')
item1.text = 'item1abc'
item2.text = 'item2abc'

# create a new XML file with the results
mydata = ET.tostring(data, encoding='unicode')

xml = xml.dom.minidom.parseString(mydata)
xml_pretty_str = xml.toprettyxml()
print(xml_pretty_str)



with open("items2.xml", "w") as file:
    file.write(xml_pretty_str)
