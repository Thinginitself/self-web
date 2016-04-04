from threading import Thread
from time import sleep
from agent import utility_helper
#import utility_helper
__author__ = 'root'
import json
import ResPool.client as client
import os


rolelist= utility_helper.Role_List()
def Play_Role(jsonstring,res_attention,pr): #
    role= utility_helper.Role(jsonstring,res_attention,pr)
    rolelist.Add_Role(role)


def add_res(relist):
    for key in relist.keys():

        t=type(relist[key])
        if t is str:
            mo={}
            mo["type"]="string"
            mo["initial"]=relist[key]

        else:
            mo={}
            mo["type"]="number"
            mo["initial"]=relist[key]

        client.add_res(str(key),mo,None)

def Delete_Role(role):
    rolelist.Delete_Role(role)

def Find_Trigger_Policy(type):# find the trigger policy which type is type
    tpl= utility_helper.Policy_List()

    for (rolename,role) in rolelist.Get_Dict().items():
        for (policyid, policy) in role.Get_Policydict().items():
            if policy.If_Trigger() and policy.type==type:
                tpl.Add_Policy(policy)
    return tpl

def If_Conflict(action1,action2):#
    if action1==action2:
        return True
    return False


def run():
    print "running..."
    utility_helper.res_cache = client.get_all()
    rolelist.update()
    triggered_policylist=Find_Trigger_Policy("A")
    posr=triggered_policylist.runall()
    print("i am posr "+posr)
    rolegoal=rolelist.goal()
   # print("i am rolegoal "+str(rolegoal))

    utility_helper.res_buff = {}
    rolelist.uploading()
    utility_helper.res_buff["room:rule_id"] = posr
    client.set_all_res_value(utility_helper.res_buff)
    #client.set_res_value("room:rule_id",posr)


path=os.path.abspath('.')

