GARMIN=/Volumes/GARMIN/Garmin

VERSION=0.2.0

clean:
	rm -f dist/squadrats2garmin-*.tar.gz
	rm -f dist/squadrats2garmin-*-py3-none-any.whl
	rm -f docker/squadrats2garmin-*.tar.gz
	rm -f docker/squadrats2garmin-*-py3-none-any.whl
	rm -rf output/*

package:
	uv build
	cp dist/squadrats2garmin-$(VERSION)-py3-none-any.whl docker

docker: package
	docker build \
		--build-arg MKGMAP_VERSION=r4923 \
		--build-arg SQUADRATS2GARMIN_VERSION=0.2.0 \
		--tag kbrazulewicz/squadrats2garmin \
		docker

docker-run:
	docker run -it \
		--env SQUADRATS2GARMIN_VERBOSE=true \
		--mount type=bind,source=.,target=/output \
		kbrazulewicz/squadrats2garmin


test:
	uv run pytest -v

test1:
	uv run pytest -v tests/test_poly.py


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

visited-kml: clean
	uv run visited --verbose --kml-file squadrats.kml --output-file output/squadrats-visited.img

visited-user-id: clean
	uv run visited --verbose --user-id P2NkzJ2UfnOGnq7DNaA1Y1JZYkl1 --output-file output/squadrats-visited.img

visited: visited-user-id
	mv output/gmapsupp.img output/squadrats-visited.img
	#scp output/squadrats-visited.img home:/home/krystian/work/squadrats2garmin/output/
	cp output/squadrats-visited.img $(GARMIN)

mkgmap:
	mkgmap --read-config=output/mkgmap.cfg
	mv output/gmapsupp.img output/squadrats-visited.img
	#scp output/squadrats-visited.img home:/home/krystian/work/squadrats2garmin/output/
	cp output/squadrats-visited.img $(GARMIN)
