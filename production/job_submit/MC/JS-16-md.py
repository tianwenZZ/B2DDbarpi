AppDt = GaudiExec()
#The following is replaced by your down director, which can be generated following 4. of https://docs.qq.com/doc/DTk5HdmNiSEJNeXNE
#http://lhcb-portal-dirac.cern.ch/DIRAC/
AppDt.directory = '/home/zhoutw/DaVinciDev_v45r8' #lbEnv
AppDt.platform  = 'x86_64_v2-centos7-gcc10-opt'

def create_job(Name,Application,OptsFile,bkk_directory,NFilePerJob,MaxFiles,OutputTuple="Tuple.root"): 

   Application.options =[OptsFile]
   job=Job(
	   name = Name,
	   application  = Application,
	   splitter     = SplitByFiles( filesPerJob = NFilePerJob, maxFiles = MaxFiles, ignoremissing = True ),
	   inputsandbox = [],
	   outputfiles  = [DiracFile(OutputTuple)],
	   backend      = Dirac(),
	   inputdata    = BKQuery(bkk_directory,dqflag=['OK']).getDataset()
	   )
   job.submit()

###
bkk=("/MC/2016/Beam6500GeV-2016-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x6139160F/Reco16/Turbo03a/Stripping28r2NoPrescalingFlagged/12197055/ALLSTREAMS.MDST")
create_job("B2DDpi-sqDalitz-dv16-down",AppDt,"dv16-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2016/Beam6500GeV-2016-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x6139160F/Reco16/Turbo03a/Stripping28r2NoPrescalingFlagged/12195004/ALLSTREAMS.MDST")
create_job("B2D0D0pi2b2b-dv16-down",AppDt,"dv16-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2016/Beam6500GeV-2016-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x6139160F/Reco16/Turbo03a/Stripping28r2NoPrescalingFlagged/12195007/ALLSTREAMS.MDST")
create_job("B2D0D0pi2b2b-sqDalitz-dv16-down",AppDt,"dv16-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2016/Beam6500GeV-2016-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x6139160F/Reco16/Turbo03a/Stripping28r2NoPrescalingFlagged/12197081/ALLSTREAMS.MDST")
create_job("B2DstpDmpi-dv16-down",AppDt,"dv16-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2016/Beam6500GeV-2016-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x6139160F/Reco16/Turbo03a/Stripping28r2NoPrescalingFlagged/12197075/ALLSTREAMS.MDST")
create_job("B2DstpDmpi-sqDalitz-dv16-down",AppDt,"dv16-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2016/Beam6500GeV-2016-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x6139160F/Reco16/Turbo03a/Stripping28r2NoPrescalingFlagged/12197071/ALLSTREAMS.MDST")
create_job("B2DpDstmpi-dv16-down",AppDt,"dv16-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2016/Beam6500GeV-2016-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x6139160F/Reco16/Turbo03a/Stripping28r2NoPrescalingFlagged/12197072/ALLSTREAMS.MDST")
create_job("B2DpDstmpi-sqDalitz-dv16-down",AppDt,"dv16-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2016/Beam6500GeV-2016-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x6139160F/Reco16/Turbo03a/Stripping28r2NoPrescalingFlagged/12197016/ALLSTREAMS.MDST")
create_job("B2DstDstpi-dv16-down",AppDt,"dv16-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2016/Beam6500GeV-2016-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x6139160F/Reco16/Turbo03a/Stripping28r2NoPrescalingFlagged/12197017/ALLSTREAMS.MDST")
create_job("B2DstDstpi-sqDalitz-dv16-down",AppDt,"dv16-mc-md.py",bkk,4,-1)
