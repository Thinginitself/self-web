__author__ = 'root'
import json
import types
import re
import os

def stringtopolicy(id, type,str):
    ss=str.split("|-")
    v=ss[0]
    cc=ss[1]
    ca=cc.split("->")
    c=ca[0]
    a=ca[1]
    #print v
    #print c
    #print a
    condition=""

    for ev in v.split("^"):
        feature=ev.split("=")[0].replace(" ","")

        value=ev.split("=")[1].replace(" ","")
        if "[" in value:
            condition += "Res["+feature+"].value in "+value +" and "
        else:
            if value == "open" or value == "on":
                value="1"

            elif value == "close" or value == "off":
                value="0"
            else:
                value="'"+value+"'"
            condition += "Res["+feature+"].value == "+value +" and "


    for ev in c.split("^"):
        feature=ev.split("=")[0].replace(" ","")

        value=ev.split("=")[1].replace(" ","")
        if "[" in value:
            condition += "Res["+feature+"].value in "+value +" and "
        else:
            if value == "open" or value == "on":
                value="1"

            elif value == "close" or value == "off":
                value="0"
            else:
                value="'"+value+"'"
            condition += "Res["+feature+"].value == "+value +" and "
    l=len(condition)-4
    condition=condition[0:l]


    action=""
    for ac in a.split(";"):
        feature=ac.split(":=")[0].replace(" ","")
        feature="'"+feature+"'"
        value=ac.split(":=")[1].replace(" ","")

        if value == "open" or value == "on":
            value="1"

        elif value == "close" or value == "off":
                value="0"
        else:
            value="'"+value+"'"
        action+="Capability.set_value("+feature+", "+value+");"


    answer='{'
    answer+='"id":"'+id+'",'
    answer+='"type":"'+type+'",'
    answer+='"condition":"'+condition+'",'
    answer+='"action":"'+action+'"'
    answer+='}'
    return answer
def stringtopolicylist(liststr,splitchar,name="null name"):
    policylist = '['
    x=0
    for po in liststr.split(splitchar):
        x = x + 1

        policylist += stringtopolicy(str(x),"A",po)
        policylist +=','

    policylist =policylist[0:len(policylist)-1]+ ']'
    answer = '{'
    answer += '"name":"'+name+'",'
    answer += '"policylist":'+policylist+''
    answer += '}'
    return answer

#str1="Light.Power = off |- Time = daytime ^ Blind.State = close -> Blind.State := open; Window.State :=open ###Light.Power = off |- Time = daytime ^ Blind.State = [1,4] -> Blind.State := close; Window.State :=close"
#FFprint stringtopolicylist(str1,"###")