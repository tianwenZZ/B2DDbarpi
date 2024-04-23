AppDt = GaudiExec()
#The following is replaced by your up director, which can be generated following 4. of https://docs.qq.com/doc/DTk5HdmNiSEJNeXNE
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
#bkk=("/MC/2018/Beam6500GeV-2018-MagUp-Nu1.6-25ns-Pythia8/Sim09m-ReDecay01/Trig0x617d18a4/Reco18/Turbo05-WithTurcal/Stripping34Filtered/12197018/B2DDPI.STRIP.MDST")
#create_job("B2D0D0bpi4b2b-sqDalitz-dv18-up",AppDt,"filtered-dv18-mc-mu.py",bkk,4,-1)

bkk=("/MC/2018/Beam6500GeV-2018-MagDown-Nu1.6-25ns-Pythia8/Sim09m-ReDecay01/Trig0x617d18a4/Reco18/Turbo05-WithTurcal/Stripping34Filtered/12197018/B2DDPI.STRIP.MDST")
create_job("B2D0D0bpi4b2b-sqDalitz-dv18-down",AppDt,"filtered-dv18-mc-md.py",bkk,4,-1)

###
#bkk=("/MC/2018/Beam6500GeV-2018-MagUp-Nu1.6-25ns-Pythia8/Sim09m-ReDecay01/Trig0x617d18a4/Reco18/Turbo05-WithTurcal/Stripping34Filtered/12197070/B2DDPI.STRIP.MDST")
#create_job("B2D0D0bpi2b4b-sqDalitz-dv18-up",AppDt,"filtered-dv18-mc-mu.py",bkk,4,-1)

bkk=("/MC/2018/Beam6500GeV-2018-MagDown-Nu1.6-25ns-Pythia8/Sim09m-ReDecay01/Trig0x617d18a4/Reco18/Turbo05-WithTurcal/Stripping34Filtered/12197070/B2DDPI.STRIP.MDST")
create_job("B2D0D0bpi2b4b-sqDalitz-dv18-down",AppDt,"filtered-dv18-mc-md.py",bkk,4,-1)

