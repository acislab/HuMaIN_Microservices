import requests
import time, argparse, os
import multiprocessing as mp


IP = "10.5.146.92"#"10.5.146.92"
PORT = "30001"

LICHENS = "/home/jingchao/HuMaIN/label-data-master/lichens/gold/inputs" 

def call_bin(job):
	imagepath, dstDir, parameters = job
	url_bin = "http://" + IP + ":" + PORT + "/binarizationapi"

	# Uploaded iamges
	image = {'image': open(imagepath, 'rb')}

	# Call binarization service
	resp = requests.get(url_bin, files=image, data=parameters, stream=True)

	# Save the responsed binarized image
	image = os.path.basename(imagepath)
	image_name, image_ext = os.path.splitext(image)
	dstimage = image_name + "_bin.png"
	dstpath = os.path.join(dstDir, dstimage)

	if resp.status_code == 200:
		with open(dstpath, 'wb') as fd:
			for chunk in resp:
				fd.write(chunk)
	else:
		print("Image %s Binarization error!" % imagepath)
        return

if __name__ == '__main__':
	paras = {}
	jobs = []
	for img in os.listdir(LICHENS):
		img_path = os.path.join(LICHENS, img)
		jobs.append((img_path, LICHENS, paras))
	pool = mp.Pool() # #processes = #CPU by default
	pool.map(call_bin, jobs)
	# Close processes pool after it is finished
	pool.close()
	pool.join()