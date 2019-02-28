## About
A completely impractical web app that makes colorful GIFs made as a fun foray into very basic image processing.

To get GIF, first run the app locally:

```
pip install -r requirements.txt
python colorgif.py
```

Once the server is running, navigate to `localhost:8888` and you will be presented with a set of options for generating your GIF. You can customize things like:
* dimensions
* blockiness (in other words, how big each block of color is)
* mood (color scheme)
* frames (how many unique images make up the GIF)

Once you hit submit, the app will generate the GIF based on the parameters you provided and will show it in your browser window. Tada!
