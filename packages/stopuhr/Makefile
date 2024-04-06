stopuhr.zip: main.py ft_timing.py icon.png manifest
	rm -f $@
	zip $@ $^ 

test:
	PYTHONPATH=../../ftrobopy FT_TXT=txt1 ./ft_timing.py

uitest:
	FT_TXT=txt1 PYTHONPATH=../../ftcommunity-TXT/board/fischertechnik/TXT/rootfs/opt/ftc:../../ftrobopy python3 main.py 
