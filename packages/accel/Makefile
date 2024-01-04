../accel.zip: ADXL345.py main.py manifest sensor.png
	zip -u -r $@ $^ 

clean:
	rm -f ../accel.zip

install:
	rsync -av *.py txt4:apps/a0000c76-e58e-4be8-8435-0074a13992f1



