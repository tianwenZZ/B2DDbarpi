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
bkk=("/MC/2017/Beam6500GeV-2017-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x62661709/Reco17/Turbo04a-WithTurcal/Stripping29r2NoPrescalingFlagged/12197055/ALLSTREAMS.MDST")
create_job("B2DDpi-sqDalitz-dv17-down",AppDt,"dv17-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2017/Beam6500GeV-2017-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x62661709/Reco17/Turbo04a-WithTurcal/Stripping29r2NoPrescalingFlagged/12195004/ALLSTREAMS.MDST")
create_job("B2D0D0pi2b2b-dv17-down",AppDt,"dv17-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2017/Beam6500GeV-2017-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x62661709/Reco17/Turbo04a-WithTurcal/Stripping29r2NoPrescalingFlagged/12195007/ALLSTREAMS.MDST")
create_job("B2D0D0pi2b2b-sqDalitz-dv17-down",AppDt,"dv17-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2017/Beam6500GeV-2017-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x62661709/Reco17/Turbo04a-WithTurcal/Stripping29r2NoPrescalingFlagged/12197081/ALLSTREAMS.MDST")
create_job("B2DstpDmpi-dv17-down",AppDt,"dv17-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2017/Beam6500GeV-2017-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x62661709/Reco17/Turbo04a-WithTurcal/Stripping29r2NoPrescalingFlagged/12197075/ALLSTREAMS.MDST")
create_job("B2DstpDmpi-sqDalitz-dv17-down",AppDt,"dv17-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2017/Beam6500GeV-2017-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x62661709/Reco17/Turbo04a-WithTurcal/Stripping29r2NoPrescalingFlagged/12197071/ALLSTREAMS.MDST")
create_job("B2DpDstmpi-dv17-down",AppDt,"dv17-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2017/Beam6500GeV-2017-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x62661709/Reco17/Turbo04a-WithTurcal/Stripping29r2NoPrescalingFlagged/12197072/ALLSTREAMS.MDST")
create_job("B2DpDstmpi-sqDalitz-dv17-down",AppDt,"dv17-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2017/Beam6500GeV-2017-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x62661709/Reco17/Turbo04a-WithTurcal/Stripping29r2NoPrescalingFlagged/12197016/ALLSTREAMS.MDST")
create_job("B2DstDstpi-dv17-down",AppDt,"dv17-mc-md.py",bkk,4,-1)

###
bkk=("/MC/2017/Beam6500GeV-2017-MagDown-Nu1.6-25ns-Pythia8/Sim09m/Trig0x62661709/Reco17/Turbo04a-WithTurcal/Stripping29r2NoPrescalingFlagged/12197017/ALLSTREAMS.MDST")
create_job("B2DstDstpi-sqDalitz-dv17-down",AppDt,"dv17-mc-md.py",bkk,4,-1)
