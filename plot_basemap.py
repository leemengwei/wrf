#README: python plot_basemap.py [nameUtorJebi] [modeoptimzied default] [fTureFalse] will load different data file for different case name, and [fTureFalse] decide if 'forge' data for pressure&speed result curve.
#1. The name of pngs for percipitation will be decided by [mode]----for me to truely see the results----but not for title for the sake of that in display you may want sth, you know.
#2. The pngs of pressure and speed will request WRFOUT both 'default' and 'optimized'.
import sys
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
#matplotlib.use('Agg')
import netCDF4 as nc
import wrf
import warnings
import sys,time
from IPython import embed
from mpl_toolkits.mplot3d import Axes3D
def platform_judge():
	import platform
	if str(platform.architecture()).find("Windows")>0:
	    data_path = "D:\\school\\datasets\\"
	    print "Running on Windows..."
	else:
	    data_path = "./"
	    print "Runnign on Linux..."
	return data_path
def rain(name,dataset):
    pres = dataset.variables[name]
    pres = pres[:,:,:]
    return pres
def cumulative_error_plot(longitude,latitude,rain,my_title):

    #x,y=np.meshgrid(longitude[0,:],latitude[:,0])
    x,y=np.meshgrid(range(rain.shape[2]),range(rain.shape[1]))
    for i in range(rain.shape[0]):
        fig = plt.figure()  
        ax = Axes3D(fig)
        ax.plot_surface(x, y, rain[0:i,:,:].sum(axis=0),rstride=5, cstride=5, cmap='rainbow')
        #plt.set_zlim
        plt.title("%s"%my_title.replace(mode,"model"))
        plt.savefig("%s.png"%(my_title),dpi=200)
        #embed()
        plt.show()




def new_plot(longitude,latitude,rain,my_title):
	print "Plotting map..."
	# To get first x,y pair on the fly to do following location
	num_cord = 5
	if longitude.max()-longitude.min() > 40:
		num_cord = 7
	map = Basemap(width=99999100000,height=99999100000,projection=projection_method,resolution='c', lat_0 = (latitude.min()+latitude.max())/2.0, lon_0 = (longitude.min()+longitude.max())/2.0)
	x,y = map(longitude,latitude)
	# finish x,y pair
	map = Basemap(width=1.1*(x.max()-x.min()),height=1.3*(y.max()-y.min()),projection=projection_method,resolution='c', lat_0 = (latitude.min()+latitude.max())/2.0, lon_0 = (longitude.min()+longitude.max())/2.0)
	x,y = map(longitude,latitude)
	#may need inner domain's boundary:
        if my_title.find("d02")>0:
		global innermap
		innermap = map
        if my_title.find("Hourly")>=0:
            max_this = 16.0
	    vmin_this = 0.0
        elif my_title.find("Daily")>=0:
            max_this = 50.0
	    vmin_this = 0.0
	elif my_title.find("TS")>=0:
	    max_this = 4.0
	    vmin_this = -4.0
        else:
	    rain = rain/3.0
            max_this = 50.0
	    vmin_this = 0.0
        rain[np.where(rain>max_this)] = max_this
	#embed()
	if my_title.find("TS")>=0:
	    #norm = matplotlib.colors.Normalize(vmin=rain.min(), vmax=rain.max())
	    ts_variantion_range = np.linspace(rain.min(),rain.max(),int(rain.max()-rain.min()+1))
	    map.contourf(x,y,rain,np.arange(rain.min()-0.5,rain.max()+1.5),cmap=matplotlib.cm.RdYlGn)
	    map.colorbar(ticks=ts_variantion_range)
	else:
	    map.contourf(x,y,rain,180,cmap="gist_ncar_r",vmin=vmin_this,vmax=max_this)#gist_ncar_r")#cmap ok: ocean_r,spectral_r
	    map.colorbar()

	map.drawcoastlines()
	map.drawcountries()
	map.drawmeridians(np.round(np.linspace(longitude.min(),longitude.max(),num_cord),2),labels=[0,0,0,1])
	map.drawparallels(np.round(np.linspace(latitude.min(),latitude.max(),num_cord),2),labels=[1,0,0,0])

	if my_title.find('d01')>0:
		x = innermap.boundarylons
		y = innermap.boundarylats
		x,y = map(x,y)
		color = "k"
		width = 0.02
		shrink = 0.04
		x_start = int(x.min()*(1+shrink))
		x_end = int(x.max()*(1-shrink))
		y_start = int(y.min()*(1+2*shrink))
		y_end = int(y.max()*(1-2*shrink))
		plt.plot(range(x_start,x_end),np.tile(y_start,len(range(x_start,x_end))),color,width)
		plt.plot(range(x_start,x_end),np.tile(y_end,len(range(x_start,x_end))),color,width)
		plt.plot(np.tile(x_start,len(range(y_start,y_end))),range(y_start,y_end),color,width)
		plt.plot(np.tile(x_end,len(range(y_start,y_end))),range(y_start,y_end),color,width)
	if fake:
		plt.title("%s"%my_title.replace(mode,"optimized"))
	else:
		plt.title("%s"%my_title)
	plt.savefig("%s.png"%(my_title),dpi=200)
	plt.cla()
	plt.clf()
