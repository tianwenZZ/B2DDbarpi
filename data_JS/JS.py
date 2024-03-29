AppDt = GaudiExec()
AppDt.directory = '/home/zhoutw/DaVinciDev_v45r8' #lbEnv
AppDt.platform  = 'x86_64_v2-centos7-gcc10-opt'

def create_job(Name,Application,OptsFile,bkk_directory,NFilePerJob,MaxFiles,OutputTuple="Tuple.root"): 

   #Application.optsfile=[OptsFile]
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

#
"""
bkk=("/LHCb/Collision18/Beam6500GeV-VeloClosed-MagDown/Real Data/Reco18/Stripping34/90000000/BHADRON.MDST")  #14653files
create_job("B2DDbarpi-dv18-down",AppDt,"dv18.py",bkk,30,-1)
bkk=("/LHCb/Collision18/Beam6500GeV-VeloClosed-MagUp/Real Data/Reco18/Stripping34/90000000/BHADRON.MDST")  #
create_job("B2DDbarpi-dv18-up",AppDt,"dv18.py",bkk,30,-1)

bkk=("/LHCb/Collision17/Beam6500GeV-VeloClosed-MagDown/Real Data/Reco17/Stripping29r2/90000000/BHADRON.MDST")  #14653files
create_job("B2DDbarpi-dv17-down",AppDt,"dv17.py",bkk,30,-1)
bkk=("/LHCb/Collision17/Beam6500GeV-VeloClosed-MagUp/Real Data/Reco17/Stripping29r2/90000000/BHADRON.MDST")  #
create_job("B2DDbarpi-dv17-up",AppDt,"dv17.py",bkk,30,-1)
"""

bkk=("/LHCb/Collision16/Beam6500GeV-VeloClosed-MagDown/Real Data/Reco16/Stripping28r2/90000000/BHADRON.MDST")  #14653files
create_job("B2DDbarpi-dv16-down",AppDt,"dv16.py",bkk,60,-1)
bkk=("/LHCb/Collision16/Beam6500GeV-VeloClosed-MagUp/Real Data/Reco16/Stripping28r2/90000000/BHADRON.MDST")  #
create_job("B2DDbarpi-dv16-up",AppDt,"dv16.py",bkk,60,-1)

bkk=("/LHCb/Collision15/Beam6500GeV-VeloClosed-MagDown/Real Data/Reco15a/Stripping24r2/90000000/BHADRON.MDST") #3k
create_job("B2DDbarpi-dv15-down",AppDt,"dv15.py",bkk,15,-1)
bkk=("/LHCb/Collision15/Beam6500GeV-VeloClosed-MagUp/Real Data/Reco15a/Stripping24r2/90000000/BHADRON.MDST") #3k
create_job("B2DDbarpi-dv15-up",AppDt,"dv15.py",bkk,15,-1)
