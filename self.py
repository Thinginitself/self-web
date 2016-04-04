# -*- coding: utf-8 -*-
"""
    Self Adaption System Website
    Author: Xiao Ning
"""

import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from werkzeug import secure_filename
from ResPool import client, res_manager, utils, Xutils
import json
from contextlib import closing


# create our little application :)
UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = set(['json'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


res_rule_id = 0
goal_list = []
all_res = []
goal_data = []
show_goal = []



@app.route('/')
@app.route('/environment_main')
def view_environment_main():
    return render_template('environment_main.html')



@app.route('/environment_list')
def view_environment_list():

    environment_name = request.args.get("environment_name",'default')
    return render_template('environment_list.html',environment_name=environment_name,show_goal=show_goal)

@app.route('/agent_choose')
def view_agent_choose():
    return render_template('agent_choose.html')

@app.route('/runtime_choose')
def view_choose():
    cur = g.db.execute('select distinct environment from entries')
    environments = [row for row in cur.fetchall()]
    entries = []
    for j in environments:
        i = j[0]
        print i
        num = g.db.execute('select count(*) from entries where environment = (?)', [i]).fetchall()[0][0]
        entries.append([i,num])
    return render_template('runtime_choose.html', entries=entries)

@app.route('/set_environment', methods=['POST'])
def op_set_environment():
    global res_list,goal_list,res_rule_id
    environment_name = request.form.get("environment_name",'default')
    cur = g.db.execute('select name, format, initial, delay, next, rule from entries where environment = (?) order by id desc', [environment_name])
    setting_res = [row for row in cur.fetchall()]
    for n, f, i, d, ni, r in setting_res:
        i = json.loads(i)
        model = {"format":f, "initial":i}
        update = {"delay":d, "next":ni, "rule":json.JSONDecoder().decode(r)}
        print "===========",n,model,update
        client.add_res(n,model,{'Default': utils.warp_update(update)})
        res_list.append(n)

    goal_list = filter(lambda x : 'goal' in x, res_list)
    for res in res_list:
        if 'rule_id' in res:
            res_rule_id = res
    return redirect(url_for('view_agent_choose'))

@app.route('/add_res_from_file',methods=['POST'])
def op_add_res_from_file():
    file = request.files['res_file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        res_list = Xutils.get_res_list_from_environment_json(filepath)
        for res in res_list:
            print res
            client.add_res(*res)
            all_res.append(res[0])
        print client.get_all_res_value(all_res,-1)
    return redirect(url_for('view_environment_list'))

@app.route('/add_property_from_file',methods=['POST'])
def op_add_property_from_file():
    file = request.files['property_file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        property_list = Xutils.get_res_list_from_property_json(filepath)
        for res in property_list:
            client.add_res(*res)
            all_res.append(res[0])
    return redirect(url_for('view_environment_list'))

def get_goal_list(data):
    print data
    for tmp in data["goal"]:
        goal_list.append("room:" + tmp["name"])
        if "goal" in tmp.keys():
            get_goal_list(tmp)

def get_show_goal(data,dep):
    for tmp in data["goal"]:
        show_goal.append((tmp["name"],dep))
        if "goal" in tmp.keys():
            get_show_goal(tmp,dep+1)

@app.route('/add_goal_from_file',methods=['POST'])
def op_add_goal_from_file():
    global goal_data
    file = request.files['goal_file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        with open(filepath, "r") as fin:
            context = fin.read()
            client.add_res("room:goal_model",{"initial":context},None)
            goal_data = json.load(open(filepath))
            get_goal_list(goal_data)
            get_show_goal(goal_data,1)
    return redirect(url_for('view_environment_list'))

@app.route('/add_software_from_file',methods=['POST'])
def op_add_software_from_file():
    file = request.files['software_file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        with open(filepath, "r") as fin:
            context = fin.read()
            client.add_res("room:software_model",{"initial":context},None)
    return redirect(url_for('view_environment_list'))

@app.route('/runtime_main')
def view_runtime():
    return render_template('runtime.html')

@app.route('/runtime_detail')
def view_list():
    res_vals = client.get_all_res_value(all_res, -1)
    print res_vals
    return render_template('list.html',
                           resources=res_vals,
                           clock=client.get_clock())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/tick',methods=['GET', 'POST'])
def op_tick():
    clock = client.ticktock()
    return json.dumps({'clock':clock,'rule_id':client.get_res_value(res_rule_id)})

@app.route('/ticktock_to_next_update',methods=['GET', 'POST'])
def op_ticktock_to_next_update():
    clock = client.ticktock_to_next_update(True)
    return json.dumps({'clock':clock,'rule_id':client.get_res_value(res_rule_id)})


@app.route('/goal_values',methods=['GET', 'POST'])
def op_get_goal_values():
    goal_vals = client.get_all_res_values(goal_list)
    print "goal_values:",goal_vals
    ret = []
    for name, vals in goal_vals.items():
        ret.append({
            'name':name,
            'data':vals
        })
    return json.dumps(ret)

if __name__ == '__main__':
    client.reset_res_pool()
    with app.app_context():
        app.run(port=5000,threaded=True)