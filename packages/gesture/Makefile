../gesture.zip: gestensensor.py main.py manifest sensor.png
	zip -u -r $@ $^ 

clean:
	rm -f ../gesture.zip

install:
	rsync -av *.py txt4:apps/53167040-fd44-468e-aedc-5fb862315340


