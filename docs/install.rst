Installation
============


Virtual Env
-----------

We recommend using Python virtual env. 

.. code-block:: bash

    sudo pip install virtualenv

    mkdir ~/.virtualenvs

    sudo pip install virtualenvwrapper

    export WORKON_HOME=~/.virtualenvs

Add to ~/.bashrc the following line

.. code-block:: bash

   . /usr/local/bin/virtualenvwrapper.sh

 
Installation
-------------

Clone the repository and run 

.. code-block:: bash

    cd color_match
    pip install -e ./
