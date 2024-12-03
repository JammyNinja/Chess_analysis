#TESTS + hello world
hello_world:
	@echo "Welcome to the makefile"

test_env:
	@echo "front end port:" $(FRONT_END_PORT)

#DATA related commands
get_data:
	python scripts/data.py

preproc:
	python scripts/preprocessing.py

get_and_prep:
	python scripts/data.py
	python scripts/preprocessing.py

clear_all_data:
# are you sure?!
	rm data/*.csv

#DOCKER
docker_build_test_image:
	docker build -t chess:test $(DOCKER_PATH)

docker_run_test_image:
# laptop port : container port
	@echo "Test: http://localhost:$(BACK_END_PORT)/user_stats?username=JammyNinja"
	docker run -it --env-file .env -p $(BACK_END_PORT):$(PORT) chess:test

stop_running_containers:
	docker ps -a -q | xargs -r docker stop | xargs -r docker rm

#RUN LOCAL (NO DOCKER)
run_app:
	streamlit run public/front/app.py

run_api:
	uvicorn public.back.api.root:app --port $(BACK_END_PORT)
