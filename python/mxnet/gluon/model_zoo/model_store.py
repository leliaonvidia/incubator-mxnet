# coding: utf-8
"""Model zoo for pre-trained models."""
from __future__ import print_function
__all__ = ['get_model_file', 'purge']
import hashlib
import os
import zipfile

from ...test_utils import download

_model_sha1 = {name: checksum for checksum, name in [
    ('44335d1f0046b328243b32a26a4fbd62d9057b45', 'alexnet'),
    ('f27dbf2dbd5ce9a80b102d89c7483342cd33cb31', 'densenet121'),
    ('b6c8a95717e3e761bd88d145f4d0a214aaa515dc', 'densenet161'),
    ('2603f878403c6aa5a71a124c4a3307143d6820e9', 'densenet169'),
    ('1cdbc116bc3a1b65832b18cf53e1cb8e7da017eb', 'densenet201'),
    ('ed47ec45a937b656fcc94dabde85495bbef5ba1f', 'inceptionv3'),
    ('d2b128fa89477c2e20061607a53a8d9f66ce239d', 'resnet101_v1'),
    ('6562166cd597a6328a32a0ce47bb651df80b3bbb', 'resnet152_v1'),
    ('38d6d423c22828718ec3397924b8e116a03e6ac0', 'resnet18_v1'),
    ('4dc2c2390a7c7990e0ca1e53aeebb1d1a08592d1', 'resnet34_v1'),
    ('2a903ab21260c85673a78fe65037819a843a1f43', 'resnet50_v1'),
    ('264ba4970a0cc87a4f15c96e25246a1307caf523', 'squeezenet1.0'),
    ('33ba0f93753c83d86e1eb397f38a667eaf2e9376', 'squeezenet1.1'),
    ('dd221b160977f36a53f464cb54648d227c707a05', 'vgg11'),
    ('ee79a8098a91fbe05b7a973fed2017a6117723a8', 'vgg11_bn'),
    ('6bc5de58a05a5e2e7f493e2d75a580d83efde38c', 'vgg13'),
    ('7d97a06c3c7a1aecc88b6e7385c2b373a249e95e', 'vgg13_bn'),
    ('649467530119c0f78c4859999e264e7bf14471a9', 'vgg16'),
    ('6b9dbe6194e5bfed30fd7a7c9a71f7e5a276cb14', 'vgg16_bn'),
    ('f713436691eee9a20d70a145ce0d53ed24bf7399', 'vgg19'),
    ('9730961c9cea43fd7eeefb00d792e386c45847d6', 'vgg19_bn')]}

_url_format = 'https://{bucket}.s3.amazonaws.com/gluon/models/{file_name}.zip'
bucket = 'apache-mxnet'

def short_hash(name):
    if name not in _model_sha1:
        raise ValueError('Pretrained model for {name} is not available.'.format(name=name))
    return _model_sha1[name][:8]

def verified(file_path, name):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(1048576)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest() == _model_sha1[name]

def get_model_file(name, local_dir=os.path.expanduser('~/.mxnet/models/')):
    r"""Return location for the pretrained on local file system.

    This function will download from online model zoo when model cannot be found or has mismatch.

    Parameters
    ----------
    name : str
        Name of the model.
    local_dir : str, default '~/.mxnet/models'
        Location for keeping the model parameters.

    Returns
    -------
    file_path
        Path to the requested pretrained model file.
    """
    file_name = '{name}-{short_hash}'.format(name=name,
                                             short_hash=short_hash(name))
    file_path = os.path.join(local_dir, file_name+'.params')
    if os.path.exists(file_path):
        if verified(file_path, name):
            return file_path
        else:
            print('Mismatch in the content of model file detected. Downloading again.')
    else:
        print('Model file is not found. Downloading.')

    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    download(_url_format.format(bucket=bucket,
                                file_name=file_name),
             fname=file_name+'.zip',
             dirname=local_dir,
             overwrite=True)
    zip_file_path = os.path.join(local_dir, file_name+'.zip')
    with zipfile.ZipFile(zip_file_path) as zf:
        zf.extractall(local_dir)
    os.remove(zip_file_path)

    if verified(file_path, name):
        return file_path
    else:
        raise ValueError('Downloaded file has different hash. Please try again.')

def purge(local_dir=os.path.expanduser('~/.mxnet/models/')):
    r"""Purge all pretrained model files in local file store.

    Parameters
    ----------
    local_dir : str, default '~/.mxnet/models'
        Location for keeping the model parameters.
    """
    files = os.listdir(local_dir)
    for f in files:
        if f.endswith(".params"):
            os.remove(os.path.join(local_dir, f))
