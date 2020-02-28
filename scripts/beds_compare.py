v7 = {"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[],"10":[],"11":[],"12":[],"13":[],"14":[],"15":[]}
v6 = {"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[],"10":[],"11":[],"12":[],"13":[],"14":[],"15":[]}

n_v7 = 0
#with open("S31285117_Covered_v7.bed","r") as f:
with open("chr1_v7.bed","r") as f:
    for line in f:
        c = int(line.split("\t")[1])
        while c <= int(line.split("\t")[2]):
            v7[str(len(str(c)))].append(c)
            c += 1
            n_v7 += 1

n_v6 = 0
with open("chr1_v6.bed","r") as f:
    for line in f:
        c = int(line.split("\t")[1])
        while c <= int(line.split("\t")[2]):
            v6[str(len(str(c)))].append(c)
            c += 1
            n_v6 += 1

print("n_v6 = "+str(n_v6))
print("n_v7 = "+str(n_v7))

est = 0
net = 0
for a in v7.items():
    for b in v6.items():
        if a[0] == b[0]:
            for el in a[1]:
                if el in b[1]:
                    est += 1
                else:
                    net += 1
print("v7 v v6")
print("est = "+str(est))
print("net = "+str(net))