#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

for line in sys.stdin:
    for token in line.strip().split():
        if '▁' not in token:
            print(token)
