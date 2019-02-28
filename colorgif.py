import time
import os
import enum
import numpy
import imageio
from flask import (
    Flask, send_file, request, render_template,
    flash, redirect, url_for
)
from PIL import Image


class Mood(enum.Enum):
    BLUE = 'blue'
    RED = 'red'
    GREEN = 'green'
    GRAY = 'gray'
    RAINBOW = 'rainbow'


GIF_DIR = '/tmp/gifs'

DEFAULT_IMG_SIZE = (800, 800)
MAX_DIMS = (1000, 1000)

# number of pixels that are chunked into a single color group
PIXEL_GROUP_SIZE = 10000

NUM_GIF_FRAMES = 10
MAX_FRAMES = 100


app = Flask(__name__)
app.secret_key = 'this_is_just_for_flashing_messages'


@app.route('/')
def index():
    kwargs = {
        'moods': Mood,
        'pixel_size': PIXEL_GROUP_SIZE,
        'width': DEFAULT_IMG_SIZE[0],
        'height': DEFAULT_IMG_SIZE[1],
        'frames': NUM_GIF_FRAMES
    }
    return render_template('index.html', **kwargs)


@app.route('/gifme')
def make_gif():

    errors = []
    kwargs = {}

    if 'mood' in request.args:
        try:
            mood = Mood(request.args['mood'])
        except:
            errors.append('Invalid mood.')
        else:
            kwargs['mood'] = mood

    if 'width' in request.args or 'height' in request.args: 

        width, height = request.args.get('width'), request.args.get('height')

        if height is None or width is None:
            errors.append('Both width and height must be specified.')
        else:
            width, height = as_int(width), as_int(height)
            if height is None or width is None:
                errors.append('Width and height must be integers.')
            else:
                if width > MAX_DIMS[0] or height > MAX_DIMS[1]:
                    msg = 'Max width and height values are {}.'.format(MAX_DIMS)
                    errors.append(msg)
                else:
                    kwargs['size'] = width, height

    if 'pixel_size' in request.args:
        pixel_size = as_int(request.args['pixel_size'])
        if pixel_size is None:
            errors.append('Pixel size must be an integer.')
        else:
            size = kwargs.get('size', DEFAULT_IMG_SIZE)
            area = size[0] * size[1]
            if pixel_size > area:
                errors.append('Pixel size exceeds total size of image.')
            else:
                kwargs['pixel_group_size'] = pixel_size
    else:
        if 'size' in kwargs:
            area = size[0] * size[1]
            kwargs['pixel_group_size'] = min(PIXEL_GROUP_SIZE, area)

    if 'frames' in request.args:
        gif_frames = as_int(request.args['frames'])
        if gif_frames is None:
            errors.append('Frames must be an integer.')
        else:
            if gif_frames > MAX_FRAMES:
                errors.append('Max number of frames is {}.'.format(MAX_FRAMES))
    else:
        gif_frames = NUM_GIF_FRAMES

    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('index'))

    frames = (make_image(**kwargs) for i in range(gif_frames))

    now = int(time.time())
    gif = os.path.join(GIF_DIR, '{}.gif'.format(now))
    imageio.mimsave(gif, frames)

    return send_file(gif, mimetype='img.gif')


def as_int(value):
    try:
        return int(value)
    except:
        return None
    

def make_image(size=DEFAULT_IMG_SIZE, pixel_group_size=PIXEL_GROUP_SIZE,
               mood=None):
    """
    Args:
        size:               tuple of (width, height) int
        pixel_group_size:   number of pixels to chunk together into single
                            color blocks
        mood:               choice from Moods enum
    """

    init_size = (size[0] * size[1]) / float(pixel_group_size)
    init_dims = int(init_size ** 0.5)

    rgb = numpy.random.randint(0, 256, (init_dims, init_dims, 3)).astype('uint8')

    if mood == Mood.BLUE:
        rgb[:, :, 0] = 0
        rgb[:, :, 1] = 0
    elif mood == Mood.RED:
        rgb[:, :, 1] = 0
        rgb[:, :, 2] = 0
    elif mood == Mood.GREEN:
        rgb[:, :, 0] = 0
        rgb[:, :, 2] = 0
    elif mood == Mood.GRAY:
        rgb[:, :, 1] = rgb[:, :, 0]
        rgb[:, :, 2] = rgb[:, :, 0]

    image = Image.fromarray(rgb)
    return image.resize(size)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=8888, type=int)
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--gif-dir', help='Directory where gifs will be saved.')

    args = parser.parse_args()

    if not args.gif_dir is None:
        GIF_DIR = args.gif_dir

    if not os.path.isdir(GIF_DIR):
        raise Exception('Directory {} does not exist.'.format(GIF_DIR))

    app.run(host=args.host, port=args.port, debug=args.debug)
