import os,sys


def resub(job,subids=[],status="failed",nn=2):
    dsts=[]
    for sj in jobs(job).subjobs:
        if sj.status != "completed":
            sj.force_status("failed")
            ft = sj.inputdata.files[0]
            prfix,suffixes = ft.lfn_prefix,ft.suffixes
            dsts.extend([prfix+dstfile for dstfile in suffixes])
    if not dsts: return 0
    print (dsts)
    nj=jobs(job).copy()
    nj.name="%i_resub_%s"%(job,status)
    nj.inputdata=LHCbDataset(files=['LFN:'+lfn for lfn in dsts]) 
    nj.splitter = SplitByFiles( filesPerJob = nn, maxFiles = -1, ignoremissing = True )
    nj.submit()
#some jobs completed, but in fact crashed (Segmentation violation)
def resub_crash(job,subids=[],status="failed",nn=2):
    dsts=[]
    name=""
    for sj in jobs(job).subjobs:
        if sj.status == "completed" and sj.outputfiles[0].lfn == '':
            sj.force_status("failed")
        #if (sj.status == status or not status) and (sj.id in subids or not subids):
            dsts.extend([dstfile.lfn for dstfile in sj.inputdata.files])
            name += ("_"+str(sj.id))
    if not dsts: return 0
    print (dsts)
    nj=jobs(job).copy()
    nj.name="%i_resub_%s"%(job,status) + name
    nj.inputdata=LHCbDataset(files=['LFN:'+lfn for lfn in dsts]) 
    nj.splitter = SplitByFiles( filesPerJob = nn, maxFiles = -1, ignoremissing = True )
    nj.submit()

#sid = [23, 28, 41, 69, 80, 81, 87, 94, 96, 100, 101, 105, 106, 108, 109, 110, 112, 115, 118, 119, 120, 121, 122, 123, 124, 125, 128, 130, 132, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 147, 149, 150, 151, 154, 155, 156, 160, 163, 169, 176, 189, 220, 243, 254, 262, 290, 311, 336, 362, 386, 442, 446] 
#resub(2763,sid,"")
#
#
#sid=[1, 17, 18, 19, 30, 62, 74, 77, 92, 93, 96, 100, 113, 152, 166, 174, 207, 213, 242, 266, 271, 286, 294, 323, 381]
#resub(2764,sid,"")


#resub(2872,[],"failed")
#resub(2873,[],"failed")
#resub(2878,[],"failed",2)
#resub(2879,[],"failed",5)
#resub(2922,[],"failed",3)
#resub(2924,[],"failed",10)
#resub(3021,[],"failed",10)
#resub(3022,[],"failed",10)
#B+ -> chi_c K(KK) MC, data, runI
#for ii in range(3049,3057):
#    resub(ii,[],"failed",1) 

#for ii in range(3057,3065):
#    resub(ii,[],"failed",3) 
#for ii in range(3057,3065):
#    resub(ii,[],"failed",3) 
#    #resub_crash(ii,[],"failed",3) 
#resub(3111,[],"failed",3) 
#for sid in range(4): resub(3718+sid,[],"failed",5) 
#for sid in range(1): resub(3721+sid,[],"failed",5) 
#for sid in range(2): resub(3722+sid,[],"failed",20) 
#for sid in range(4): resub(3724+sid,[],"failed",20) 
for sid in range(6): resub(3793+sid,[],"failed",3) 

