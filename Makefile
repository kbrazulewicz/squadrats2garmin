run:
	python3 squadrats2osm.py ../config/squadrats2osm.json

test:
	python3 -m unittest -v

test1:
	python3 -m unittest tests.test_poly.TestPoly.test_generate_tiles_for_a_row1

kml:
	rm -rf output/*
	python3 kmlread.py
	mv output/gmapsupp.img output/squadrats-visited.img
	scp output/squadrats-visited.img home:/home/krystian/work/squadrats2garmin/output/
	cp output/squadrats-visited.img /Volumes/GARMIN/Garmin