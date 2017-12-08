#Import defs from plot_basemap.py then compute objective function.
from plot_basemap import WRF
from plot_basemap import get_TS
from plot_basemap import platform_judge
from plot_basemap import get_speed_pressure_seq
from plot_basemap import get_seq_error
from plot_basemap import get_rain_obs_x_y_z
from plot_basemap import interp_obs

def TS_wrapper(data_path,case_name,inner_domain):
	x,long_obs,y,lat_obs,z,monthly_obs = get_rain_obs_x_y_z(data_path,case_name,"default",3)
	CLONG_D02,CLAT_D02,WRFOUT_P_D02,U2,V2 = WRF(inner_domain)
	new_obs = interp_obs(x,y,z,CLONG_D02,CLAT_D02)
	score = get_TS(WRFOUT_P_D02,new_obs)
	return score
def Speed_Pressure_wrapper(wrfout,speed_obs,pressure_obs):
	speed_seq,pressure_seq = get_speed_pressure_seq(wrfout)
	error_speed,error_pressure = get_seq_error(speed_obs,pressure_obs,speed_seq,pressure_seq)
	return error_speed,error_pressure

if __name__ == "__main__":
	print "Computing Objectives according to compute_objective.py...."
	case_name = "Rumbia"
#	case_name = "Kongrey"
	mode = "default"
#	mode = "optimized"
	pressure_Rumbia =  [998.0,996.0,992.0,992.0,992.0,990.0,985.0,980.0,976.0,985.0,998.0,1000.0]
	speed_Rumbia =[18.0,20.0,23.0,23.0,23.0,25.0,28.0,30.0,25.0,23.0,18.0,15.0]
	data_path = platform_judge()
	wrfout1 = data_path+'wrfout_d01_%s_%s'%(case_name,mode)
	wrfout2 = data_path+'wrfout_d02_%s_%s'%(case_name,mode)#Just read x,y for interpolation.


	print "Results----------------------"
	score = TS_wrapper(data_path,case_name,wrfout2)
	print "TS score:",score
	error_speed,error_pressure = Speed_Pressure_wrapper(wrfout1,speed_Rumbia,pressure_Rumbia)
	print "Pressure Error:",error_speed.mean()
	print "Speed Error:",error_pressure.mean()