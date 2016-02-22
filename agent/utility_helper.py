from __future__ import division
import json
import types
import re
import sys
import ResPool.client as client
Res_list={}
res_cache={}
res_buff={}
poname_num={}
class Res:
    def __init__(self,name,value=0):
        self.name=name
        self.value=value
        self.isnew=True

    @classmethod
    def Getvalue(self,name,clock):
        return client.get_res_value(name, clock)

    @classmethod
    def Setvalue(self,name,value):
        client.set_res_value(name,value)

    def update_value(self, clock=-1):
        #self.value=client.get_res_value(self.name, clock)
        self.value = res_cache.get(self.name)
        self.isnew=True
        return self.value
    def set_value(self,value):
        self.value=value
        self.isnew=False
    def uploading_value(self):
        if self.isnew==False:
            #client.set_res_value(self.name,self.value)
            res_buff[self.name]=self.value
            print "i am uploading the value of "+ self.name


class Capability:
    @classmethod
    def set_value(self,name,value):
        for ro in Res_list:
            for re in Res_list[ro]:
                if Res_list[ro][re].name==name:
                    Res_list[ro][re].set_value(value)




    def Run(self):
        print("i am empty")

    def __init__(self,name,action):
        self.name=name
        self.action=action

class Policy:

    def __init__(self,role,id,type,condition,action):
        self.role=role
        self.id=id
        self.type=type
        self.condition=condition
        self.action=action
        poname_num[self.id]=0

    def If_Trigger(self):
        #print self.condition
        #print self.condition
        return eval(self.condition)



    def Run(self):
        print(self.action)
        exec(self.action)


class Policy_List:
    def __init__(self):
        self.pl={}

    def Add_Policy(self,policy):
        self.pl[policy.id]=policy

    def Delete_Policy(self,policy):
        if type(policy) is types.StringType:
            del self.rl[policy]
        if isinstance(policy,Policy):
            del self.rl[policy.id]
        del self.pl[policy]

    def Get_Dict(self):
        return self.pl

    def runall(self):
        str1=""
        for (poname,po) in self.pl.items():
            po.Run()
            if poname in poname_num.keys():
                poname_num[poname]+=1
            else:
                poname_num[poname]=1
            str1=str1+"policy:"+poname+" num:"+str(poname_num[poname])+"##"
        str1=""
        ssss=sorted(poname_num.iteritems(), key = lambda asd:asd[0], reverse = False)
        for (poname,num) in ssss:
            str1=str1+poname+"   "+str(num)+"\r\n"
        # for (poname,num) in poname_num.items():
        #     str1=str1+poname+"   "+str(num)+"\r\n"
        print "hahaha"+str1
        return str1

    def Show(self):
        for (poname,po) in self.pl.items():
            print("i am policy"+po.id)




class Role:


    def __init__(self,jsontring,res_goal=[]):

        self.policylist=Policy_List()
        s=json.loads(jsontring)
        self.name=s["name"]
        Res_list[self.name]={}
        for rn in res_goal:
            #print rn
            if rn not in Res_list[self.name]:
                Res_list[self.name][rn]=Res(rn)

        for po in s["policylist"]:
            condition=po["condition"]
            rr = re.compile(r'Res\[([^\]]*)\]\.value',re.VERBOSE)
            for resname in rr.findall(condition):
                if resname not in Res_list[self.name]:
                    Res_list[self.name][resname]=Res(resname)



            p=Policy(self.name,po["id"],po["type"],rr.subn(r'Res_list["'+self.name+r'"]["\1"].value',condition)[0],po["action"])
            self.policylist.Add_Policy(p)
    def get_res_value(self,res_name):
        return Res_list[self.name][res_name].value

    def update(self):
        for key in Res_list[self.name]:
            Res_list[self.name][key].update_value()


    def uploading(self):
        for n in Res_list[self.name]:
            Res_list[self.name][n].uploading_value()

    def Get_Policydict(self):
        return self.policylist.Get_Dict()



    def goal(self):
        lightintensity=Res_list[self.name]["light.intensity"].value
        tvpower=Res_list[self.name]["tv.power"].value
        computerpower=Res_list[self.name]["computer.power"].value
        airconpower=Res_list[self.name]["aircondition.power"].value
        heaterlevel=Res_list[self.name]["heater.level"].value
        blind=Res_list[self.name]["blind"].value
        time=Res_list[self.name]["time"].value
        weather=Res_list[self.name]["weather"].value
        outsidetemperature=Res_list[self.name]["outside.temperature"].value
        airconlevel=Res_list[self.name]["aircondition.level"].value



        if Res_list[self.name]["aircondition.mode"].value == "cool":
            airmode=0
        else:
            airmode=1
        window=Res_list[self.name]["window"].value

        power=lightintensity/3+tvpower+computerpower+airconpower+heaterlevel/3
        if power > 5:
            power=5

        if time=="daytime":
            if weather=="sunny":
                brightness=lightintensity+blind*2
            else:
                brightness=lightintensity+blind
        else:
            brightness=lightintensity

        if window == 1:
            temperature=outsidetemperature+airconlevel*(airmode-0.5)*2/5+heaterlevel/5
        else:
            temperature=outsidetemperature+airconlevel*(airmode-0.5)*2/2+heaterlevel/2


        intpower=int(power)
        intbrightness=int(brightness)
        inttemperature=int(temperature)
        #client.set_res_value("temperature",temperature)
        Res_list[self.name]["temperature"].set_value(temperature)
        #client.set_res_value("power",intpower)
        Res_list[self.name]["power"].set_value(intpower)
        #client.set_res_value("brightness",intbrightness)
        Res_list[self.name]["brightness"].set_value(intbrightness)





        es=1-intpower/4
        #client.set_res_value("room:goal_energy",es)
        Res_list[self.name]["room:goal_energy"].set_value(es)

        ec=intpower/2
        if ec >1:
            ec=1
        #client.set_res_value("room:goal_effective_control",ec)
        Res_list[self.name]["room:goal_effective_control"].set_value(ec)

        if intbrightness<3:
            vc=intbrightness/2
        else:
            vc=2.5-intbrightness/2
        #client.set_res_value("room:goal_visual_comfort",vc)
        Res_list[self.name]["room:goal_visual_comfort"].set_value(vc)

        if inttemperature<=2:
            tc=inttemperature/2
        else:
            tc=(5-inttemperature)/3
        #client.set_res_value("room:goal_thermal_comfort",tc)
        Res_list[self.name]["room:goal_thermal_comfort"].set_value(tc)

        og=(es+ec+vc+tc)/4
        #client.set_res_value("room:goal_overall",og)
        Res_list[self.name]["room:goal_overall"].set_value(og)





    def Show(self):
        print("i am role "+self.name)
        for (key, po) in self.Get_Policydict().items():

            print("it is policy "+po.id)
            if po.If_Trigger():
                po.Run()
                #print "aaaaa"

class Role_List:
    def __init__(self):
        self.rl={}

    def Add_Role(self,role):
        self.rl[role.name]=role

    def Delete_Role(self,role):

        if type(role) is types.StringType:
            del self.rl[role]
            del Res_list[role]
        if isinstance(role,Role):
            del Res_list[role.name]
            del self.rl[role.name]

    def update(self):
        for k in self.rl:
            self.rl[k].update()

    def goal(self):
        for key in self.rl:
            self.rl[key].goal()


    def uploading(self):
        for key in self.rl:
            self.rl[key].uploading()
    def Get_Dict(self):
        return self.rl

    def Show(self):
        for (k,r) in self.rl.items():
            r.Show()






