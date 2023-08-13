if [[ ! -f "bin/activate" ]]; then
	python3 -m venv .
fi 
. bin/activate
pip install pyyaml &&
python3 auto-sync.py $@
