from redisworks import Root
from time import sleep,time

root = Root(host='10.3.141.1', port=6379, db=0)
from ast import literal_eval


def write_config(change_list: list):
    try:
        root.flush()
        config=literal_eval(str(root.config))
        for element in change_list:
            config[element['component']][element['attribute']] = element['value']
        root.update_timestamp = time()
        root.config = config
    except Exception as e:
        print(e)
        print("Couldn't write config, trying again.")
        sleep(1)
        return write_config(change_list)

while True:
    
    sleep(2)
    write_config([{'component':'purge_switch','attribute':'on','value':True},{'component':'purge_switch','attribute':'disabled','value':True}])
    print('on')
    sleep(2)
    write_config([{'component':'purge_switch','attribute':'on','value':False},{'component':'purge_switch','attribute':'disabled','value':False}])
    print('off')
