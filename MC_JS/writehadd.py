import json

json_name = "jobid_name_map.json"
with open(json_name, "r") as f:
    mapJobidNames = json.load(f)

decay = ["B2DDpi-sqDalitz", "B2D0D0pi2b2b", "B2D0D0pi2b2b-sqDalitz", "B2DstpDmpi",
         "B2DstpDmpi-sqDalitz", "B2DpDstmpi", "B2DpDstmpi-sqDalitz", "B2DstDstpi", "B2DstDstpi-sqDalitz"]
mag = ["up", "down"]
year = ["15", "16", "17", "18"]

mapDecay = {}
for dec in decay:
    for m in mag:
        for y in year:
            jobname = f"{dec}-dv{y}-{m}"
            mapDecay[jobname] = [mapJobidNames[jobname]]
            if jobname+"_splitted" in mapJobidNames.keys():
                mapDecay[jobname].append(mapJobidNames[jobname+"_splitted"])

haddscript = open("myhadd.sh", "w")
haddscript.write("#!/bin/bash\n")
for dec in decay:
    haddscript.write(f"mkdir {dec}\n")
    for m in mag:
        for y in year:
            ids = mapDecay[f"{dec}-dv{y}-{m}"]
            haddscript.write(f"hadd {dec}/{dec}_20{y}_m{m[0]}.root ")
            for ii in ids:
                haddscript.write(f"{ii}/* ")
            haddscript.write("\n")
    haddscript.write("\n\n##############################\n")
haddscript.close()
