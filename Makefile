GARMIN=/Volumes/GARMIN/Garmin


run:
	python3 squadrats2osm.py ../config/squadrats2osm.json

grid-pl:
	uv run squadrats2garmin.py --verbose --config-files config/PL-Polska.json
	ls -l dist/europe/*-PL-*.img
	cp dist/europe/*-PL-*.img $(GARMIN)

grid-es: clean
	uv run squadrats2garmin.py --verbose --config-files config/ES-España.json
	ls -l dist/europe/*-ES-*.img
#	cp dist/europe/*-PL-*.img $(GARMIN)

test:
	python3 -m unittest -v

test1:
	python3 -m unittest tests.test_poly.TestPoly.test_generate_tiles_for_a_row1


clean:
	rm -rf output/*

visited-kml: clean
	uv run visited-squadrats.py --verbose --kml-file squadrats.kml --output-file output/squadrats-visited.img

visited-user-id: clean
	uv run visited-squadrats.py --verbose --user-id P2NkzJ2UfnOGnq7DNaA1Y1JZYkl1 --output-file output/squadrats-visited.img

visited: visited-user-id
	mv output/gmapsupp.img output/squadrats-visited.img
	#scp output/squadrats-visited.img home:/home/krystian/work/squadrats2garmin/output/
	cp output/squadrats-visited.img $(GARMIN)

mkgmap:
	mkgmap --read-config=output/mkgmap.cfg
	mv output/gmapsupp.img output/squadrats-visited.img
	#scp output/squadrats-visited.img home:/home/krystian/work/squadrats2garmin/output/
	cp output/squadrats-visited.img $(GARMIN)