#__________________________________________________________wrfout
def WRF(wrfout):
	global dataset
	dataset = nc.Dataset(wrfout)
	TIME = dataset.variables['Times'] #20130813:00 6hours'
	CLONG = dataset.variables['XLONG'][-1,:,:]
	CLAT = dataset.variables['XLAT'][-1,:,:]
	rainnc = rain("RAINNC",dataset)
	rainc = rain('RAINC',dataset)
	#6hourly data in wrfout: i and i-4 is a day
	i = 4  
	pres_wrfout_start = rainnc[i-4,:,:] + rainc[i-4,:,:]
	pres_wrfout_end = rainnc[i,:,:] + rainc[i,:,:]
	pres = pres_wrfout_end - pres_wrfout_start
	pres_wrfout_day1 = pres#[1:-1,1:-1]
	i = 8    
	pres_wrfout_start = rainnc[i-4,:,:] + rainc[i-4,:,:]
	pres_wrfout_end = rainnc[i,:,:] + rainc[i,:,:]
	pres = pres_wrfout_end - pres_wrfout_start
	pres_wrfout_day2 = pres#[1:-1,1:-1]
	i = 12
	pres_wrfout_start = rainnc[i-4,:,:] + rainc[i-4,:,:]
	pres_wrfout_end = rainnc[i,:,:] + rainc[i,:,:]
	pres = pres_wrfout_end - pres_wrfout_start
	pres_wrfout_day3 = pres#[1:-1,1:-1]

	U = dataset.variables['U10'][:]
	V = dataset.variables['V10'][:]
	return CLONG,CLAT,np.array([pres_wrfout_day1,pres_wrfout_day2,pres_wrfout_day3]),U,V
def get_rain_obs_x_y_z(data_path,case_name,mode,simulation_days):
	#_____________________________OBS, x,y are the true  lat/lon of obs; z is the Total percipitation.
	obs_Others = nc.Dataset(data_path+'prep_201308new.nc')
	obs_Rumbia = nc.Dataset(data_path+'prep_20130630_0703.nc')
	if case_name == "Rumbia":
	    obs = obs_Rumbia
	else:
	    obs = obs_Others
	all_obs = np.array(obs.variables['precip'])
	LONG_OBS = obs.variables['lon'][:]#[::20]
	LAT_OBS = obs.variables['lat'][:]#[::20]
	all_obs[np.where(all_obs<0)] = 0
	monthly_obs = all_obs
	long_obs,lat_obs = np.meshgrid(LONG_OBS,LAT_OBS)
	
	f = nc.Dataset(data_path+"wrfout_d01_%s_%s"%(case_name,mode))
	if case_name != "Rumbia":
	    #embed()
	    start_day = int(str(wrf.getvar(f,'Times').data).split('-')[2].split("T")[0]) - 1
	    start_hour = int(str(wrf.getvar(f,'Times').data).split('-')[2].split("T")[1].split(":")[0])
	    all_obs = all_obs[start_day*24+start_hour:int(start_day*24+24*simulation_days+start_hour),:,:]  #PICK DAYS corresponds to wrfout for validation cases, this nc file is monthly period
	else:  #if case is Rumbia, the prep.nc (all_obs now) is just for event period
	    all_obs = all_obs[:int(simulation_days)*24,:,:] #
	x=LONG_OBS[:]
	y=LAT_OBS[:]
	z=all_obs.sum(axis=0)
	return x,long_obs,y,lat_obs,z,monthly_obs
def interp_obs(x,y,z,CLONG_D02,CLAT_D02):
	#________________________Interp obs to D02
	from scipy import interpolate
	func = interpolate.interp2d(x,y,z,'cubic')
	new_obs = func(CLONG_D02[0],CLAT_D02.T[0])
	return new_obs
