plotter.zip: main.py plotter.py move_sync.py plt_reader.py upload.py index.html print.html icon.png manifest data/*.hpgl data/*.plt thirdparty
	zip -u -r $@ $^ 

clean:
	rm -f plotter.zip

install:
	git submodule init
	git submodule update
	rsync -av *.py *.html data thirdparty txt3:apps/155710e1-be0b-4eaf-a1ed-6f50bf199a68

