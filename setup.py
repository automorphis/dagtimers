from setuptools import setup

setup(
    name = 'dagtools',
    version = "0.1",
    description = "Nicely displayed timers.",
    long_description = "Nicely displayed timers.",
    long_description_content_type="text/plain",
    author = "Michael P. Lane",
    author_email = "mlanetheta@gmail.com",
    url = "https://github.com/automorphis/dagtimers",
    package_dir = {"": "lib"},
    packages = [
        "dagtimers",
        "cornifer._utilities"
    ],
    zip_safe=False
)