hello_world:
	@echo "Welcome to the makefile"

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

#create a .env for someone?
