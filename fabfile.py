# -*- coding: utf-8 -*-


from fabric.api import local


def deploy():
    local('epio upload')
