import sys
import os

path_to_run = sys.argv[1]
new_path = sys.argv[2]
run_name = sys.argv[3]
sample_name = sys.argv[4]
Lane = sys.argv[5]
adapt = sys.argv[6]

if not os.path.isdir("/"+new_path+"/"+run_name+"/"+sample_name):
    os.makedirs("/"+new_path+"/"+run_name+"/"+sample_name)
os.chdir("/"+new_path+"/"+run_name+"/"+sample_name)

if "," not in Lane:
    if "," not in adapt:
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane+"/"+run_name+"_L0"+Lane+"_"+adapt+"_1.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane+"/"+run_name+"_L0"+Lane+"_"+adapt+"_2.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
    elif "," in adapt:
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane+"/"+run_name+"_L0"+Lane+"_"+adapt.split(",")[0]+"_1.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane+"/"+run_name+"_L0"+Lane+"_"+adapt.split(",")[0]+"_2.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane+"/"+run_name+"_L0"+Lane+"_"+adapt.split(",")[1]+"_1.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane+"/"+run_name+"_L0"+Lane+"_"+adapt.split(",")[1]+"_2.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo bash -c \"cat **_1.fq.gz > "+sample_name+"_1.fq.gz\"")
        os.system("sudo bash -c \"cat **_2.fq.gz > "+sample_name+"_2.fq.gz\"")
elif "," in Lane:
    if "," not in adapt:
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane.split(",")[0]+"/"+run_name+"_L0"+Lane.split(",")[0]+"_"+adapt+"_1.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane.split(",")[0]+"/"+run_name+"_L0"+Lane.split(",")[0]+"_"+adapt+"_2.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane.split(",")[1]+"/"+run_name+"_L0"+Lane.split(",")[1]+"_"+adapt+"_1.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane.split(",")[1]+"/"+run_name+"_L0"+Lane.split(",")[1]+"_"+adapt+"_2.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo bash -c \"cat **_1.fq.gz > "+sample_name+"_1.fq.gz\"")
        os.system("sudo bash -c \"cat **_2.fq.gz > "+sample_name+"_2.fq.gz\"")
    elif "," in adapt:
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane.split(",")[0]+"/"+run_name+"_L0"+Lane.split(",")[0]+"_"+adapt.split(",")[0]+"_1.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane.split(",")[0]+"/"+run_name+"_L0"+Lane.split(",")[0]+"_"+adapt.split(",")[0]+"_2.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane.split(",")[1]+"/"+run_name+"_L0"+Lane.split(",")[1]+"_"+adapt.split(",")[0]+"_1.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane.split(",")[1]+"/"+run_name+"_L0"+Lane.split(",")[1]+"_"+adapt.split(",")[0]+"_2.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane.split(",")[0]+"/"+run_name+"_L0"+Lane.split(",")[0]+"_"+adapt.split(",")[1]+"_1.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane.split(",")[0]+"/"+run_name+"_L0"+Lane.split(",")[0]+"_"+adapt.split(",")[1]+"_2.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane.split(",")[1]+"/"+run_name+"_L0"+Lane.split(",")[1]+"_"+adapt.split(",")[1]+"_1.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo mv /"+path_to_run+"/"+run_name+"/L0"+Lane.split(",")[1]+"/"+run_name+"_L0"+Lane.split(",")[1]+"_"+adapt.split(",")[1]+"_2.fq.gz /"+new_path+"/"+run_name+"/"+sample_name)
        os.system("sudo bash -c \"cat **_1.fq.gz > "+sample_name+"_1.fq.gz\"")
        os.system("sudo bash -c \"cat **_2.fq.gz > "+sample_name+"_2.fq.gz\"")

