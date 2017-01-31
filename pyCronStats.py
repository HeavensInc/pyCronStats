import recurringStats as RS
import schedule
import time

#def job():
#    print("I'm working...")

joblist = [
	[ "temp",   RS.eJobType.fileRead, "/sys/devices/platform/sunxi-i2c.0/i2c-0/0-0034/temp1_input", "CPU Temperature in MilliCelsius" ],
	[ "google", RS.eJobType.pingHost, "8.8.8.8", "Ping to Google" ],
	[ "router", RS.eJobType.pingHost, "192.168.0.1", "Ping to Router" ],
	[ "wifiAP", RS.eJobType.pingHost, "192.168.188.1", "Ping to WifiAP" ],
	]
	
jobclasslist = []

for job in joblist:
	jobclass = RS.cRecurringStats("pyStat", job[0], 20, 24*12)
	if job[1] == RS.eJobType.fileRead:
		jobclass.setupAsFileRead( job[2], job[3], [20e3,50e3])
	elif job[1] == RS.eJobType.pingHost:
		jobclass.setupAsPingHost( job[2], job[3])

	schedule.every().minutes.do(jobclass.executeGathering)
	schedule.every(15).minutes.do(jobclass.executeDrawing)

	jobclasslist.append(jobclass)


while 1:
    schedule.run_pending()
    time.sleep(1)
