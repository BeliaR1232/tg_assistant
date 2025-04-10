#!/usr/bin/env sh
dockerize -wait 'tcp://redis:6379'
arq src.scheduler.main.WorkerSettings 
