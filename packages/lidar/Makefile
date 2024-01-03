../lidar.zip: VL53L0X.py main.py manifest sensor.png
	zip -u -r $@ $^ 

clean:
	rm -f ../lidar.zip

install:
	rsync -av *.py txt4:apps/bdf10bb8-5d97-41a0-a887-213d6d4c053c


