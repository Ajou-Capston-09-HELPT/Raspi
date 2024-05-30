import threading 
import time
import camera
import network

def main():
	try:
		t1 = threading.Thread(target=camera.main)
		t1.start()
		t2 = threading.Thread(target=network.main)
		t2.start()
  
		while True:
			time.sleep(0.1)
	
	except KeyboardInterrupt:
		global flag_exit
		flag_exit = True
		join(t1, t2)
		network.close()

def join(t1, t2):
    t1.join()
    t2.join()	

 
if __name__ == "__main__":
	main()
