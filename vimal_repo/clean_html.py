# Importing essential libraries

from bs4 import BeautifulSoup
import codecs
import re


# reading html file
file = codecs.open("./job_description.rtf", 'r')

html_file=file.read()


print('******************************************')
def cleanhtml(html_text):
    ''' takes the html file and return the text information by romoving all the tags except basic tags'''
    comments= "<!--.*?-->" 
    basictag= '^["<h1><h2><h3><h4><h5><h6><p><br><ul><ol><li><div><span>"]'                         
    remove_comment_soup= re.sub(comments, "", html_text)
    basic_tag_soup= re.sub(basictag,'',remove_comment_soup)
    soup = BeautifulSoup(basic_tag_soup,'lxml')
    for tag in soup():
        for attribute in ["class", "id", "style"]:
           del tag[attribute]
    find_a=soup.find_all('a')
    find_a[1].decompose()
    return(soup)

clean_html=cleanhtml(html_file)
print(type(clean_html))
#converting bs4.BeautifulSoup object to  str object. So, that //,\\ can be removed 
text=str(clean_html)
text=text.replace('\\','')
text=text.replace('//','')
print(text)


with open('./clean.html', 'w') as f:
    f.write(text)

print('**************** done ***********************')





