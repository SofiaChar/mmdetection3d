import mmengine
import json
from valohai_yaml.objs import Step, Config, Parameter
from valohai_yaml.objs.parameter import MultipleMode
import pyaml

cfg = mmengine.config.Config.fromfile('./configs/mvxnet/mvxnet_fpn_dv_second_secfpn_8xb2-80e_kitti-3d-3class.py')
cfg.dump('resnet50_dump.json')

with open('resnet50_dump.json', 'r') as file:
    data = json.load(file)

def walk(val, path=()):
    if isinstance(val, dict):
        for key, value in val.items():
            if isinstance(value, dict):
                yield from walk(value, (*path, key))
            else:
                yield (*path, key), value


valohai_parameters = []

for key, default_value in walk(data):
    name = ".".join(key)
    param_type = type(default_value)

    parameter = Parameter(name=key[-1], pass_as=f"{name}=" + "{v}", category=key[0])
    parameter.default = default_value
    parameter.optional = True

    if param_type is type(None):
        param_optional = True
        param_type = "string"
    if isinstance(default_value, list):
        parameter.type = "string"
        param_value = str(default_value)
        parameter.default = str(default_value)
        parameter.multiple = MultipleMode.SEPARATE
        parameter.multiple_separator = ','
    if isinstance(default_value, str):
        parameter.type  = "string"
    if isinstance(default_value, bool):
        parameter.type  = "flag"
    if isinstance(default_value, int):
        parameter.type  = "integer"
        parameter.default = int(default_value)
    if isinstance(default_value, float):
        parameter.type  = "float"
        parameter.default = float(default_value)

    
    valohai_parameters.append(parameter)

step = Step(
    name="train",
    image='valohai/mmdetection3d',
    command=[
        "python3 tools/train.py --cfg-options {parameters}"
    ],
    parameters=valohai_parameters
)
config = Config(steps=[step])
with open('valohai.yaml', 'w') as file:
    pyaml.dump(config.serialize(), file)