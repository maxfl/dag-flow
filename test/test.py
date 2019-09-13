#!/usr/bin/env python

from dagflow import *

i = Input('input', None)
o = Output('output', None)

o >> i