str1='{"name":"mobile",   "policylist":[{"id":"001","type":"A","condition":"2>1","action":"print(\'wahahah\');print(\'action accaafda\')"},{"id":"002","type":"O","condition":"2<3","action":"print(\'heheheh\')"}]}'
str2='{"name":"telephone","policylist":[{"id":"003","type":"A","condition":"2<Res[temp].value and 6==6","action":"Capability.set_value(\'temp\',True)"},{"id":"004","type":"O","condition":"2<3","action":"print(\'heafgdeh\')"},{"id":"010","type":"A","condition":"1 < 2 and 0 < Res[Window-state].value","action":"Capability.set_value(\'Airconditioner.state\',1)"}]}'
str3='{"name":"context","policylist":[{"id":"001","type":"A","condition":"Res[blind].value == 1 and Res[brightness].value > 3","action":"Capability.set_value(\'light.power\', 0)"},{"id":"002","type":"A","condition":"Res[blind].value == 0 and Res[brightness].value < 3","action":"Capability.set_value(\'light.power\',0)"},{"id":"003","type":"A","condition":"Res[heater].value == 1 and Res[airquality].value > 1","action":"Capability.set_value(\'window\',0)"},{"id":"004","type":"A","condition":"Res[heater].value == 1 and Res[temperature].value > 3","action":"Capability.set_value(\'aircondition.power\',0)"},{"id":"005","type":"A","condition":"Res[heater].value == 0 and Res[temperature].value < 3","action":"Capability.set_value(\'aircondition.power\',1);Capability.set_value(\'aircondition.mode\',\'heat\')"},{"id":"006","type":"A","condition":"Res[aircondition.power].value == 1 and Res[airquality].value > 1","action":"Capability.set_value(\'window\',0)"},{"id":"007","type":"A","condition":"Res[aircondition.mode].value == \'heating\' and Res[temperature].value > 3","action":"Capability.set_value(\'heater\',0)"},{"id":"008","type":"A","condition":"Res[aircondition.mode].value == \'cool\'","action":"Capability.set_value(\'heater\',0)"},{"id":"009","type":"A","condition":"Res[window].value == 1 and Res[somebodyhome].value ==0","action":"Capability.set_value(\'blind\',0)"},{"id":"010","type":"A","condition":"Res[window].value == 0 and Res[airquality].value < 2","action":"Capability.set_value(\'aircondition.power\',1)"},{"id":"011","type":"A","condition":"Res[computer.volume].value == \'currentValue\' and Res[env.volume].value > 4 and Res[tv.power].value == 1","action":"Capability.set_value(\'tv.volume\',1)"},{"id":"012","type":"A","condition":"Res[computer.volume].value == \'currentValue\' and Res[env.volume].value > 4 and Res[computer.power].value == 1","action":"Capability.set_value(\'computer.volume\',1)"},{"id":"013","type":"A","condition":"Res[somebodyhome].value == 0","action":"Capability.set_value(\'tv.power\',0);Capability.set_value(\'computer.power\',0)"},{"id":"014","type":"A","condition":"Res[weather].value == \'rainy\'","action":"Capability.set_value(\'window\',0)"},{"id":"015","type":"A","condition":"Res[weather].value == \'snowy\'","action":"Capability.set_value(\'window\',0)" }]}'
str4='{"name":"context","policylist":[{"id":"001","type":"A","condition":"Res[aircondition.mode].value==\'cool\' ","action":"Capability.set_value(\'aircondition.power\',1);Capability.set_value(\'window\',0);Capability.set_value(\'heater.power\',0)"},{"id":"002","type":"A","condition":"Res[aircondition.mode].value==\'heat\'","action":"Capability.set_value(\'aircondition.power\',1);Capability.set_value(\'window\',0)"},{"id":"003","type":"A","condition":"Res[aircondition.mode].value==\'heat\' and Res[temperature].value > 3","action":"Capability.set_value(\'heater.power\',0)"},{"id":"004","type":"A","condition":"Res[heater.power].value == 1","action":"Capability.set_value(\'window\',0)"},{"id":"005","type":"A","condition":"Res[aircondition.power].value == 1 and Res[outside.temperature].value < 3","action":"Capability.set_value(\'aircondition.mode\',\'heat\')"},{"id":"006","type":"A","condition":"Res[aircondition.power].value == 1 and Res[outside.temperature].value > 3","action":"Capability.set_value(\'aircondition.mode\',\'cool\')"},{"id":"007","type":"A","condition":"Res[light.intensity].value == 0 and Res[time].value ==\'daytime\' and Res[somebodyhome].value == 1","action":"Capability.set_value(\'blind\',1)"},{"id":"008","type":"A","condition":"Res[light.intensity].value == 0 and Res[tv.power].value == 1","action":"Capability.set_value(\'tv.brightness\',2)"},{"id":"009","type":"A","condition":"Res[light.intensity].value == 0 and Res[computer.power].value == 1","action":"Capability.set_value(\'computer.brightness\',2)"},{"id":"010","type":"A","condition":"Res[heater.level].value == 0 and Res[temperature].value < 2","action":"Capability.set_value(\'aircondition.mode\',\'heat\');Capability.set_value(\'aircondition.power\',1)"},{"id":"011","type":"A","condition":"Res[window].value == 0 and Res[temperature].value < 2","action":"Capability.set_value(\'heater.level\',1);Capability.set_value(\'heater.power\',1)"}]}'
#Play_Role(str)
#Play_Role(str2)

chu=utility_helper.chushihua("room")
#chu.show()

#Play_Role(str4,['room:goal_visual_comfort','room:goal_thermal_comfort','room:goal_overall','room:goal_effective_control','room:goal_energy','aircondition.power','blind','window','weather','brightness','power','humidity','volume','light.intensity','heater.level','aircondition.mode','time','outside.temperature','aircondition.level'])
#add_ziyuantoyuanzhukongjian(chu.relist)
add_res(chu.relist)
#print chu.relist
#print "=======",client.get_res_value("brightness"),"====="
#client.add_res("brightness",{"initial":0},None)
#print "=======",client.get_res_value("brightness"),"====="
Play_Role(json.dumps(chu.polist),chu.relist,chu.property)

rolelist.Show()



"""
triggered_policylist=Find_Trigger_Policy("O")
print("======")
triggered_policylist.Show()
rolelist.Delete_Role("mobile")
print("_______________")
rolelist.Show()
triggered_policylist=Find_Trigger_Policy("A")
triggered_policylist.Show()

"""

