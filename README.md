## Tensorflow Garbage Classifier

This is my attempt at writing a garbage classifier (images of garbage) with the techniques from Andrew Ng's courses, using Tensorflow.

I'm also setting up Blender to generate my data because there doesn't seem to exist a large dataset of labelled images of garbage.

#### Setup

Virtualenv:
```
virtualenv venv
source /venv/bin/activate
```

Dependencies:
```
pip install matplotlib
pip install Pillow
```

CPU-only dependencies:
```
pip install tensorflow
```

For GPU, installation instructions are [here](https://www.tensorflow.org/install/install_linux) and [here](https://www.nvidia.com/en-us/data-center/gpu-accelerated-applications/tensorflow/).
Note that for cuDNN, its a `.dpkg` file instead of a tarball.


Get CIFAR-10 Dataset [here](https://www.cs.toronto.edu/~kriz/cifar.html).


#### Reference
[Pillow Docs](http://pillow.readthedocs.io/en/3.4.x/reference/Image.html)

#### Blender

I'm trying to use Blender to generate new training data. I'm using `.predef` files for editing Blender scripts in an external editor, as described [here](http://jameskersey.com/2013/09/11/python_editing_for_blender_part_one).

You need to load every script referenced through `import` from within Blender by opening the file in the Blender script editor. There's a [workaround for this](http://web.purplefrog.com/~thoth/blender/python-cookbook/import-python.html) which I'll eventually implement.