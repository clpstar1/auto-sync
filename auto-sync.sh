if [[ ! -f "bin/activate" ]]; then
	python3 -m venv .
fi 
. bin/activate
python3 auto-sync.py $@
