#!/usr/bin/env python
#   -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'MovingAverage_Advisor',
        version = '0.1.0',
        description = '',
        long_description = 'MovingAverage_Advisor',
        long_description_content_type = None,
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        keywords = '',

        author = 'Phodzo Muladi',
        author_email = 'muladi.lione@gmail.com',
        maintainer = '',
        maintainer_email = '',

        license = '',

        url = '',
        project_urls = {},

        scripts = [],
        packages = [
            '.',
            'advisor',
            'advisor.MovingAverage',
            'advisor.Trade'
        ],
        namespace_packages = [],
        py_modules = [],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '',
        obsoletes = [],
    )
