# -*- coding: utf-8 -*-
"""
    Self Adaption System Website
    Author: Xiao Ning
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from werkzeug import secure_filename
from ResPool import client, res_manager
import json


# create our little application :)
UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = set(['txt', 'xml'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

res_list = []
goal_list = []
res_rule_id = 0

@app.route('/')
@app.route('/runtime')
def view_runtime():
    return render_template('runtime.html')

@app.route('/list')
def view_list():
    res_vals = client.get_all_res_value(res_list, -1)
    print res_vals
    return render_template('list.html',
                           resources=res_vals,
                           clock=client.get_clock())

@app.route('/customization')
def view_customization():
    return render_template('customization.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/import', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            client.reset_res_pool()
            global res_list,goal_list
            res_list = client.add_res_from_file(filepath)
            goal_list = filter(lambda x : 'goal' in x, res_list)
            return render_template('runtime.html')
    return render_template('import.html')

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
    res_list = client.add_res_from_file("./static/reslist_view.xml")
    goal_list = filter(lambda x : 'goal' in x, res_list)
    for res in res_list:
        if 'rule_id' in res:
            res_rule_id = res
    print "res_list=",res_list
    print "goal_list=",goal_list
    with app.app_context():
        app.run(port=5000)