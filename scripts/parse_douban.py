#coding=utf-8
import douban.service

def get_book(isbn):
    client = douban.service.DoubanService(api_key = "07385bc1741d18c615a913445c574a52", secret = "")
    desc = dict(
            isbn13 = "",
            title = "",
            subtitle = "",
            price = "",
            pubdate = "",
            publisher = "",
            author = [],
            translator = [],
            isbn10 = "",
            pages = "",
            binding = "")

    book = client.GetBook("/book/subject/isbn/" + isbn)
    if book != None:
        for attr in book.attribute:
            if attr.name == "author":
                desc["author"].append(attr.text)
            elif attr.name == "translator":
                desc["translator"].append(attr.text)
            else:
                if attr.name in desc:
                    desc[attr.name] = attr.text
        desc["title"] = book.title.text
        desc["author"] =','.join(desc["author"])
        desc["translator"]=','.join(desc["translator"])
    return desc

def get_keys():
    return "isbn13 title subtitle price pubdate publisher author translator pages binding".split(' ') 
   
if __name__=="__main__":
    b=get_book('9787121006661')
    for k,v in b.items():
        print k,unicode(v,'utf-8')
