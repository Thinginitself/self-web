
from ResPool import client, res_manager, utils

client.reset_res_pool()
sen = "sensor"
client.add_res(sen, {"format":"number",'initial': 20}, None)
print '----',client.get_res_value(sen),'-----'