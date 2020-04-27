from io import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="{{ cookiecutter.project_name }}",
    version="0.1.0",
    description="Pyramid starter project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[
        "pyramid==1.10.4",
        "waitress==1.4.2",
        "pyramid_jinja2==2.8",
        "SQLAlchemy[postgresql]==1.3.10",
        "deform==2.0.8",
        "colander==1.7.0",
        "redis==3.3.11",
        "zope.sqlalchemy==1.2",
        "zope.interface==4.6.0",
        "Jinja2==2.10.3",
        "MarkupSafe==1.1.1",
        "pyramid_tm==2.3",
        "pyramid_retry==2.1",
        "passlib==1.7.1",
    ],
    extras_require={
        "dev": ["alembic==1.2.1", "pyramid_debugtoolbar==4.5"],
        "test": ["pytest==5.2.1", "pytest-cov==2.8.1"],
    },
    entry_points={"paste.app_factory": ["main={{ cookiecutter.repo_name }}:main"]},
)
