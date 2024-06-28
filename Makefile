hello_world:
	@echo "Welcome to the makefile"

get_data:
	python src/data.py

preproc:
	python src/preprocessing.py

get_and_prep:
	python src/data.py
	python src/preprocessing.py

clear_all_data:
# are you sure?!
	rm data/*.csv

#create a .env for someone?
