GARMIN=/Volumes/GARMIN/Garmin


run:
	python3 squadrats2osm.py ../config/squadrats2osm.json

grid-pl:
	python3 squadrats2garmin.py --verbose --config-files config/PL-Polska.json
	ls -l dist/europe/*-PL-*.img
	cp dist/europe/*-PL-*.img $(GARMIN)

test:
	python3 -m unittest -v

test1:
	python3 -m unittest tests.test_poly.TestPoly.test_generate_tiles_for_a_row1


clean:
	rm -rf output/*

kml-to-osm: clean
	python3 visited-squadrats.py --verbose --input-file squadrats.kml --output-file output/squadrats-visited.img

kml: kml-to-osm
	mv output/gmapsupp.img output/squadrats-visited.img
	scp output/squadrats-visited.img home:/home/krystian/work/squadrats2garmin/output/
	cp output/squadrats-visited.img $(GARMIN)

mkgmap:
	mkgmap --read-config=output/mkgmap.cfg
	mv output/gmapsupp.img output/squadrats-visited.img
	scp output/squadrats-visited.img home:/home/krystian/work/squadrats2garmin/output/
	cp output/squadrats-visited.img $(GARMIN)