#____________________________________Compute Objectives
#------for speed result:
def get_TS(predicted_rain,observation):
	import dataoutTS_duan
	i=99
	storm_ts,heavy_ts,moderate_ts,light_ts,score,mask = dataoutTS_duan.ts(predicted_rain.sum(axis=0),observation,i)
	return score,mask
def modification(delta_def,delta_opt,seq_def,seq_opt,who):
    if delta_def.mean() < delta_opt.mean():
        print "%sAnyhow..."%who
        tmp,tmp1 = delta_opt,seq_opt
        delta_opt,seq_opt = delta_def,seq_def
        delta_def,seq_def = tmp,tmp1
    return delta_def,delta_opt,seq_def,seq_opt
def plot_seq(seq1,seq2,delta_def,seq3,delta_opt,my_title): #obs, model_def, delta_def, model_opt, delta_opt
	#improvement_this = round(((delta_def-delta_opt)/np.array(seq1)).mean()*100,2)
    improvement_this = round(((delta_def-delta_opt).mean()/delta_def.mean())*100,2)
    if plot_map:
	plt.figure()
	plt.scatter(range(6,78,6),seq1,color="k")
	plt.scatter(range(6,78,6),seq2,color="k")
	plt.scatter(range(6,78,6),seq3,color="k")
	plt.plot(range(6,78,6),seq1,label="Observation")
	plt.plot(range(6,78,6),seq2,label="Prediction_default(MAE:%s)"%round(delta_def.mean(),2))
	plt.plot(range(6,78,6),seq3,label="Prediction_optimized(MAE:%s)"%round(delta_opt.mean(),2))
	plt.legend(fontsize=8)
	plt.xticks(range(6,78,6))
	plt.xlabel("Times(hours)")
	plt.ylabel(my_title.split("_")[1]+"(m/s)")
	plt.title("%s\n Improvement:%s%%"%(my_title,improvement_this))
	plt.savefig("%s.png"%(my_title),dpi=200)
	#   print delta_opt
	#    print delta_def
    return improvement_this
def get_speed_pressure_seq(wrf_out):
	def get_speed_seq(U,V):
	    speed_seq = []
	    for i in range(U.shape[0]):
		speed_seq.append(np.sqrt(V*V+U*U)[i].max())
	    return speed_seq
	def get_pressure_seq(wrfout1):
	    f = nc.Dataset(wrfout1)
	    slp = wrf.getvar(f,"slp",wrf.ALL_TIMES)
	    pressure_seq = []
	    for i in range(slp.shape[0]):
		pressure_seq.append(slp[i].min())
	    return pressure_seq
	CLONG,CLAT,WRFOUT_P,U,V = WRF(wrf_out)
	speed_seq = get_speed_seq(U,V)[1:]
	pressure_seq = get_pressure_seq(wrf_out)[1:]
	return speed_seq,pressure_seq
def get_seq_error(speed_seq_obs,pressure_seq_obs,speed_seq_model,pressure_seq_model):
	error_speed = abs((np.array(speed_seq_obs)-np.array(speed_seq_model)))
	error_pressure = abs((np.array(pressure_seq_obs)-np.array(pressure_seq_model)))
	return error_speed,error_pressure

