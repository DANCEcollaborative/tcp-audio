### To create a conda env
Use `$ bash setup.sh` to create an env or use the following code
```
conda create --name voice_client python=3.8

conda activate voice_client
conda install numpy pyzmq
pip install sounddevice 
```

### To run the application
Use `$ bash run.sh` or use the following code
```
conda activate voice_client
python client.py
```