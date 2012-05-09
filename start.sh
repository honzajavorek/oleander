#!/bin/bash

# Simple BASH script to begin work on project.
# - launches Flask development server
# - opens terminal at project directory with virtualenv activated


PROJECT_DIR=`dirname $0`
CSS_DIR="$PROJECT_DIR/oleander/static/css"


RCFILE=`tempfile`
echo ". ~/.bashrc" >> $RCFILE

VIRTUALENV_RCFILE=`tempfile`
cat $RCFILE >> $VIRTUALENV_RCFILE
echo ". $PROJECT_DIR/env/bin/activate" >> $VIRTUALENV_RCFILE

DEV_SERVER_RCFILE=`tempfile`
cat $VIRTUALENV_RCFILE >> $DEV_SERVER_RCFILE
echo "find $PROJECT_DIR -type f -name '*.pyc' | xargs rm
export OLEANDER_SETTINGS=$PROJECT_DIR/settings/lisa.py
until python $PROJECT_DIR/manage.py runserver; do
    echo 'Server crashed. Respawning...' >&2
    sleep 5
done
" >> $DEV_SERVER_RCFILE

SASS_RCFILE=`tempfile`
cat $RCFILE >> $SASS_RCFILE
echo "sass --style expanded --debug-info --watch $CSS_DIR" >> $SASS_RCFILE

SHELL_RCFILE=`tempfile`
cat $VIRTUALENV_RCFILE >> $SHELL_RCFILE
echo "export OLEANDER_SETTINGS=$PROJECT_DIR/settings/lisa.py
cd $PROJECT_DIR
" >> $SHELL_RCFILE


if which gnome-terminal &> /dev/null; then
    # GNOME Terminal
    exec gnome-terminal\
        --geometry="85x24+850+100"\
        --tab -e "bash --rcfile $DEV_SERVER_RCFILE" -t "Dev Server"\
        --tab -e "bash --rcfile $SASS_RCFILE" -t "Sass/Scss"\
        --tab -e "bash --rcfile $SHELL_RCFILE" -t "Shell"

else
    echo "Your terminal is not supported."
fi


rm $RCFILE $VIRTUALENV_RCFILE $DEV_SERVER_RCFILE $SASS_RCFILE $SHELL_RCFILE