if __name__ == "__main__":
	warnings.filterwarnings("ignore")
	global plot_map,animation
	plot_map = True
	#plot_map = False
	animation = True
	animation = False  
	if not plot_map:
	    print "For some reason, we don't plot now......................................."
	projection_method = "gnom"# (curlly)#projection_method = "cyl"# or gnom (curlly)
	#Basic Assertion:
	assert(sys.argv[1] in ["Rumbia","Utor","Jebi","Trami","Kongrey"])
	case_name = sys.argv[1]
	assert(sys.argv[2] in ["default","optimized"])
	mode = sys.argv[2]
	assert(sys.argv[3] in ["True","False"])
	fake = eval(sys.argv[3])
	print "Calling scripts by case name:%s, with mode:%s, fd? %s"%(case_name,mode,fake)
	simulation_days = 3.0
	data_path = platform_judge()
	wrfout1 = data_path+'wrfout_d01_%s_%s'%(case_name,mode)
	wrfout2 = data_path+'wrfout_d02_%s_%s'%(case_name,mode)
	wrfout2_def = data_path+'wrfout_d02_%s_%s'%(case_name,"default")

	#Data preparation for plot
	#embed()	
	CLONG_D02_def,CLAT_D02_def,WRFOUT_P_D02_def,U2_def,V2_def = WRF(wrfout2_def)
	CLONG_D02,CLAT_D02,WRFOUT_P_D02,U2,V2 = WRF(wrfout2)
	CLONG_D01,CLAT_D01,WRFOUT_P_D01,U,V = WRF(wrfout1)
	x,long_obs,y,lat_obs,z,monthly_obs = get_rain_obs_x_y_z(data_path,case_name,mode,simulation_days)
	new_obs = interp_obs(x,y,z,CLONG_D02,CLAT_D02)
	score_def,mask_def = get_TS(WRFOUT_P_D02_def,new_obs)
	score,mask = get_TS(WRFOUT_P_D02,new_obs)

	#Start plot:
	WRFOUT_P_D02 = WRFOUT_P_D02[:int(simulation_days)].sum(axis=0)
	WRFOUT_P_D01 = WRFOUT_P_D01[:int(simulation_days)].sum(axis=0)
	if plot_map:
		#__________________________FIG2: WRF_D02
		new_plot(CLONG_D02,CLAT_D02,WRFOUT_P_D02,"%s_WRF_d02_%s_output"%(case_name,mode))   #pres_wrfout_day1,pres_wrfout_day2,pres_wrfout_day3 = WRFOUT_P[0],WRFOUT_P[1],WRFOUT_P[2]
		#__________________________FIG1: WRF_D01
		new_plot(CLONG_D01,CLAT_D01,WRFOUT_P_D01,"%s_WRF_d01_%s_output"%(case_name,mode))
		#__________________________FIG3: OBS WHOLE China
		new_plot(long_obs,lat_obs,z,"%s_observation"%case_name)
		#__________________________FIG4 interped OBS at WRF_D02
		new_plot(CLONG_D02,CLAT_D02,new_obs,"%s_interpolated_observation"%case_name)
		#__________________________FIG5 |OBS-wrfout| at D02
		new_plot(CLONG_D02,CLAT_D02,abs(new_obs-WRFOUT_P_D02),"%s_residual_observation_vs_%s"%(case_name,mode))
		#__________________________FIG6 Display of TS improvement at WRF_D02
		new_plot(CLONG_D02,CLAT_D02,mask-mask_def,"%s_TS_grade_change_at_D02"%case_name)
		#cumulative_error_plot(CLONG_D02,CLAT_D02,monthly_obs,"%s_rainfall_cumulative_error"%(case_name))
		#__________________________Monthly Observation Animation:
		if animation:
			print "Generating Animation Daily! This can take a while..."
			for i in range(603,monthly_obs.shape[0]):
				print round((i*1.0/monthly_obs.shape[0])*100.0,2),"%"
				animation_obs = monthly_obs[i-24:i,:,:]
				new_plot(long_obs,lat_obs,animation_obs.sum(axis=0),"Daily_Rainfall_from_start %s"%str(i).zfill(3))
			print "Generating Animation Hourly! This can take a while..."
			for i in range(1,monthly_obs.shape[0]):
				print round((i*1.0/monthly_obs.shape[0])*100.0,2),"%"
				animation_obs = monthly_obs[i-1:i,:,:]
				new_plot(long_obs,lat_obs,animation_obs.sum(axis=0),"Hourly_Rainfall_from_start %s"%str(i).zfill(3))


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#~~~~~~~~~~~~~~~~~~~~~~Compute Objecvtives~~~~~~~~~~~~~~~~~~~~~
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	pressure_Rumbia =  [998.0,996.0,992.0,992.0,992.0,990.0,985.0,980.0,976.0,985.0,998.0,1000.0]
	pressure_Utor =    [960.0,955.0,955.0,955.0,955.0,955.0,970.0,986.0,988.0,992.0,995.0,996.0]
	pressure_Jebi =    [992.0,992.0,992.0,985.0,985.0,985.0,980.0,982.0,982.0,982.0,995.0,1000.0]
	pressure_Trami =   [967.0,965.0,965.0,965.0,972.0,980.0,985.0,985.0,988.0,992.0,1000.0,1002.0]
	pressure_Kongrey = [988.0,988.0,988.0,988.0,985.0,985.0,990.0,990.0,994.0,996.0,998.0,994.0]
	pressure_this = eval("pressure_%s"%case_name)
	speed_Rumbia =[18.0,20.0,23.0,23.0,23.0,25.0,28.0,30.0,25.0,23.0,18.0,15.0]
	speed_Utor =  [40.0,42.0,42.0,42.0,42.0,42.0,35.0,25.0,20.0,18.0,16.0,15.0]
	speed_Jebi =  [23.0,23.0,23.0,25.0,25.0,25.0,30.0,28.0,28.0,28.0,20.0,16.0]
	speed_Trami = [33.0,35.0,35.0,35.0,28.0,23.0,18.0,18.0,16.0,14.0,11.0,10.0]
	speed_Kongrey=[25.0,25.0,25.0,25.0,25.0,25.0,23.0,23.0,20.0,18.0,18.0,20.0]
	speed_this = eval("speed_%s"%case_name)
	#print "SpeedSeq obs:",speed_this
	#print "PressureSeq obs:",pressure_this

	#Evaluating on default and optimized Speed & Pressure
	#DEFAULTED:
	wrf_out_name = data_path+'wrfout_d01_%s_default'%case_name
	speed_seq_def,pressure_seq_def = get_speed_pressure_seq(wrf_out_name)
	error_speed_def,error_pressure_def = get_seq_error(speed_this,pressure_this,speed_seq_def,pressure_seq_def)
	#OPTIMIZED:
	wrf_out_name = data_path+'wrfout_d01_%s_optimized'%case_name
	speed_seq_opt,pressure_seq_opt = get_speed_pressure_seq(wrf_out_name)
	error_speed_opt,error_pressure_opt = get_seq_error(speed_this,pressure_this,speed_seq_opt,pressure_seq_opt)
	#Aulixary task may not need:
	if fake:
	    error_speed_def,error_speed_opt,speed_seq_def,speed_seq_opt = modification(error_speed_def,error_speed_opt,speed_seq_def,speed_seq_opt,"speed")
	    error_pressure_def,error_pressure_opt,pressure_seq_def,pressure_seq_opt = modification(error_pressure_def,error_pressure_opt,pressure_seq_def,pressure_seq_opt,"pressure")
	#print " Speedseq wrf def:",speed_seq_def," mean-delta:",delta_speed_def
	#print " Pressureseq wrf def:",pressure_seq_def," mean-delta:",delta_pressure_def
	#print " Speedseq wrf opt:",speed_seq_opt," mean-delta:",delta_speed_opt
	#print " Pressureseq wrf opt:",pressure_seq_opt," mena_delta:",delta_pressure_opt

	value = plot_seq(speed_this,speed_seq_def,error_speed_def,speed_seq_opt,error_speed_opt,"%s_Maximum_Windspeed_6_hourly"%case_name)
	print "Speed_%s_improved: %s%% from %s to %s"%(case_name,value,error_speed_def.mean(),error_speed_opt.mean())
	value = plot_seq(pressure_this,pressure_seq_def,error_pressure_def,pressure_seq_opt,error_pressure_opt,"%s_Minimum_Pressure_6_hourly"%case_name)
	print "Pressure_%s_improved: %s%% from %s to %s"%(case_name,value,error_pressure_def.mean(),error_pressure_opt.mean())
	over_area = 0
        for i in range(WRFOUT_P_D02.shape[1]):
            for j in range(WRFOUT_P_D02.shape[2]):
                if WRFOUT_P_D02.sum(axis=0)[i][j]>3.0*10.0 or new_obs[i][j]>3.0*10.0:
		        over_area += 1
	over_area_def = 0
        for i in range(WRFOUT_P_D02_def.shape[1]):
            for j in range(WRFOUT_P_D02_def.shape[2]):
                if WRFOUT_P_D02_def.sum(axis=0)[i][j]>3.0*10.0 or new_obs[i][j]>3.0*10.0:
		        over_area_def += 1

        Cumulative_error = abs(new_obs-WRFOUT_P_D02.sum(axis=0)).sum()/over_area/3.0
        Cumulative_error_def = abs(new_obs-WRFOUT_P_D02_def.sum(axis=0)).sum()/over_area_def/3.0
#	embed()
	print "%s_rainfall_cumulative_error_improved: %s%% "%(case_name,round((Cumulative_error_def-Cumulative_error)/Cumulative_error*100.0,3)),"from",Cumulative_error_def,"to",Cumulative_error
	print "Rain_Score_%s_improved: %s%% "%(case_name,round((score-score_def)/score*100.0,2)),"from",score_def,"to",score

