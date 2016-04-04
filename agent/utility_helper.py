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

class chushihua:
    def __init__(self,name):
        self.name=name
        #self.str1=client.get_res_value(name+":ruleset",-1)
        #self.str2=client.get_res_value(name+":software_model",-1)
        #self.str3=client.get_res_value(poname_num+":goal_model",-1)

        file_object = open("./static/ruleset.json")
        try:
            self.str1= file_object.read()
        finally:
            file_object.close()

        file_object = open("./static/software.json")
        try:
            self.str2= file_object.read()
        finally:
            file_object.close()

        file_object = open("./static/goal.json")
        try:
            self.str3= file_object.read()
        finally:
            file_object.close()

        file_object = open("./static/property.json")
        try:
            self.str4= file_object.read()
        finally:
            file_object.close()

        self.s1=json.loads(self.str1)

        self.s2=json.loads(self.str2)
        self.s3=json.loads(self.str3)
        self.s4=json.loads(self.str4)
        self.polist={}
        self.relist={}
        self.property={}
        self.fun1()
        self.fun2(self.s2["software"]["feature"])
        self.fun3(self.s3)
        self.fun4()
        #json.dump(self.polist)
        print(self.relist)

    def fun1(self):
        popo=[]
        num=0
        for rule in self.s1["ruleset"]:
            num=num+1
            poli={}
            poli["id"]=str(num)
            poli["type"]="A"
            strcon=self.changecon(rule["condition"])
            strac=self.changeac(rule["action"])
            poli["condition"]=strcon
            poli["action"]=strac
            popo.append(poli)

        self.polist["name"]=self.name
        self.polist["policylist"]=popo

    def changecon(self,condition):
        texts = condition.split("and")
        ans="1==1"
        for text in texts:
            text=text.lstrip()
            text=text.rstrip()
            if "==" in text:
                tt=text.split("==")
                ans=ans+" and "+"Res["+tt[0]+"].value=="+tt[1]
            elif ">=" in text:
                tt=text.split(">=")
                ans=ans+" and "+"Res["+tt[0]+"].value>="+tt[1]
            elif "<=" in text:
                tt=text.split("<=")
                ans=ans+" and "+"Res["+tt[0]+"].value<="+tt[1]
            elif ">" in text:
                tt=text.split(">")
                ans=ans+" and "+"Res["+tt[0]+"].value>"+tt[1]

            elif "<" in text:
                tt=text.split("<")
                ans=ans+" and "+"Res["+tt[0]+"].value<"+tt[1]

        return ans



    def changeac(self,action):
        texts=action.split("and")
        ans=""
        for text in texts:
            text=text.lstrip()
            text=text.rstrip()
            tt=text.split("==")
            #tt[0].lstrip()
            #tt[0].rstrip()

            ans=ans+"Capability.set_value(\'"+tt[0]+"\',"+tt[1]+");"

        return ans

    def fun2(self,fe):
        for key in fe.keys():
            if "range" in fe[key]:
                #lala={}
                #lala[key]=str(fe[key]["range"][0])

                self.relist[key]=str(fe[key]["range"][0])
                self.add_property(key,fe[key])
            else:
                self.fun2(fe[key])

    def add_property(self,key,value):

        if type(value["impact"]) is list:
            for im in value["impact"]:
                guanxi={}
                for index in range(len(im["effect"])):
                    guanxi[value["range"][index]]=im["effect"][index]

                if im["related_property"] not in self.property:
                    self.property[im["related_property"]]={}

                if key not in self.property[im["related_property"]]:
                    self.property[im["related_property"]][key]={}
                self.property[im["related_property"]][key]=guanxi

        else:
            guanxi={}
            for index in range(len(value["impact"]["effect"])):
                #print(value["impact"]["effect"][index])
                guanxi[value["range"][index]]=value["impact"]["effect"][index]
            if value["impact"]["related_property"] not in self.property:
                self.property[value["impact"]["related_property"]]={}
            if key not in self.property[value["impact"]["related_property"]]:
                self.property[value["impact"]["related_property"]][key]={}
            self.property[value["impact"]["related_property"]][key]=guanxi


    def fun3(self,goal):
        #lala={}
        #lala[self.name+":goal"]=0
        #self.relist.append(lala)
        self.relist[self.name+":goal"]=0
        for gg in goal["goal"]:
            #lala={}
            #lala[self.name+":"+gg["name"]]=0
            #self.relist.append(lala)
            self.relist[self.name+":"+gg["name"]]=0
            if "goal" in gg.keys():
                self.fun3(gg)
            else:
                if type(gg["related_property"]) is list:
                    for haha in gg["related_property"]:
                        #lala={}
                        #lala[haha["name"]]=0
                        #self.relist.append(lala)
                        self.relist[haha["name"]]=0
                else:
                    #lala={}
                    #lala[gg["related_property"]["name"]]=0
                    #self.relist.append(lala)
                    self.relist[gg["related_property"]["name"]]=0

    def fun4(self):
        for prope in self.s4["property"]:
            #lala={}
            #lala[prope["name"]]=prope["initial"]
            #self.relist.append(lala)
            self.relist[prope["name"]]=prope["initial"]




    def show(self):
        print(self.polist)
        print(self.relist)
        print(self.property)










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


    def __init__(self,jsontring,res_goal={},property={}):

        self.policylist=Policy_List()
        self.property=property
        s=json.loads(jsontring)
        self.name=s["name"]
        Res_list[self.name]={}
        for key in res_goal.keys():
            if key not in Res_list[self.name]:
                Res_list[self.name][key]=Res(key)

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
        self.property_jisuan()
        #goal_dep= self.get_res_value(self.name+":goal_model")
        file_object = open("./static/goal.json")
        try:
            str3= file_object.read()
        finally:
            file_object.close()
        
        self.goal_everyone(self.name+":goal",json.loads(str3))

    def property_jisuan(self):
        for pro in self.property.keys():
            ans=0
            n=0
            for ziyuan in self.property[pro].keys():
                ans=ans+self.property[pro][ziyuan][self.get_res_value(ziyuan)]
                n=n+1

            ans=ans/n
            print("asdfgrwefewfwefwwfw"+str(ans))
            print(Res_list[self.name])
            Res_list[self.name][str(pro)].set_value(ans)


    def goal_jisuan(self,goal_name,property):
        if goal_name not in Res_list[self.name]:
            Res_list[self.name][goal_name]=Res(goal_name)
        ans=0

        if type(property) is list:
            for pp in property:
                ans+=float(pp["weight"])*self.get_res_value(pp["name"])
        else:
            print(type(property["weight"]))
            print("fhksahfksdahfkjhsadkjfhsadkhfksdhfd")
            print(type(self.get_res_value(property["name"])))
            ans=float(property["weight"])*self.get_res_value(property["name"])

        Res_list[self.name][goal_name].set_value(ans)

    def goal_everyone(self,goal_name,str_json):
        #print(str_json)
        #s=json.loads(str_json)
        s=str_json
        if goal_name not in Res_list[self.name]:
            Res_list[self.name][goal_name]=Res(goal_name)
        ans=0
        for gg in s["goal"]:
            if "goal" in gg.keys():
                self.goal_everyone(self.name+":"+gg["name"],gg)
                ans+=float(gg["weight"])*self.get_res_value(self.name+":"+gg["name"])
            else:
                self.goal_jisuan(self.name+":"+gg["name"],gg["related_property"])
                ans+=float(gg["weight"])*self.get_res_value(self.name+":"+gg["name"])


        Res_list[self.name][goal_name].set_value(ans)














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






