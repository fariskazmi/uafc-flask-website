UAFC Website - https://www.uafc.me/
=====

This was created by using Flask. You can locally host the server using the following commands:

Installing
----------

This is all done on a bash terminal (Linux/Mac). If you are on windows, you can install bash `here`_.

.. _here: https://www.windowscentral.com/install-windows-subsystem-linux-windows-10
Update package list:

.. code-block:: text

    sudo apt-get update

Install python:

.. code-block:: text

    sudo apt install python3
    
Install pip:

.. code-block:: text

    sudo apt install python3-pip

Install git:

.. code-block:: text

    sudo apt install git
    
Navigate to your working directory:

.. code-block:: text

    cd exampleDirectory/exampleSubDirectory
    
Clone this repository into your folder:

.. code-block:: text

    git clone https://github.com/fariskazmi/uafc-flask-website.git
    
Navigate into the downloaded folder:

.. code-block:: text

    cd uafc-flask-website
    
Create a virtual python environment:

.. code-block:: text

    python3 -m venv venv
    
Activate the virtual environment:

.. code-block:: text

    source venv/bin/activate
    
Install the required packages:

.. code-block:: text

    pip install -r requirements.txt
    
Run the server!:

.. code-block:: text

    python3 run.py
    
The local server should be running now. Visit http://localhost:5000/ in your web browser to see it. Any email-related functions on the website will not function on this repository and will cause an error. If you want to use them, you can enter your username and password in config.py





