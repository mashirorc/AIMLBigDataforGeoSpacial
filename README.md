# VoTT WSU Team
## GeoTIFF Conversion Python Application

### Dependencies
 - Python 3.7
 - TensorFlow 1.13.1
 - Keras 2.0.8
 - GDAL (pip install GDAL-3.2.2-cp37-cp37m-win_amd64.whl)
 - mask-rcnn (python setup.py install)
 - Tkinter (comes standard in Python 3.X)
 - GDAL:
	 - Ubuntu:
		> sudo apt-get install gdal-bin
		> sudo apt-get install libgdal-dev
  - 
		
- Sci-kit Image:
>pip3 install scikit-image

- matplotlib:
>pip3 install matplotlib 

- numpy
- json
- glob
- cv2

<br/><br/>

### Instructions

User needs to install Tensorflow and Keras as above, so python3.7 is needed
GDAL needs to be installed as above, a whl file is included if needed in the git repo
mask-rcnn needs to be installed as above, setup.py is in the git repo 

Have matching folders with VoTT. Connection == Source Connection, Project == Target Connection
Select Import Tags
Select row in the text box of the tags to train on then press Train Model
Predict Image is now chosen of an image that has a JSON file in the Connection folder
Export Tags to VoTT after Predict Image will replace that JSON file

Already, we knew that we had to have a way to import these GeoTIFF 
images into our application and into VoTT. This is presently done both via an "Import" and an "Open" button within the Python application.
As I have described earlier though, GeoTIFFs are not an accepted file type for VoTT, so we needed to come up with a work around. The
implementation that we decided to go with for making sure that VoTT can load GeoTIFF
images was to convert these images into PNGs. Once the image has been successfully imported into our Python application, our application needs to be able to 
successfully save a GeoTIFF as a PNG so that it can be imported into VoTT to be tagged.
Once the image is tagged and the tagged information is saved locally, the Python application should be able to render these tags over the displayed GeoTIFF image in the
application's canvas.

## VoTT application w/ Zoom/Pan

### Dependencies
	- VoTT requires NodeJS (>= 10.x, Dubnium) and NPM
	- CanvasTools-for-VoTT (>= 2.2.25)

### Instructions
	- git clone https://github.com/diwashbiswa/VoTT.git
	- cd VoTT
	- git checkout diwashbiswa/ct-zoom
	- npm ci
	- npm start

- The above instruction should open both electron and web version of VoTT
- Create a sample project on the electron version
- Then you'll be able to use the zoom in/out by clicking the search-plus and search-minus buttons located at the toolbar at the top
- You can also use mouse wheel or scrollbar to pan on the images
