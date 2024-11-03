../navigator.zip: main.py detector.py aruco.png manifest calibration.json calibration.py
	zip -u -r $@ $^ 

clean:
	rm -f ../navigator.zip

install:
	rsync -av *.py *.json ftc@txt2:apps/1a598566-8137-4993-854d-3e294a8e6a60



