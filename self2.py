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
from ResPool import client, res_manager, utils
import json
from contextlib import closing


# create our little application :)
UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = set(['txt', 'xml'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATABASE'] = "./self.db"



res_list = []
goal_list = []
res_rule_id = 0

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():   
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    g.db.close()






@app.route('/')
@app.route('/environment_main')
def view_environment_main():
    cur = g.db.execute('select distinct environment from entries')
    environments = [row for row in cur.fetchall()]
    entries = []
    for j in environments:
        i = j[0]
        print i
        num = g.db.execute('select count(*) from entries where environment = (?)', [i]).fetchall()[0][0]
        entries.append([i,num])
    return render_template('environment_main.html', entries=entries)

@app.route('/environment_list')
def view_environment_list():
    environment_name = request.args.get("environment_name",'default')
    cur = g.db.execute('select type, name, format, initial from entries where environment = (?) order by id desc', [environment_name])
    setting_res = [row for row in cur.fetchall()]

    return render_template('environment_list.html', resources=setting_res, environment_name=environment_name)

@app.route('/add_res', methods=['POST'])
def op_add_res(): 
    res_environment = request.form.get("res_environment")
    res_name = request.form.get("res_name")
    res_format = request.form.get("res_format")
    res_initial = request.form.get("res_initial")
    res_delay = request.form.get("res_delay")
    res_next = request.form.get("res_next")
    res_rule = request.form.get("res_rule")
    res_type = request.form.get("res_type", "resource")
    g.db.execute('insert into entries (environment, name, type, format, initial, delay, next, rule) values (?, ?, ?, ?, ?, ?, ?)',
                 [res_environment, res_name, res_type, res_format, res_initial, res_delay, res_next, res_rule])
    g.db.commit()
    return redirect(url_for('view_environment_list'))

@app.route('/del_res', methods=['POST'])
def op_del_res():
    del_res_name = request.form.get("del_res_name")
    print del_res_name
    g.db.execute("delete from entries where name = (?)", [del_res_name])
    g.db.commit()
    return redirect(url_for('view_environment_list'))

@app.route('/environment_custom',methods=['POST', 'GET'])
def view_environment_custom():
    res_name = request.args.get("res_name","default")
    res_environment = request.args.get("res_environment","home")
    return render_template('environment_custom.html',pre_res_name=res_name,pre_res_environment=res_environment)

@app.route('/custom_res',methods=['POST','GET'])
def view_custom_res():
    res_name = request.args.get("res_name","default")
    res_environment = request.args.get("res_environment","home")
    return render_template('custom_res.html',pre_res_name=res_name,pre_res_environment=res_environment)

@app.route('/custom_property',methods=['POST','GET'])
def view_custom_property():
    res_name = request.args.get("res_name","default")
    res_environment = request.args.get("res_environment","home")
    return render_template('custom_property.html',pre_res_name=res_name,pre_res_environment=res_environment)


@app.route('/custom_goal',methods=['POST','GET'])
def view_custom_goal():
    res_name = request.args.get("res_name","default")
    res_environment = request.args.get("res_environment","home")
    return render_template('custom_goal.html',pre_res_name=res_name,pre_res_environment=res_environment)


@app.route('/custom_software',methods=['POST','GET'])
def view_custom_software():
    res_name = request.args.get("res_name","default")
    res_environment = request.args.get("res_environment","home")
    return render_template('custom_software.html',pre_res_name=res_name,pre_res_environment=res_environment)



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

@app.route('/add_setting_from_file',methods=['POST'])
def op_add_setting_from_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        with open(filepath, "r") as fin:
            context = fin.read()
            data = utils.get_data_from_xml_context(context)
        for res in data["res_list"]['res']:
            g.db.execute('insert into entries (environment, name, type, format, initial, delay, next, rule) values (?, ?, ?, ?, ?, ?, ?, ?)',[file.filename, res["@name"], 'resource', res["model"]["format"], res["model"]["initial"], res["update"]["delay"], res["update"]["next"], json.JSONEncoder().encode(res["update"]["rule"])])
            g.db.commit()
    return redirect(url_for('view_environment_main'))


@app.route('/agent_choose', methods=['POST', 'GET'])
def view_agent_choose():
    if request.method == 'POST':
        return redirect(url_for('view_runtime'))
    return render_template('agent_choose.html')



@app.route('/runtime_main')
def view_runtime():
    return render_template('runtime.html')

@app.route('/runtime_detail')
def view_list():
    res_vals = client.get_all_res_value(res_list, -1)
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
    init_db()
    client.reset_res_pool()
    with app.app_context():
        app.run(port=5000,threaded=True)