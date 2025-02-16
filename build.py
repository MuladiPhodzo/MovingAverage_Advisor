#   -*- coding: utf-8 -*-
from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "MovingAverage_Advisor"
version = "0.1.0"
default_task = "publish"


@init
def set_properties(project):
    project.build_depends_on("requests")  # Example dependency
    project.set_property("flake8_break_build", True)
    pass
