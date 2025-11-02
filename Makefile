GARMIN=/Volumes/GARMIN/Garmin


run:
	python3 squadrats2osm.py ../config/squadrats2osm.json

grid-pl:
	python3 squadrats2garmin.py --config-files config/PL-Polska.json
	cp dist/europe/squadrats-PL-poland.img
	ls -l dist/europe/*-PL-*.img $(GARMIN)

test:
	python3 -m unittest -v

test1:
	python3 -m unittest tests.test_poly.TestPoly.test_generate_tiles_for_a_row1

kml:
	rm -rf output/*
	python3 kmlread.py --verbose --input-file squadrats-2025-10-24.kml --output-file output/squadrats-visited.img
	mv output/gmapsupp.img output/squadrats-visited.img
	scp output/squadrats-visited.img home:/home/krystian/work/squadrats2garmin/output/
	cp output/squadrats-visited.img /Volumes/GARMIN/Garmin

mkgmap:
	mkgmap --read-config=output/mkgmap.cfg
	mv output/gmapsupp.img output/squadrats-visited.img
	scp output/squadrats-visited.img home:/home/krystian/work/squadrats2garmin/output/
	cp output/squadrats-visited.img $(GARMIN)