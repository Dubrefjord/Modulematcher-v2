import sys
import os
import subprocess
import threading

def attack_node(json):
  #print("starting attack in wrapper")
  attack = subprocess.run(['python3',str(attack_script), json], capture_output=True, text=True) #subproces.run is ok because can wait until the detection module is finished before writing to the user.
  if attack.returncode==0 and len(attack.stdout)>0:
    #print(attack.args)
    print(attack.stdout)
  else:
    print("ERROR OCCURED IN ATTACKSCRIPT FOR NODE")
    print(attack.args)
    print(attack.stderr)
    print(attack.stdout)


dir_path = os.path.dirname(os.path.realpath(__file__))
#TODO test whether these exist or something. Use ArgumentParser
crawl_script = dir_path+'/'+sys.argv[1]
attack_script = dir_path+'/'+sys.argv[2]
url = sys.argv[3]
print("Wrapper running")
node_file = open("node_file.txt","w+")

#Create pipes for communication between crawler and wrapper
matcher_read_fd, crawler_write_fd = os.pipe()
crawler_read_fd, matcher_write_fd = os.pipe() #This currently isn't used, could probably remove in future. Not sure if it's possible to pass a dummy-value to pass_fds below.
os.environ['matcher_read_fd'] = str(matcher_read_fd)
os.environ['matcher_write_fd']= str(matcher_write_fd)
os.environ['crawler_write_fd'] = str(crawler_write_fd)
os.environ['crawler_read_fd']= str(crawler_read_fd)
crawler_env = os.environ.copy()

print("starting crawler")
crawler = subprocess.Popen(['python3',str(crawl_script) ,"--url" ,url, '--matcher'], pass_fds=[crawler_read_fd, crawler_write_fd], env=crawler_env, stdout=subprocess.DEVNULL) #try with stdin
os.close(crawler_read_fd)
os.close(crawler_write_fd)

crawler_output = open(matcher_read_fd,'r')
threads = []
attacked_jsons = []

for json in crawler_output:
  json = json.replace('\n','')
  if json in attacked_jsons: #Filter out duplicate nodes. If we want more advanced filter that for example removes duplicates where the cookies are in a different order we can make a deep comparison of the received node and the onces in the node list here. However, this is probably good enough.
      continue
  node_file.write(json+"\n")
  t= threading.Thread(target=attack_node, args=[json])
  attacked_jsons.append(json)
  t.start()
  threads.append(t)

node_file.close()
for thread in threads:
  thread.join()
